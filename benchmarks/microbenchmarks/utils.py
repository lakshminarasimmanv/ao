import time
from typing import List

import torch
from torch.profiler import profile, record_function, ProfilerActivity

from torchao.quantization import (
    MappingType,
    PerRow,
    PerTensor,
    float8_dynamic_activation_float8_weight,
    float8_weight_only,
    fpx_weight_only,
    int4_weight_only,
    int8_dynamic_activation_int4_weight,
    int8_dynamic_activation_int8_weight,
    int8_weight_only,
    quantize_,
    uintx_weight_only,
)
from torchao.utils import TORCH_VERSION_AT_LEAST_2_5, unwrap_tensor_subclass


# TODO: add more models
class ToyLinearModel(torch.nn.Module):
    def __init__(self, k=64, n=32, dtype=torch.bfloat16):
        super().__init__()
        self.linear1 = torch.nn.Linear(k, n, bias=False).to(dtype)

    def forward(self, x):
        x = self.linear1(x)
        return x


class LNLinearSigmoid(torch.nn.Module):
    def __init__(self, fc_dim1, fc_dim2, dtype=torch.bfloat16):
        super().__init__()
        self.ln = torch.nn.LayerNorm(fc_dim1, elementwise_affine=False)
        self.fc = torch.nn.Linear(fc_dim1, fc_dim2, bias=False).to(dtype)
        self.sigmoid = torch.nn.Sigmoid()

    def forward(self, x):
        x = self.ln(x)
        x = self.fc(x)
        x = self.sigmoid(x)
        return x


def get_default_device() -> str:
    return (
        "cuda"
        if torch.cuda.is_available()
        else "xpu"
        if torch.xpu.is_available()
        else "cpu"
    )


