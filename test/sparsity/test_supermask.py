import copy
import logging
import unittest
import math

import torch
from torch import nn
from torch.testing._internal import common_utils

from torchao.dtypes import MarlinSparseLayout, SemiSparseLayout
from torchao.quantization.quant_api import (
    int4_weight_only,
    int8_dynamic_activation_int8_weight,
    quantize_,
)
from torchao.sparsity import apply_fake_sparsity, semi_sparse_weight, sparsify_
from torchao.sparsity.utils import create_block_sparse_tensor
from torchao.utils import (
    TORCH_VERSION_AT_LEAST_2_3,
    TORCH_VERSION_AT_LEAST_2_4,
    TORCH_VERSION_AT_LEAST_2_5,
    TORCH_VERSION_AT_LEAST_2_6,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

class TestSupermask(common_utils.TestCase):

    @common_utils.parametrize("sparsity_level", [0.25, 0.5])
    @common_utils.parametrize("blocksize", [2, 4, 8])
    def test_supermask(self, sparsity_level, blocksize):
        input = torch.randn((1, 16)).half().cuda()
        model = (
            nn.Sequential(
                nn.Linear(16, 16, bias=False),
            )
            .half()
            .cuda()
            .eval()
        )

        from torchao.sparsity import SupermaskLinear

        M, N = model[0].weight.shape
        sparsify_(model, lambda x: SupermaskLinear.from_linear(x, sparsity_level=sparsity_level, blocksize=blocksize))
        sparsify_(model, SupermaskLinear.to_linear)
        weight_bsr = model[0].weight.to_sparse_bsr(blocksize=blocksize)

        # Test correct sparsity level
        nnz = weight_bsr._nnz() 
        expected = round((M // blocksize) * (N // blocksize) * (1 - sparsity_level))
        assert nnz == expected, f"Expected {expected} nonzeros, got {nnz}"

    def test_from_linear(self):
        from torchao.sparsity import SupermaskLinear
        linear = nn.Linear(128, 128)
        supermask_linear = SupermaskLinear.from_linear(linear, sparsity_level=0.5, blocksize=4)
        assert supermask_linear.weight.shape == linear.weight.shape


common_utils.instantiate_parametrized_tests(TestSupermask)

if __name__ == "__main__":
    unittest.main()
