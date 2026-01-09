#!/usr/bin/env python3
"""Generate GitHub Actions summary from evaluation results.

Usage:
    python scripts/generate_summary.py results/eval_abc123.json
"""

import json
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_summary.py <result_file>", file=sys.stderr)
        sys.exit(1)
    
    result_file = sys.argv[1]
    
    try:
        with open(result_file) as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading {result_file}: {e}", file=sys.stderr)
        sys.exit(1)
    
    metrics = data.get("metrics", {})
    prompt_hash = data.get("prompt_hash", "unknown")
    
    # Output metrics table rows
    print(f"| Action Accuracy | {metrics.get('action_accuracy', 0):.1f}% |")
    print(f"| Liquid Valid | {metrics.get('liquid_valid', 0):.1f}% |")
    print(f"| Renders to JSON | {metrics.get('renders_to_json', 0):.1f}% |")
    print(f"| Avg Latency | {metrics.get('avg_latency_ms', 0):.0f}ms |")
    print(f"| Error Rate | {metrics.get('error_rate', 0):.1f}% |")
    print()
    print(f"Prompt Hash: `{prompt_hash}`")


if __name__ == "__main__":
    main()
