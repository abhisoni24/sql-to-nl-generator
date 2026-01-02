
import json
import os

OUTPUT_FILE = '../../dataset/current/nl_social_media_queries_perturbed.json'
FAILED_ID_FILE = 'failed_sql_ids.txt'

def verify_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, OUTPUT_FILE)
    failed_id_path = os.path.join(base_dir, FAILED_ID_FILE)

    print(f"Verifying data in: {output_path}")

    try:
        with open(output_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Output file not found.")
        return
    except json.JSONDecodeError:
        print("Output file contains invalid JSON.")
        return

    # Valid IDs tracking
    valid_ids = set()
    malformed_ids = set()

    for item in data:
        query_id = item.get('id')
        
        # Validation checks
        if 'generated_perturbations' not in item:
            print(f"ID {query_id}: Missing 'generated_perturbations'")
            malformed_ids.add(query_id)
            continue
            
        perturbations = item['generated_perturbations']
        
        if not isinstance(perturbations, dict):
             print(f"ID {query_id}: 'generated_perturbations' is not a dict")
             malformed_ids.add(query_id)
             continue

        # Check single_perturbations
        single = perturbations.get('single_perturbations')
        if not isinstance(single, list):
            print(f"ID {query_id}: 'single_perturbations' is not a list")
            malformed_ids.add(query_id)
            continue
            
        if len(single) != 10:
            print(f"ID {query_id}: Expected 10 single perturbations, found {len(single)}")
            malformed_ids.add(query_id)
            continue

        # Check compound_perturbation
        compound = perturbations.get('compound_perturbation')
        if not isinstance(compound, dict):
            print(f"ID {query_id}: 'compound_perturbation' is not a dict")
            malformed_ids.add(query_id)
            continue
            
        if 'perturbed_nl_prompt' not in compound:
             print(f"ID {query_id}: 'compound_perturbation' missing 'perturbed_nl_prompt'")
             malformed_ids.add(query_id)
             continue

        valid_ids.add(query_id)

    # Calculate missing IDs (Assuming known range 1-2100)
    # Ideally should read input file to know total, but for this specific task we know it is 2100.
    # Or better, read input file just to be safe if that changed.
    input_path = os.path.join(base_dir, '../../dataset/current/nl_social_media_queries.json')
    try:
        with open(input_path, 'r') as f:
            input_data = json.load(f)
            all_ids = {x['id'] for x in input_data}
    except Exception as e:
        print(f"Could not read input file to determine all IDs: {e}")
        all_ids = set(range(1, 2101)) # Fallback

    missing_ids = all_ids - valid_ids
    if missing_ids:
        print(f"Found {len(missing_ids)} missing IDs.")
    
    if malformed_ids:
        print(f"Found {len(malformed_ids)} malformed records.")

    # Combine
    total_failed = missing_ids.union(malformed_ids)
    sorted_failed_ids = sorted(list(total_failed))
    
    with open(failed_id_path, 'w') as f:
        if sorted_failed_ids:
            f.write('\n'.join(map(str, sorted_failed_ids)))
        else:
            f.write('') # Clear file if all good
        
    print(f"Updated failed IDs file. Total failed/missing count: {len(sorted_failed_ids)}")

if __name__ == "__main__":
    verify_data()
