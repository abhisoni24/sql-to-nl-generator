import sys
import os
import json
import random

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.core.generator import SQLQueryGenerator
from src.core.schema import SCHEMA, FOREIGN_KEYS

def generate_benchmark_sql(output_path, num_queries=50):
    """
    Generate a diverse set of SQL queries to serve as the benchmark foundation.
    """
    print(f"Generating {num_queries} base SQL queries...")
    generator = SQLQueryGenerator(SCHEMA, FOREIGN_KEYS)
    
    # We want a mix of complexities
    # Using generator.generate_dataset logic but simpler
    dataset = generator.generate_dataset(num_per_complexity=int(num_queries/7) + 1)
    
    # Trim to exact number
    dataset = dataset[:num_queries]
    
    print(f"Saving {len(dataset)} base queries to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(dataset, f, indent=2)

if __name__ == "__main__":
    output = "benchmark_base_sqls.json"
    if len(sys.argv) > 1:
        output = sys.argv[1]
    
    generate_benchmark_sql(output)
