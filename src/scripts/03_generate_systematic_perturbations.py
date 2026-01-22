"""
Script to generate systematic prompt perturbations using deterministic rules.
"""

import json
import sys
import os
from typing import Dict, Any, List

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlglot import parse_one
from src.core.nl_renderer import SQLToNLRenderer, PerturbationType, PerturbationConfig

# Constants
INPUT_FILE = './dataset/current/nl_social_media_queries.json'
OUTPUT_FILE = './dataset/current/nl_social_media_queries_systematic.json'

# Descriptions for changes made
PERTURBATION_DESCRIPTIONS = {
    PerturbationType.UNDER_SPECIFICATION: "Omitted explicit table or column names.",
    PerturbationType.IMPLICIT_BUSINESS_LOGIC: "Replaced specific filter conditions with specific business logic terms.",
    PerturbationType.SYNONYM_SUBSTITUTION: "Replaced schema terms with synonyms.",
    PerturbationType.INCOMPLETE_JOINS: "Replaced explicit SQL JOIN syntax with vague natural language connectors.",
    PerturbationType.RELATIVE_TEMPORAL: "Replaced absolute dates with relative terms.",
    PerturbationType.AMBIGUOUS_PRONOUNS: "Replaced schema references with ambiguous pronouns.",
    PerturbationType.VAGUE_AGGREGATION: "Replaced precise aggregate functions with vague terms.",
    PerturbationType.COLUMN_VARIATIONS: "Modified column naming conventions.",
    PerturbationType.MISSING_WHERE_DETAILS: "Used subjective terms in WHERE clauses.",
    PerturbationType.TYPOS: "Injected naturalistic typos."
}

def main():
    print(f"Loading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r') as f:
        queries = json.load(f)
    print(f"Loaded {len(queries)} queries.")

    output_data = []
    
    # Initialize basic renderer for checks
    base_renderer = SQLToNLRenderer()
    
    print("Generating systematic perturbations...")
    
    for i, query_item in enumerate(queries):
        sql = query_item['sql']
        nl_prompt_original = query_item.get('nl_prompt', '')
        
        # Structure for output item
        output_item = {
            "id": query_item.get('id', i+1),
            "complexity": query_item.get('complexity', 'unknown'),
            "sql": sql,
            "tables": query_item.get('tables', []),
            "generated_perturbations": {
                "original": {
                    "nl_prompt": nl_prompt_original,
                },
                "single_perturbations": [],
                "metadata": {}
            }
        }
        
        # Parse SQL once
        try:
            ast = parse_one(sql, dialect='mysql')
        except Exception as e:
            print(f"Error parsing SQL for query {i}: {e}")
            output_data.append(output_item)
            continue
            
        applicable_count = 0
        not_applicable_count = 0
        
        # Iterate through all perturbation types
        for p_id, p_type in enumerate(PerturbationType, 1):
            is_applicable = base_renderer.is_applicable(ast, p_type)
            
            perturbation_entry = {
                "perturbation_id": p_id,
                "perturbation_name": p_type.value,
                "applicable": is_applicable,
                "perturbed_nl_prompt": None,
                "changes_made": None,
                "reason_not_applicable": None
            }
            
            if is_applicable:
                # Generate perturbed prompt
                config = PerturbationConfig(active_perturbations={p_type}, seed=i*100 + p_id)
                renderer = SQLToNLRenderer(config)
                try:
                    perturbed_prompt = renderer.render(ast)
                    perturbation_entry["perturbed_nl_prompt"] = perturbed_prompt
                    perturbation_entry["changes_made"] = PERTURBATION_DESCRIPTIONS.get(p_type, "Applied perturbation.")
                    applicable_count += 1
                except Exception as e:
                    perturbation_entry["applicable"] = False
                    perturbation_entry["reason_not_applicable"] = f"Render error: {str(e)}"
                    not_applicable_count += 1
            else:
                perturbation_entry["reason_not_applicable"] = "Logic check failed."
                not_applicable_count += 1
                
            output_item["generated_perturbations"]["single_perturbations"].append(perturbation_entry)
            
        # Update metadata
        output_item["generated_perturbations"]["metadata"] = {
            "total_applicable_perturbations": applicable_count,
            "total_not_applicable": not_applicable_count,
            "applicability_rate": applicable_count / len(PerturbationType) if len(PerturbationType) > 0 else 0
        }
        
        output_data.append(output_item)
        
        if (i+1) % 100 == 0:
            print(f"Processed {i+1} queries...")
            
    print(f"Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f, indent=2)
        
    print("Done!")

if __name__ == "__main__":
    main()
