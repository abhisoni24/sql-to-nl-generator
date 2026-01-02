"""
Pipeline to generate natural language prompts with variations from SQL queries.
Loads social_media_queries.json, parses each SQL, renders vanilla + 3 variations, and updates JSON.
"""

import json
from sqlglot import parse_one
from src.core.nl_renderer import SQLToNLRenderer


def generate_nl_prompts(input_file='raw_social_media_queries.json', output_file='./dataset/current/nl_social_media_queries.json'):
    """Generate NL prompts with variations for all SQL queries in the dataset."""
    
    # Load existing queries
    print(f"Loading {input_file}...")
    with open(input_file, 'r') as f:
        queries = json.load(f)
    
    print(f"Loaded {len(queries)} queries.")
    
    # Initialize renderer
    renderer = SQLToNLRenderer()
    
    # Process each query
    print("Generating natural language prompts with variations...")
    success_count = 0
    error_count = 0
    
    for i, query_data in enumerate(queries):
        sql = query_data['sql']
        
        try:
            # Parse SQL
            ast = parse_one(sql, dialect='mysql')
            
            # Generate vanilla + 3 variations
            results = renderer.generate_variations(ast, num_variations=3)
            
            # Add to data
            query_data['nl_prompt'] = results['vanilla']
            query_data['nl_prompt_variations'] = results['variations']
            success_count += 1
            
        except Exception as e:
            print(f"Error processing query {i}: {sql[:50]}... - {e}")
            query_data['nl_prompt'] = "[Error: Could not generate NL prompt]"
            query_data['nl_prompt_variations'] = []
            error_count += 1
    
    print(f"Successfully generated {success_count} prompts with variations, {error_count} errors.")
    
    # Save updated JSON
    print(f"Saving to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(queries, f, indent=2)
    
    print("Done!")
    
    # Print a few examples
    print("\n" + "="*80)
    print("Sample NL Prompts with Variations:")
    print("="*80)
    for i in range(min(3, len(queries))):
        print(f"\nQuery {i+1}:")
        print(f"SQL: {queries[i]['sql']}")
        print(f"Vanilla: {queries[i]['nl_prompt']}")
        print("Variations:")
        for j, var in enumerate(queries[i]['nl_prompt_variations'], 1):
            print(f"  {j}. {var}")
    print("="*80)


if __name__ == "__main__":
    generate_nl_prompts()
