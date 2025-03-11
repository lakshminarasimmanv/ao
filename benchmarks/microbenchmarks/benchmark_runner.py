"""
Benchmark Runner

This is the main entry point for the benchmarking application. It reads the YAML configuration
file and orchestrates the entire benchmarking process by:
- Loading and validating benchmark configurations
- Executing benchmark scenarios
- Collecting and processing results
- Generating reports

Usage:
    python benchmark_runner.py [config.yaml]

The YAML file should contain all necessary configuration parameters for the benchmarks.
"""

from itertools import product
from typing import Any, Dict, List, Tuple

import yaml

from utils import (
    BenchmarkConfig,
    generate_results_csv,
    print_results,
)


def get_shapes_for_config(shape_config: Dict[str, Any]) -> List[Tuple[str, List[int]]]:
    """Get shapes for a given configuration"""
    name = shape_config["name"]
    if name == "custom":
        return [(name, shape) for shape in shape_config["shapes"]]
    else:
        raise NotImplementedError(
            f"Shape config {name} not supported. Currently only supports custom shapes."
        )


def load_benchmark_configs(config_path: str) -> List[BenchmarkConfig]:
    """Load benchmark configurations from YAML file"""
    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)

    quantization_config_recipe_names = config_data["quantization_config_recipe_names"]
    params = config_data["model_params"]
    output_dir = config_data.get("output_dir", "benchmarks/microbenchmarks/results")

    configs = []
    # Process each shape configuration
    for shape_config in params["matrix_shapes"]:
        shapes = get_shapes_for_config(shape_config)
        # Generate combinations for each shape
        for quant, (shape_name, shape) in product(
            quantization_config_recipe_names, shapes
        ):
            configs.append(
                BenchmarkConfig(
                    quantization=quant,
                    params=params,
                    shape_name=shape_name,
                    shape=shape,
                    output_dir=output_dir,
                )
            )
    return configs


def run_benchmarks_from_config(config_path: str) -> None:
    """Run benchmarks using configurations from YAML file"""
    from benchmark_inference import run as run_inference

    configs = load_benchmark_configs(config_path)
    results = []
    print("Benchmarking Inference ......")
    for config in configs:
        print(f"Running: {config.name}")
        result = run_inference(config)  # Pass the config object directly
        results.append(result)

    # Add results to csv
    generate_results_csv(results, configs[0].output_dir)

    # Print results
    print_results(results)

    # TODO: Process results: Speedups:
    # 1. For different shapes for same model and quantization
    # 2. For different quantizations for same model and shape
    # 3. For different models for same quantization


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run benchmarks from config file")
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to benchmark configuration file",
    )
    args = parser.parse_args()
    run_benchmarks_from_config(args.config)
