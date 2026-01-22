"""
Script to generating empirical examples of prompt variations using an LLM.
This is a data collection probe, not part of the production pipeline.
"""

import json
import random
import os
import time
import sys
from typing import Dict, List, Any

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# For Agent--- fix this import and rest of the script to use the adapter correctly and send api calls to gemini
from src.harness.adapters.base import get_llm_client
from src.core.schema import SCHEMA

import concurrent.futures
import threading

# Constants
# Constants
INPUT_FILE = './dataset/current/nl_social_media_queries.json'
OUTPUT_FILE = './dataset/current/perturbed_social_media_queries.json' # This constant is still used for the specific output file name
SAMPLE_SIZE = 5  # Reduced for verification
VARIANTS_PER_SAMPLE = 2  # Reduced for verification
LLM_PROVIDER = 'gemini' 
MODEL_NAME = 'gemini-2.5-flash-lite'

# Perturbation Dimensions
# These are the "knobs" we turn for each generation.
PERTURBATION_DIMENSIONS = {
    "semantic_completeness": ["fully specified", "mildly underspecified"],
    "lexical_precision": ["formal", "vague", "colloquial"],
    "framing": ["command", "question", "goal-oriented"],
    "structural_ordering": ["SQL-aligned", "inverted logic", "stream of consciousness"],
    "noise": ["none", "polite filler", "light contextual distraction"]
}

def construct_llm_prompt(sql: str, config: Dict[str, str]) -> str:
    """Constructs the meta-prompt for the LLM based on perturbation config."""
    # format schema details
    schema_str = "\n".join([f"- {table}: {', '.join(cols.keys())}" for table, cols in SCHEMA.items()])

    return f"""You are a helpful assistant generating natural language training data for a text-to-SQL system.

Task:
Generate ONE natural language request that corresponds to the SQL query below.
You must adhere strictly to the following stylistic constraints:

1. Semantic Completeness: {config['semantic_completeness']}
   (If "mildly underspecified", you may omit obvious details like "id" or "ASC/DESC" if implied contextually, but do NOT change the core logic.)
2. Lexical Precision: {config['lexical_precision']}
   (Use vocabulary matching this style.)
3. Framing: {config['framing']}
   (Phrase the request as a {config['framing']}.)
4. Structural Ordering: {config['structural_ordering']}
   (Do not just read the SQL left-to-right if "inverted" or "stream of consciousness".)
5. Noise Level: {config['noise']}
   (Add non-functional text accordingly.)

Database Schema:
{schema_str}

SQL Query:
{sql}

Output Requirements:
- Return ONLY the natural language prompt.
- Do not include explanations, quotes, or markdown code blocks.
- Do not invent tables or columns that aren't in the SQL.
"""

def generate_config() -> Dict[str, str]:
    """Randomly selects one value for each perturbation dimension."""
    return {
        key: random.choice(values)
        for key, values in PERTURBATION_DIMENSIONS.items()
    }

def main():
    print("Starting LLM-Assisted Prompt Generation Probe...")
    print("="*60)
    
    # 1. Load Data
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return
        
    with open(INPUT_FILE, 'r') as f:
        all_data = json.load(f)
    
    # 2. Sample Data
    samples = random.sample(all_data, min(SAMPLE_SIZE, len(all_data)))
    print(f"Loaded {len(all_data)} queries, sampled {len(samples)}.")
    
    # 3. Initialize LLM
    try:
        client = get_llm_client(LLM_PROVIDER, model_name=MODEL_NAME)
        print(f"Initialized {LLM_PROVIDER} client (model: {MODEL_NAME}).")
    except Exception as e:
        print(f"Failed to initialize LLM client: {e}")
        return

    output_data = []
    lock = threading.Lock()
    
    # 4. Loop and Generate (Parallel)
    print("Generating variations in parallel...")
    
    def process_sample(sample):
        local_results = []
        sql = sample['sql']
        sample_id = sample.get('id', 'unknown')
        
        # Canonical
        local_results.append({
            "sql_id": sample_id,
            "prompt_id": f"{sample_id}_canonical",
            "type": "canonical",
            "sql": sql,
            "prompt_text": sample.get('nl_prompt', ''),
            "perturbation_config": None
        })
        
        for i in range(VARIANTS_PER_SAMPLE):
            config = generate_config()
            prompt = construct_llm_prompt(sql, config)
            
            # Retry logic for rate limits
            max_retries = 5
            retry_delay = 5
            
            for attempt in range(max_retries):
                try:
                    # Add a small delay (jitter) to avoid thundering herd
                    time.sleep(random.uniform(0.1, 1.0))
                    
                    response = client.generate(prompt)
                    
                    if response['success']:
                        gen_text = response['sql'].strip()
                        with lock:
                            print(f"  [Sample {sample_id}] Generated Variant {i+1}")
                        
                        local_results.append({
                            "sql_id": sample_id,
                            "prompt_id": f"{sample_id}_var_{i+1}",
                            "type": "llm_generated",
                            "sql": sql,
                            "prompt_text": gen_text,
                            "perturbation_config": config,
                            "llm_model": client.model_name
                        })
                        break
                    elif "429" in str(response.get('error', '')):
                         print(f"  [Sample {sample_id}] Rate limit. Retrying in {retry_delay}s...")
                         time.sleep(retry_delay)
                         retry_delay *= 2
                    else:
                        print(f"  [Sample {sample_id}] Failed: {response['error']}")
                        break

                except Exception as e:
                    print(f"  [Sample {sample_id}] Exception: {e}")
                    break
        return local_results

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_sample = {executor.submit(process_sample, sample): sample for sample in samples}
        for future in concurrent.futures.as_completed(future_to_sample):
             try:
                 results = future.result()
                 output_data.extend(results)
             except Exception as exc:
                 print(f"Sample generated an exception: {exc}")

    # 5. Save Results

    # 5. Save Results
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f, indent=2)
        
    print("="*60)
    print(f"Done. Saved {len(output_data)} prompts to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
