#!/usr/bin/env python3
"""
Create a mini dataset with one query per complexity type for testing.
"""
import json
import sys
from collections import defaultdict

def create_mini_dataset(input_file, output_file):
    """Extract one query per complexity type."""
    print(f"Loading dataset from {input_file}...")
    
    with open(input_file, 'r') as f:
        full_dataset = json.load(f)
    
    print(f"Total queries in full dataset: {len(full_dataset)}")
    
    # Group by complexity
    by_complexity = defaultdict(list)
    for query in full_dataset:
        complexity = query.get('complexity', 'unknown')
        by_complexity[complexity].append(query)
    
    print(f"\nComplexity distribution:")
    for comp, queries in sorted(by_complexity.items()):
        print(f"  {comp:15s}: {len(queries)} queries")
    
    # Extract first query from each complexity
    mini_dataset = []
    for complexity in sorted(by_complexity.keys()):
        if by_complexity[complexity]:
            mini_dataset.append(by_complexity[complexity][0])
            print(f"\n✓ Extracted {complexity} query (ID: {by_complexity[complexity][0]['id']})")
    
    # Save mini dataset
    with open(output_file, 'w') as f:
        json.dump(mini_dataset, f, indent=2)
    
    print(f"\n✓ Mini dataset saved to {output_file}")
    print(f"  Total queries: {len(mini_dataset)}")
    
    # Calculate expected test cases
    total_test_cases = 0
    for query in mini_dataset:
        if 'generated_perturbations' in query:
            # Count original + applicable perturbations
            count = 1  # original
            for pert in query['generated_perturbations'].get('single_perturbations', []):
                if pert.get('applicable', False):
                    count += 1
            total_test_cases += count
            print(f"  - {query['complexity']:15s}: {count} test cases (1 original + {count-1} perturbations)")
    
    print(f"\n  Expected total test cases: {total_test_cases}")
    
    return output_file

if __name__ == "__main__":
    input_file = "dataset/current/nl_social_media_queries.json"
    output_file = "dataset/current/mini_test_dataset.json"
    
    create_mini_dataset(input_file, output_file)
