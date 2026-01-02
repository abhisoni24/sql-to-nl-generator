
import os
import json
import time
import argparse
from tqdm import tqdm
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Import from local cache.py
try:
    from cache import perturbation_types, schema, foreign_keys, instructions
except ImportError:
    # If running from a different directory, adjust path or assume it works if in same dir
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from cache import perturbation_types, schema, foreign_keys, instructions

# Constants
INPUT_FILE = '../../dataset/current/nl_social_media_queries.json'
OUTPUT_FILE = '../../dataset/current/nl_social_media_queries_perturbed.json'
MODEL_NAME = "gemini-2.5-flash-lite"
CACHE_TTL = "12600s"

def setup_client():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    return genai.Client(api_key=api_key)

def create_cache(client, model_name):
    cached_text = f'''
        # Schema definition for SocialMediaDB
        {schema}
        # Define valid join paths (left_table, right_table): (left_key, right_key)
        {foreign_keys}
        perturbation_types: 
        {perturbation_types} 
        Here are your instructions:
        {instructions}
    '''
    
    try:
        cache = client.caches.create(
            model=model_name,
            config=types.CreateCachedContentConfig(
                display_name='task_info_v1', 
                system_instruction=(
                    '''You are an expert at generating realistic perturbations of natural language
                    database query prompts. Your task is to apply specific perturbation types to 
                    simulate how real developers write prompts when interacting with AI coding 
                    assistants. The perturbation details are provided in the task_info_v1 cache.'''
                ),
                contents=[cached_text],
                ttl=CACHE_TTL,
            )
        )
        return cache
    except Exception as e:
        print(f"Error creating cache: {e}")
        return None

def generate_mock_response(nl_prompt):
    """Generates a mock response for testing."""
    import random
    time.sleep(0.1) # Simulate loose latency
    return json.dumps({
        "original": {"nl_prompt": nl_prompt},
        "single_perturbations": [
            {
                "perturbation_id": 1, 
                "perturbation_name": "under_specification", 
                "applicable": True, 
                "perturbed_nl_prompt": f"MOCK PERTURBATION: {nl_prompt}", 
                "changes_made": "Mock change"
            }
        ],
        "compound_perturbation": {
             "perturbations_applied": [{"perturbation_id": 1, "perturbation_name": "mock"}],
             "perturbed_nl_prompt": f"MOCK COMPOUND: {nl_prompt}",
             "changes_made": "Mock compound change"
        }
    })

def process_queries(mock=False):
    # Determine paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, INPUT_FILE)
    output_path = os.path.join(base_dir, OUTPUT_FILE)

    print(f"Reading from: {input_path}")
    print(f"Writing to: {output_path}")

    # Load input
    with open(input_path, 'r') as f:
        queries = json.load(f)

    # Load existing output for resume
    processed_data = []
    processed_ids = set()
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r') as f:
                processed_data = json.load(f)
                processed_ids = {item['id'] for item in processed_data}
            print(f"Found existing output with {len(processed_data)} processed queries. Resuming...")
        except json.JSONDecodeError:
            print("Output file exists but is invalid/empty. Starting fresh.")
    
    # Identify queries to process
    queries_to_process = [q for q in queries if q['id'] not in processed_ids]
    print(f"Total queries: {len(queries)}")
    print(f"Already processed: {len(processed_ids)}")
    print(f"Remaining: {len(queries_to_process)}")

    if not queries_to_process:
        print("All queries processed!")
        return

    # Setup Client and Cache
    client = None
    cache = None
    if not mock:
        client = setup_client()
        print("Setting up cache...")
        cache = create_cache(client, MODEL_NAME)
        print(f"Cache created: {cache.name}")

    # Processing Loop
    success_count = 0
    fail_count = 0
    
    # We append to the processed_data list and save periodically
    pbar = tqdm(queries_to_process, desc="Processing Queries", unit="query")
    
    for query in pbar:
        try:
            nl_prompt = query['nl_prompt']
            
            if mock:
                response_text = generate_mock_response(nl_prompt)
            else:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=f'''
                        # Task
                        Generate 10 single-perturbation versions and 1 compound-perturbation version
                        (with up to 5 perturbations) of the given natural language prompt.
                        # Input Data: {nl_prompt}''',
                    config=types.GenerateContentConfig(cached_content=cache.name)
                )
                response_text = response.text

            # Parse JSON
            # Sometimes Gemini returns markdown blocks like ```json ... ```
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            perturbation_data = json.loads(cleaned_text)
            
            # Combine original query data with perturbation data
            # We want to keep original structure and APPEND the perturbations
            # The prompt requested: "Append the returned json output from the client from each call at the end of the respective query"
            # So we will add a new key 'generated_perturbations' to the query object
            
            enriched_query = query.copy()
            enriched_query['generated_perturbations'] = perturbation_data
            
            processed_data.append(enriched_query)
            success_count += 1
            
        except Exception as e:
            fail_count += 1
            tqdm.write(f"Failed query ID {query['id']}: {e}")
            # Optional: Add a failed record so we don't indefinitely retry without fixing? 
            # For now, we skip saving it so it WILL be retried next run.
        
        pbar.set_postfix({"Success": success_count, "Fail": fail_count})

        # Save periodically (every 10 or so, and definitely at end)
        if success_count % 10 == 0:
             with open(output_path, 'w') as f:
                json.dump(processed_data, f, indent=2)

    # Final Save
    with open(output_path, 'w') as f:
        json.dump(processed_data, f, indent=2)
    
    print(f"\nCompleted. Success: {success_count}, Fail: {fail_count}")
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate perturbations for SQL queries using Gemini.")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode without API calls.")
    args = parser.parse_args()

    process_queries(mock=args.mock)
