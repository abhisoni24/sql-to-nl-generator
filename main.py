import sys
import os
import json
import uuid
import sqlglot
from sqlglot import exp

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.core.generator import SQLQueryGenerator
from src.core.schema import SCHEMA, FOREIGN_KEYS
from src.core.nl_renderer import SQLToNLRenderer, PerturbationConfig, PerturbationType

def get_change_description(p_type: PerturbationType) -> str:
    """Helper to return description of changes for metadata."""
    descriptions = {
        PerturbationType.UNDER_SPECIFICATION: "Omitted explicit table or column names.",
        PerturbationType.IMPLICIT_BUSINESS_LOGIC: "Replaced specific filter conditions with specific business logic terms.",
        PerturbationType.SYNONYM_SUBSTITUTION: "Replaced schema terms with synonyms.",
        PerturbationType.INCOMPLETE_JOINS: "Removed explicit keys and used natural language for joins.",
        PerturbationType.RELATIVE_TEMPORAL: "Replaced absolute dates with relative terms.",
        PerturbationType.AMBIGUOUS_PRONOUNS: "Replaced schema references with ambiguous pronouns.",
        PerturbationType.VAGUE_AGGREGATION: "Replaced approximate aggregation functions with vague terms.",
        PerturbationType.COLUMN_VARIATIONS: "Modified column naming conventions.",
        PerturbationType.MISSING_WHERE_DETAILS: "Used subjective terms in WHERE clauses.",
        PerturbationType.TYPOS: "injected naturalistic typos."
    }
    return descriptions.get(p_type, "Applied perturbation.")

def generate_benchmark_dataset(output_path: str, num_per_complexity: int = 300):
    print(f"Initializing SQL Generator...")
    generator = SQLQueryGenerator(SCHEMA, FOREIGN_KEYS)
    
    print(f"Generating queries ({num_per_complexity} per complexity type)...")
    base_dataset = generator.generate_dataset(num_per_complexity=num_per_complexity)
    
    final_output = []
    
    print(f"Processing {len(base_dataset)} base queries for variations...")
    pert_types = list(PerturbationType)
    
    # Vanilla renderer for base prompt
    base_renderer = SQLToNLRenderer(PerturbationConfig(active_perturbations=set(), seed=42))

    for i, item in enumerate(base_dataset):
        if (i+1) % 100 == 0:
            print(f"Processing query {i+1}/{len(base_dataset)}...")
            
        sql_str = item['sql']
        # Ensure ID is unique and integer-like if possible, or keep original
        base_id = item['id'] 
        complexity = item['complexity']
        tables = item['tables']
        
        try:
            ast = sqlglot.parse_one(sql_str)
        except Exception as e:
            print(f"Error parsing SQL for ID {base_id}: {e}")
            continue
            
        # 1. Vanilla Prompt
        vanilla_nl = item.get('prompt_text')
        if not vanilla_nl:
            try:
                vanilla_nl = base_renderer.render(ast)
            except Exception:
                vanilla_nl = "Error rendering prompt."

        # 2. (Skipped) Random Variations - removed per user request

        # 3. Single Perturbations (SDT)
        single_perturbations_list = []
        app_count = 0
        
        for p_id, p_type in enumerate(pert_types, 1):
            # Check applicability
            temp_renderer = SQLToNLRenderer(PerturbationConfig(active_perturbations={p_type}, seed=42))
            is_app = temp_renderer.is_applicable(ast, p_type)
            
            p_record = {
                "perturbation_id": p_id,
                "perturbation_name": p_type.value,
                "applicable": is_app,
                "perturbed_nl_prompt": None,
                "changes_made": None,
                "reason_not_applicable": None if is_app else "Logic check failed."
            }
            
            if is_app:
                app_count += 1
                try:
                    p_nl = temp_renderer.render(ast)
                    p_record["perturbed_nl_prompt"] = p_nl
                    p_record["changes_made"] = get_change_description(p_type)
                except Exception as e:
                    p_record["perturbed_nl_prompt"] = None
                    p_record["changes_made"] = f"Error: {e}"
            
            single_perturbations_list.append(p_record)

        # Construct final object
        entry = {
            "id": base_id,
            "complexity": complexity,
            "sql": sql_str,
            "tables": tables,
            "generated_perturbations": {
                "original": {
                    "nl_prompt": vanilla_nl,
                    "sql": sql_str,
                    "tables": tables,
                    "complexity": complexity
                },
                "single_perturbations": single_perturbations_list,
                "metadata": {
                    "total_applicable_perturbations": app_count,
                    "total_not_applicable": len(pert_types) - app_count,
                    "applicability_rate": round(app_count / len(pert_types), 2)
                }
            }
        }
        
        final_output.append(entry)

    # Ensure output dir exists
    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    print(f"Saving {len(final_output)} items to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(final_output, f, indent=2)
            
    print("Done.")

if __name__ == "__main__":
    output_file = "dataset/current/nl_social_media_queries.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    generate_benchmark_dataset(output_file)
