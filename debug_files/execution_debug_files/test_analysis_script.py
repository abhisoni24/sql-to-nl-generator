#!/usr/bin/env python3
"""
Test script for the analysis module using sample data.
Creates synthetic experiment results to demonstrate all analysis features.
"""
import json
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def create_sample_results(output_file: str, num_records: int = 200):
    """Create sample JSONL results for testing."""
    import random
    
    models = ["gemini-2.0-flash", "gpt-4o", "claude-3.5-sonnet"]
    perturbations = ["original", "typos", "under_specification", "synonym_substitution", 
                    "ambiguous_pronouns", "column_variations", "missing_where_details"]
    complexities = ["simple", "moderate", "complex", "advanced"]
    failure_types = ["none", "parse_error", "execution_error", "mismatch", "empty"]
    
    records = []
    for i in range(num_records):
        model = random.choice(models)
        pert_type = random.choice(perturbations)
        complexity = random.choice(complexities)
        
        # Simulate that original prompts are easier
        base_correctness = 0.85 if pert_type == "original" else 0.65
        # Simulate that simpler queries are easier
        complexity_factor = {"simple": 0.1, "moderate": 0, "complex": -0.1, "advanced": -0.2}
        correctness_prob = base_correctness + complexity_factor[complexity]
        
        is_correct = random.random() < correctness_prob
        similarity = random.uniform(0.7, 1.0) if is_correct else random.uniform(0.0, 0.6)
        
        if is_correct:
            failure = "none"
        else:
            failure = random.choice(["parse_error", "execution_error", "mismatch", "empty"])
        
        record = {
            "run_id": "sample-run-001",
            "model_name": model,
            "model_family": "api",
            "prompt_id": f"{i//10}_pert_{i%10}",
            "prompt_text": f"Sample query {i}",
            "perturbation_type": pert_type,
            "perturbation_id": perturbations.index(pert_type),
            "query_complexity": complexity,
            "tables_involved": ["users", "posts"],
            "gold_sql": "SELECT * FROM users WHERE id > 100",
            "raw_output": "SELECT * FROM users WHERE id > 100" if is_correct else "",
            "normalized_sql": "SELECT * FROM users WHERE id > 100" if is_correct else "",
            "evaluation_result": {
                "correctness": is_correct,
                "similarity_score": round(similarity, 4),
                "failure_type": failure
            },
            "decoding_config": {"temperature": 0.0, "max_tokens": 512},
            "metadata": {"query_id": i//10, "is_perturbed": pert_type != "original"},
            "timestamp": "2026-01-14T06:30:00.000000"
        }
        records.append(record)
    
    # Write to JSONL
    with open(output_file, 'w') as f:
        for record in records:
            f.write(json.dumps(record) + '\n')
    
    print(f"✓ Created {len(records)} sample records in {output_file}")
    return output_file


def test_analysis():
    """Test the analysis script with sample data."""
    print("=" * 60)
    print("Testing Analysis Script")
    print("=" * 60)
    
    # Create sample data
    sample_file = "/tmp/sample_experiment_results.jsonl"
    output_dir = "/tmp/sample_analysis_output"
    
    create_sample_results(sample_file, num_records=300)
    
    # Run analysis
    from src.harness.core.analyze_results import ExperimentAnalyzer
    
    analyzer = ExperimentAnalyzer(sample_file, output_dir)
    analyzer.run_full_analysis()
    
    # Verify outputs
    output_path = Path(output_dir)
    
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    
    # Check directories created
    assert (output_path / "figures").exists(), "Figures directory not created"
    assert (output_path / "tables").exists(), "Tables directory not created"
    print("✓ Output directories created")
    
    # Check key files exist
    expected_figures = [
        "model_accuracy_comparison.png",
        "model_similarity_boxplot.png",
        "perturbation_accuracy.png",
        "model_perturbation_heatmap.png",
        "complexity_accuracy_trend.png",
        "failure_distribution.png",
        "correlation_heatmap.png"
    ]
    
    missing_figures = []
    for fig in expected_figures:
        if not (output_path / "figures" / fig).exists():
            missing_figures.append(fig)
    
    if missing_figures:
        print(f"⚠️  Missing figures: {missing_figures}")
    else:
        print(f"✓ All {len(expected_figures)} expected figures generated")
    
    # Check tables
    expected_tables = [
        "summary_statistics.txt",
        "model_performance.csv",
        "perturbation_performance.csv",
        "complexity_performance.csv",
        "failure_modes.csv",
        "correlation_matrix.csv"
    ]
    
    missing_tables = []
    for table in expected_tables:
        if not (output_path / "tables" / table).exists():
            missing_tables.append(table)
    
    if missing_tables:
        print(f"⚠️  Missing tables: {missing_tables}")
    else:
        print(f"✓ All {len(expected_tables)} expected tables generated")
    
    # Check executive summary
    assert (output_path / "EXECUTIVE_SUMMARY.md").exists(), "Executive summary not created"
    print("✓ Executive summary created")
    
    # Display summary location
    print("\n" + "=" * 60)
    print("OUTPUTS SAVED TO:")
    print("=" * 60)
    print(f"  {output_path}")
    print(f"    - figures/ ({len(list((output_path / 'figures').glob('*.png')))} files)")
    print(f"    - tables/ ({len(list((output_path / 'tables').glob('*')))} files)")
    print(f"    - EXECUTIVE_SUMMARY.md")
    
    print("\n✅ ANALYSIS TEST PASSED!")
    print("\nYou can view the outputs at:")
    print(f"  {output_path}")


if __name__ == "__main__":
    try:
        test_analysis()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
