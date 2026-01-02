
import json
import os
from collections import Counter, defaultdict

INPUT_FILE = '../../dataset/current/nl_social_media_queries_perturbed.json'
FAILED_ID_FILE = 'failed_sql_ids.txt'

def analyze():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, INPUT_FILE)
    failed_path = os.path.join(base_dir, FAILED_ID_FILE)

    # Load successfully processed data
    with open(input_path, 'r') as f:
        data = json.load(f)

    # Load failed IDs
    failed_ids = []
    if os.path.exists(failed_path):
        with open(failed_path, 'r') as f:
            failed_ids = f.read().splitlines()

    total_attempted = 2100
    total_processed = len(data)
    total_failed = len(failed_ids)

    print(f"Total Attempted: {total_attempted}")
    print(f"Successfully Processed: {total_processed}")
    print(f"Failed: {total_failed}")

    # Metrics containers
    single_stats = defaultdict(lambda: {'applicable': 0, 'not_applicable': 0, 'total': 0})
    compound_counts = []
    compound_combinations = Counter()
    complexity_counts = Counter()

    for item in data:
        # Complexity
        complexity = item.get('complexity', 'unknown')
        complexity_counts[complexity] += 1

        # Generated data
        gen = item.get('generated_perturbations', {})
        singles = gen.get('single_perturbations', [])
        compound = gen.get('compound_perturbation', {})

        # Single Analysis
        for p in singles:
            p_name = p['perturbation_name']
            is_app = p['applicable']
            
            single_stats[p_name]['total'] += 1
            if is_app:
                single_stats[p_name]['applicable'] += 1
            else:
                single_stats[p_name]['not_applicable'] += 1

        # Compound Analysis
        applied = compound.get('perturbations_applied', [])
        compound_counts.append(len(applied))
        
        # Sort to handle same set in different order
        combo_names = tuple(sorted([p['perturbation_name'] for p in applied]))
        compound_combinations[combo_names] += 1

    # Output Results
    print("\n--- Complexity Distribution ---")
    for comp, count in complexity_counts.items():
        print(f"{comp}: {count}")

    print("\n--- Single Perturbation Applicability ---")
    print(f"{'Perturbation Type':<30} | {'Appl':<5} | {'N/A':<5} | {'Rate %':<6}")
    print("-" * 55)
    for p_name, stats in single_stats.items():
        rate = (stats['applicable'] / stats['total']) * 100 if stats['total'] > 0 else 0
        print(f"{p_name:<30} | {stats['applicable']:<5} | {stats['not_applicable']:<5} | {rate:6.1f}")

    print("\n--- Compound Perturbation Statistics ---")
    avg_perts = sum(compound_counts) / len(compound_counts) if compound_counts else 0
    print(f"Average number of perturbations per compound: {avg_perts:.2f}")
    
    print("\nTop 10 Compound Combinations:")
    for combo, count in compound_combinations.most_common(10):
        print(f"{count}: {', '.join(combo)}")

if __name__ == "__main__":
    analyze()
