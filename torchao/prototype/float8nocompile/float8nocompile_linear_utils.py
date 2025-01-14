# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
import logging
from typing import Callable, Optional

import torch.nn as nn

from torchao.float8.config import Float8LinearConfig
from torchao.float8.float8_linear_utils import swap_linear_layers
from torchao.prototype.float8nocompile.float8nocompile_linear import (
    Float8LinearNoCompile,
)
from torchao.prototype.float8nocompile.kernels.fp8_dynamic_tensorwise import (
    KernelAlgorithm,
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def convert_to_float8_nocompile_training(
    module: nn.Module,
    *,
    config: Float8LinearConfig = None,
    module_filter_fn: Optional[Callable[[nn.Module, str], bool]] = None,
    kernel_algo: KernelAlgorithm = KernelAlgorithm.ATOMIC_MAX,
    no_precompute_for_backward: bool = False,
) -> nn.Module:
    """
    Swaps `torch.nn.Linear` in `module` with `Float8LinearNoCompile`.

    Args:
        module: Module to modify.
        module_filter_fn: If specified, only the `torch.nn.Linear` subclasses that
            that pass the filter function will be swapped. The inputs to the
            filter function are the module instance and the FQN.
        config (Float8LinearConfig): configuration for conversion to float8

    Returns:
     nn.Module: The modified module with swapped linear layers.
    """
    if config is None:
        config = Float8LinearConfig()

    from_float = lambda m: Float8LinearNoCompile.from_float(
        m,
        config=config,
        kernel_algo=kernel_algo,
        no_precompute_for_backward=no_precompute_for_backward,
    )
    return swap_linear_layers(
        module,
        from_float,
        module_filter_fn=module_filter_fn,
    )


def no_precompute_for_backward_every_nth_layer(model: nn.Module, n: int):
    """Set no_precompute_for_backward to True for every nth layer in the model."""
    for layer_idx, (layer_id, layer) in enumerate(model.layers.named_children()):
        if layer_idx % n == 0:
            log.info(f"Enabling no_precompute_for_backward for layer {layer_id}")
            _enable_no_precompute_for_backward(layer)


def _enable_no_precompute_for_backward(model: nn.Module):
    """Recursively set no_precompute_for_backward to True for all linear layers in the given model."""
    for child_layer in model.children():
        if isinstance(child_layer, nn.Linear):
            child_layer.no_precompute_for_backward = True
        else:
            _enable_no_precompute_for_backward(child_layer)
