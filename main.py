import json
import random
from generator import SQLQueryGenerator
from schema import SCHEMA, FOREIGN_KEYS

from sqlglot import exp

def main():
    generator = SQLQueryGenerator(SCHEMA, FOREIGN_KEYS)
    output_data = []
    
    print("Generating 1000 queries...")
    
    for i in range(1000):
        try:
            query_ast, complexity = generator.generate_query()
            sql_string = query_ast.sql(dialect='mysql')
            
            # Basic metadata
            entry = {
                "id": i + 1,
                "complexity": complexity,
                "sql": sql_string,
                "tables": [t.name for t in query_ast.find_all(exp.Table)]
            }
            output_data.append(entry)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error generating query {i+1}: {e}")
            continue
            
    print(f"Successfully generated {len(output_data)} queries.")
    
    with open('social_media_queries.json', 'w') as f:
        json.dump(output_data, f, indent=2)
        
    print("Saved to social_media_queries.json")

if __name__ == "__main__":
    main()
