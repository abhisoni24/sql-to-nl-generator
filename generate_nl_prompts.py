"""
Pipeline to generate natural language prompts from SQL queries.
Loads social_media_queries.json, parses each SQL, renders to NL, and updates JSON.
"""

import json
from sqlglot import parse_one
from nl_renderer import SQLToNLRenderer


def generate_nl_prompts(input_file='social_media_queries.json', output_file='social_media_queries.json'):
    """Generate NL prompts for all SQL queries in the dataset."""
    
    # Load existing queries
    print(f"Loading {input_file}...")
    with open(input_file, 'r') as f:
        queries = json.load(f)
    
    print(f"Loaded {len(queries)} queries.")
    
    # Initialize renderer
    renderer = SQLToNLRenderer()
    
    # Process each query
    print("Generating natural language prompts...")
    success_count = 0
    error_count = 0
    
    for i, query_data in enumerate(queries):
        sql = query_data['sql']
        
        try:
            # Parse SQL
            ast = parse_one(sql, dialect='mysql')
            
            # Render to NL
            nl_prompt = renderer.render(ast)
            
            # Add to data
            query_data['nl_prompt'] = nl_prompt
            success_count += 1
            
        except Exception as e:
            print(f"Error processing query {i}: {sql[:50]}... - {e}")
            query_data['nl_prompt'] = f"[Error: Could not generate NL prompt]"
            error_count += 1
    
    print(f"Successfully generated {success_count} prompts, {error_count} errors.")
    
    # Save updated JSON
    print(f"Saving to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(queries, f, indent=2)
    
    print("Done!")
    
    # Print a few examples
    print("\n" + "="*80)
    print("Sample NL Prompts:")
    print("="*80)
    for i in range(min(5, len(queries))):
        print(f"\nQuery {i+1}:")
        print(f"SQL: {queries[i]['sql']}")
        print(f"NL:  {queries[i]['nl_prompt']}")
    print("="*80)


if __name__ == "__main__":
    generate_nl_prompts()