def benchmark_func_call(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken to run {func.__name__}: {elapsed_time:.2f} seconds")
    return result


def ffn_only(mod, fqn):
    return isinstance(mod, torch.nn.Linear) and "feed_forward" in fqn


def not_ffn_only(mod, fqn):
    return isinstance(mod, torch.nn.Linear) and not ffn_only(mod, fqn)


def ffn_or_attn_only(mod, fqn):
    return isinstance(mod, torch.nn.Linear) and (
        "feed_forward" in fqn or "attention" in fqn
    )


def quantize_model(
    model: torch.nn.Module,
    quantization: str,
    **kwargs,
):
    """Quantize a model inplace or return a new quantized model.

    Args:
        model (torch.nn.Module): model to be quantized
        quantization (str): quantization method to be used
        kwargs: additional arguments to be passed to the quantization method
    """
    # Define kwargs
    sparsity = kwargs.get("sparsity", None)
    precision = kwargs.get("precision", None)

    # Quantization techniques
    if "int8wo" in quantization:
        quantize_(model, int8_weight_only())
    if "int8dq" in quantization:
        if sparsity and "semi" in sparsity:
            from torchao.dtypes import SemiSparseLayout

            quantize_(
                model,
                int8_dynamic_activation_int8_weight(layout=SemiSparseLayout()),
                filter_fn=ffn_only,
            )
            quantize_(
                model, int8_dynamic_activation_int8_weight(), filter_fn=not_ffn_only
            )
        elif "int8dq_prefill_wo_decode" in quantization:
            quantize_(
                model, int8_dynamic_activation_int8_weight(weight_only_decode=True)
            )
        else:
            quantize_(model, int8_dynamic_activation_int8_weight())
    if "int4wo" in quantization:
        use_hqq = False
        if "hqq" in quantization:
            use_hqq = True
        group_size = int(quantization.split("-")[1])
        assert group_size in [
            32,
            64,
            128,
            256,
        ], f"int4wo group_size needs to be one of [32,64,128,256] but got {group_size}"
        quantize_(model, int4_weight_only(group_size=group_size, use_hqq=use_hqq))
    elif "int8adq-int4w-symm" in quantization:
        from torchao.dtypes import CutlassInt4PackedLayout

        quantize_(
            model,
            int8_dynamic_activation_int4_weight(
                group_size=None,
                mapping_type=MappingType.SYMMETRIC,
                act_mapping_type=MappingType.SYMMETRIC,
                layout=CutlassInt4PackedLayout(),
            ),
        )
    if "marlin" in quantization:
        if "qqq" in quantization:
            from torchao.dtypes import MarlinQQQLayout

            quantize_(
                model,
                int8_dynamic_activation_int4_weight(
                    group_size=128,
                    mapping_type=MappingType.SYMMETRIC,
                    act_mapping_type=MappingType.SYMMETRIC,
                    layout=MarlinQQQLayout(),
                ),
            )
        elif "semi" in sparsity:
            from torchao.dtypes import MarlinSparseLayout

            quantize_(
                model,
                int4_weight_only(layout=MarlinSparseLayout()),
                filter_fn=ffn_or_attn_only,
            )
    if "fp6" in quantization:
        quantize_(model, fpx_weight_only(3, 2))
    elif "embed-int8wo" in quantization:
        quantize_(
            model,
            int8_weight_only(group_size=64),
            filter_fn=lambda x, *args: isinstance(x, torch.nn.Embedding),
        )
    elif "uintx" in quantization:
        # uintx-nbits-group_size, e.g. "uintx-2-64"
        if "hqq" in quantization:
            # uintx-nbits-group_size-hqq
            use_hqq = True
        else:
            use_hqq = False
        _quant_args = quantization.split("-")
        nbits = int(_quant_args[1])
        assert nbits >= 1 and nbits <= 8, "nbits must be 1 to 8"
        _NBITS_TO_DTYPE = {
            1: torch.uint1,
            2: torch.uint2,
            3: torch.uint3,
            4: torch.uint4,
            5: torch.uint5,
            6: torch.uint6,
            7: torch.uint7,
            8: torch.uint8,
        }
        dtype = _NBITS_TO_DTYPE[nbits]
        group_size = int(_quant_args[2])
        quantize_(model, uintx_weight_only(dtype, group_size, use_hqq=use_hqq))
    elif "int8_dynamic_activation_intx_weight" in quantization:
        from torchao.experimental.quant_api import (
            int8_dynamic_activation_intx_weight,
        )
        from torchao.quantization.granularity import PerGroup

        assert (
            precision == torch.float32
        ), "int8_dynamic_activation_intx_weight requires using precision=torch.float32"

        # Quantize model
        _quant_args = quantization.split("-")
        weight_dtype = getattr(torch, f"int{_quant_args[1]}")
        granularity = PerGroup(int(_quant_args[2]))
        has_weight_zeros = bool(_quant_args[3])
        quantize_(
            model,
            int8_dynamic_activation_intx_weight(
                weight_dtype=weight_dtype,
                granularity=granularity,
                has_weight_zeros=has_weight_zeros,
            ),
        )
    elif "float8wo" in quantization:
        quantize_(model, float8_weight_only())
    elif "float8dq" in quantization:
        granularity = str(quantization.split("-")[-1])
        if granularity == "tensor":
            granularity = PerTensor()
        elif granularity == "row":
            granularity = PerRow()
        else:
            granularity = PerTensor()
        quantize_(
            model, float8_dynamic_activation_float8_weight(granularity=granularity)
        )
    else:
        if not TORCH_VERSION_AT_LEAST_2_5:
            unwrap_tensor_subclass(model)
    return model


# Function to benchmark model evaluation - e2e eval run
def benchmark_model_inference_in_microseconds(model, input_data):
    # Returns model run time in seconds
    # warm up
    for _ in range(2):
        model(input_data)
    num_iters = 5
    start_time = time.perf_counter()
    with torch.no_grad():
        for _ in range(num_iters):
            _ = model(input_data)
    end_time = time.perf_counter()

    return (end_time - start_time) / num_iters

def benchmark_model_inference_in_microseconds_with_profiler(model, input_data, kernels_to_benchmark: List[str]):
    # warm up
    for _ in range(2):
        model(input_data)
    with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA], record_shapes=True) as prof:
        # with record_function("model_inference"):
        for _ in range(1):  # Run the model multiple times to warm up the cache
            with torch.no_grad():
                _ = model(*input_data)
                torch.cuda.synchronize()

    # Return the profiler output
    return prof

def create_model_and_input(
    model_type: str,
    m: int,
    k: int,
    n: int,
    dtype: torch.dtype = torch.bfloat16,
    device: str = get_default_device(),
):
    """Create a model and input data for benchmarking.

    Args:
        model_type (str): type of the model to be created
        batch_size (int): batch size of the input data
        device (str): device to run the model on
        dtype (torch.dtype): data
        m, k, n (int): dimensions of the model and input data
    """
    if model_type == "linear":
        model = ToyLinearModel(k, n, dtype).to(device)
        input_data = torch.randn(m, k, device=device, dtype=dtype)
    elif model_type == "ln_linear_sigmoid":
        model = LNLinearSigmoid(k, n, dtype).to(device)
        input_data = torch.randn(m, k, device=device, dtype=dtype)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    return model, input_data

def get_gpu_kernel_times(profiler_chrome_trace, gpu_op_name):
    # Filter CUDA events
    event_data = [(event.key, event.device_time)
                  for event in profiler_chrome_trace.key_averages()
                  if event.device_type == torch.autograd.DeviceType.CUDA]

    # Calculate overhead time and op time
    gpu_op_time, gpu_overhead_time = 0, 0
    for event in event_data:
        if gpu_op_name in event[0]:
            gpu_op_time += event[1]
        else:
            gpu_overhead_time += event[1]
    return gpu_op_time, gpu_overhead_time
