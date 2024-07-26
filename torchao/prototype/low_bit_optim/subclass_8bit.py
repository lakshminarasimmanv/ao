import torch
from torch import Tensor
from torchao.dtypes.utils import _implements, _ATEN_OP_OR_TORCH_FN_TABLE

from .quant_utils import create_dynamic_map, scale_tensor, quantize_8bit_with_qmap, dequant_with_qmap


aten = torch.ops.aten
c10d_functional = torch.ops.c10d_functional
_c10d_functional = torch.ops._c10d_functional

QMAP_SIGNED = create_dynamic_map(signed=True)
QMAP_UNSIGNED = create_dynamic_map(signed=False)


class OptimState8bit(Tensor):
    implements = classmethod(_implements)
    tensor_attrs = ["codes", "scale", "qmap"]

    @staticmethod
    def __new__(cls, codes: Tensor, scale: Tensor, qmap: Tensor, signed: bool):
        return Tensor._make_wrapper_subclass(
            cls,
            codes.shape,
            device=codes.device,
            requires_grad=False,
        )

    def __init__(self, codes: Tensor, scale: Tensor, qmap: Tensor, signed: bool):
        """Create quantized 8-bit optimizer state as proposed in https://arxiv.org/abs/2110.02861

        Args
            codes: quantized 8-bit data stored as uint8. Has the same shape as the original float tensor.
            scale: scale data for block-wise quantization.
            qmap: lookup table that maps between quantized value (code) and float value.
            signed: whether the tensor is signed or unsigned.

        NOTE: To get block-wise scale, the original float tensor is first reshape to (-1, block_size).
        Thus, the last dimension of the original float tensor is not necessarily divisible by block size.
        Given `codes` and `scale`, `block_size` is calculated as `codes.numel() // scale.numel()`.
        """
        assert codes.dtype is torch.uint8
        assert scale.ndim == 1
        self.codes = codes
        self.scale = scale
        self.qmap = qmap
        self.signed = signed
        self.block_size = codes.numel() // scale.numel()

    def __tensor_flatten__(self):
        return self.tensor_attrs, [self.signed]

    @classmethod
    def __tensor_unflatten__(cls, tensor_data_dict, tensor_attributes, outer_size=None, outer_stride=None):
        return cls(*[tensor_data_dict[name] for name in cls.tensor_attrs], *tensor_attributes)

    def dequantize(self, output_dtype=None):
        dtype = output_dtype or torch.get_default_dtype()
        return dequant_with_qmap(self.codes, self.qmap, self.scale).to(dtype)

    @classmethod
    def zeros(cls, shape, signed: bool = True, block_size: int = 2048, device=None):
        codes = torch.zeros(shape, dtype=torch.uint8, device=device)
        scale = torch.zeros(codes.numel() // block_size, device=device)
        qmap = torch.tensor(QMAP_SIGNED if signed else QMAP_UNSIGNED, device=device)
        return cls(codes, scale, qmap, signed)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(signed={self.signed}, block_size={self.block_size}, "
            f"shape={tuple(self.shape)}, device={self.device}, requires_grad={self.requires_grad})"
        )

    @classmethod
    def __torch_dispatch__(cls, func, types, args, kwargs):
        if func in _ATEN_OP_OR_TORCH_FN_TABLE[cls]:
            return _ATEN_OP_OR_TORCH_FN_TABLE[cls][func](func, *args, **kwargs)

        raise NotImplementedError(f"{cls.__name__} dispatch: attempting to run {func}, this is not supported")


@OptimState8bit.implements(aten.copy_.default)
def _(func, *args, **kwargs):
    dst = args[0]
    src = args[1]

    if isinstance(dst, OptimState8bit) and isinstance(src, OptimState8bit):
        assert dst.signed == src.signed and dst.block_size == src.block_size
        dst.codes.copy_(src.codes)
        dst.scale.copy_(src.scale)
        # qmap should be the same, don't need to copy

    elif isinstance(dst, OptimState8bit):
        scaled_src, scale = scale_tensor(src, dst.block_size)
        codes = quantize_8bit_with_qmap(scaled_src, dst.qmap)
        dst.codes.copy_(codes)
        dst.scale.copy_(scale)

    else:
        dst.copy_(src.dequantize())

    return dst


@OptimState8bit.implements(aten.lerp.Scalar)
def _(func, *args, **kwargs):
    args = [x.dequantize() if isinstance(x, OptimState8bit) else x for x in args]
    return func(*args, **kwargs)


# this is needed for DTensor.from_local()
@OptimState8bit.implements(aten.view.default)
def _(func, *args, **kwargs):
    x, shape = args
    return OptimState8bit(x.codes.view(shape), x.scale, x.qmap, x.signed)


# this is needed for DTensor.full_tensor()
@OptimState8bit.implements([
    c10d_functional.all_gather_into_tensor.default,
    _c10d_functional.all_gather_into_tensor.default,
    c10d_functional.wait_tensor.default,
    _c10d_functional.wait_tensor.default,
])
def _(func, *args, **kwargs):
    x = args[0]
    if not isinstance(x, OptimState8bit):
        raise ValueError(f"expecting a OptimState8bit but found {type(x)}")

    # assume tensors from all ranks have the same signedness
    return OptimState8bit(
        func(x.codes, *args[1:], **kwargs),
        func(x.scale, *args[1:], **kwargs),
        x.qmap.clone(),
        x.signed,
    )
