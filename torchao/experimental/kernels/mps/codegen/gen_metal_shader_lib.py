# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import os
import sys

import yaml

if len(sys.argv) != 2:
    print("Usage: gen_metal_shader_lib.py <output_file>")
    sys.exit(1)

# Output file where the generated code will be written
OUTPUT_FILE = sys.argv[1]

MPS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Path to yaml file containing the list of .metal files to include
METAL_YAML = os.path.join(MPS_DIR, "metal.yaml")

metal_files = set()
with open(METAL_YAML, "r") as yamlf:
    metal_config = yaml.safe_load(yamlf)
    for op in metal_config:
        if "file" in op:
            metal_files.add(op["file"])
metal_files = sorted(metal_files)

# Path to the folder containing the .metal files
METAL_DIR = os.path.join(MPS_DIR, "metal")

prefix = """/**
 * This file is generated by gen_metal_shader_lib.py
 */

#ifdef USE_ATEN
using at::native::mps::MetalShaderLibrary;
#else
#include <torchao/experimental/kernels/mps/src/MetalShaderLibrary.h>
#endif

static MetalShaderLibrary metal_lowbit_quantized_lib(R"METAL_LOWBIT(
"""

suffix = """
)METAL_LOWBIT");
"""

comment = """
/**
 * Contents of {}
 */

"""

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, "w") as outf:
    outf.write(prefix)
    for file in metal_files:
        with open(os.path.join(METAL_DIR, file), "r") as f:
            content = f.read()
            outf.write(comment.format(file))
            outf.write(content)
            outf.write("\n\n")
    outf.write(suffix)
