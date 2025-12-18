"""
Test LLM SQL generation with vanilla and perturbed NL prompts.
Tests functional correctness by generating SQL from natural language.
"""

import json
import random
from datetime import datetime
from typing import List, Dict, Any
import os
from llm_client import get_llm_client


def load_random_samples(json_file: str, num_samples: int = 10) -> List[Dict[str, Any]]:
    """Load random samples from the dataset."""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Get random samples
    samples = random.sample(data, min(num_samples, len(data)))
    return samples


def test_nl_to_sql(
    samples: List[Dict[str, Any]],
    llm_provider: str = "gemini",
    model_name: str = None,
    output_dir: str = "test_results"
):
    """
    Test NL-to-SQL generation with LLM.
    
    Args:
        samples: List of query samples from dataset
        llm_provider: LLM provider to use ('gemini', 'openai', 'claude')
        model_name: Specific model name to use (optional)
        output_dir: Directory to save results
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize LLM client
    print(f"Initializing {llm_provider} client...")
    try:
        if model_name:
            client = get_llm_client(llm_provider, model_name=model_name)
        else:
            client = get_llm_client(llm_provider)
        print(f"✓ {llm_provider.capitalize()} client initialized (model: {client.model_name})")
    except Exception as e:
        print(f"✗ Failed to initialize {llm_provider} client: {e}")
        return
    
    # Prepare results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{output_dir}/test_results_{llm_provider}_{timestamp}.json"
    
    results = {
        'metadata': {
            'timestamp': timestamp,
            'llm_provider': llm_provider,
            'model_name': client.model_name,
            'num_samples': len(samples),
            'num_total_tests': len(samples) * 4  # 1 vanilla + 3 variations per sample
        },
        'tests': []
    }
    
    print(f"\nTesting {len(samples)} samples (4 prompts each = {len(samples) * 4} total tests)")
    print("="*80)
    
    # Test each sample
    for idx, sample in enumerate(samples, 1):
        sample_id = sample['id']
        ground_truth_sql = sample['sql']
        vanilla_nl = sample['nl_prompt']
        variations_nl = sample.get('nl_prompt_variations', [])
        
        print(f"\n[Sample {idx}/{len(samples)}] ID: {sample_id}")
        print(f"Ground Truth SQL: {ground_truth_sql[:80]}...")
        
        # Test vanilla prompt
        print(f"  Testing vanilla prompt...")
        vanilla_result = _test_single_prompt(
            client, vanilla_nl, ground_truth_sql, "vanilla"
        )
        
        # Test variations
        variation_results = []
        for var_idx, variation_nl in enumerate(variations_nl, 1):
            print(f"  Testing variation {var_idx}/3...")
            var_result = _test_single_prompt(
                client, variation_nl, ground_truth_sql, f"variation_{var_idx}"
            )
            variation_results.append(var_result)
        
        # Store results
        results['tests'].append({
            'sample_id': sample_id,
            'ground_truth_sql': ground_truth_sql,
            'complexity': sample.get('complexity'),
            'vanilla': vanilla_result,
            'variations': variation_results
        })
    
    # Save results
    with open(log_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*80)
    print(f"✓ Testing complete! Results saved to: {log_file}")
    
    # Print summary
    _print_summary(results)


def _test_single_prompt(
    client,
    nl_prompt: str,
    ground_truth_sql: str,
    prompt_type: str
) -> Dict[str, Any]:
    """Test a single NL prompt."""
    # Generate full prompt with schema
    full_prompt = client.get_schema_prompt(nl_prompt)
    
    # Generate SQL
    response = client.generate(full_prompt)
    
    return {
        'prompt_type': prompt_type,
        'nl_prompt': nl_prompt,
        'generated_sql': response['sql'],
        'success': response['success'],
        'error': response['error'],
        'raw_response': response['raw_response']
    }


def _print_summary(results: Dict[str, Any]):
    """Print test summary statistics."""
    print("\nTest Summary:")
    print("-" * 40)
    
    total_tests = results['metadata']['num_total_tests']
    successful = sum(
        1 for test in results['tests']
        for result in [test['vanilla']] + test['variations']
        if result['success']
    )
    failed = total_tests - successful
    
    print(f"Total Tests: {total_tests}")
    print(f"  Successful: {successful} ({successful/total_tests*100:.1f}%)")
    print(f"  Failed: {failed} ({failed/total_tests*100:.1f}%)")
    
    # Breakdown by type
    vanilla_success = sum(1 for test in results['tests'] if test['vanilla']['success'])
    variation_success = sum(
        1 for test in results['tests']
        for var in test['variations']
        if var['success']
    )
    
    print(f"\nBy Prompt Type:")
    print(f"  Vanilla: {vanilla_success}/{len(results['tests'])} ({vanilla_success/len(results['tests'])*100:.1f}%)")
    print(f"  Variations: {variation_success}/{len(results['tests'])*3} ({variation_success/(len(results['tests'])*3)*100:.1f}%)")


def main():
    """Main execution function."""
    # Configuration
    JSON_FILE = 'social_media_queries.json'
    NUM_SAMPLES = 10
    LLM_PROVIDER = 'gemini'
    MODEL_NAME = 'gemini-3-flash-preview'  # From user's example, 1k RPM limit
    
    print("SQL Generation Testing Framework")
    print("="*80)
    print(f"Dataset: {JSON_FILE}")
    print(f"Samples: {NUM_SAMPLES}")
    print(f"LLM Provider: {LLM_PROVIDER}")
    print(f"Model: {MODEL_NAME}")
    print("="*80)
    
    # Load samples
    print(f"\nLoading {NUM_SAMPLES} random samples...")
    samples = load_random_samples(JSON_FILE, NUM_SAMPLES)
    print(f"✓ Loaded {len(samples)} samples")
    
    # Run tests
    test_nl_to_sql(samples, llm_provider=LLM_PROVIDER, model_name=MODEL_NAME)


if __name__ == "__main__":
    main()
