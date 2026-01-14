#!/usr/bin/env python3
"""
Test script for Fix #4: Enhanced Logging Metadata
"""
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.harness.core.execution import ExecutionEngine
from src.harness.adapters.base import BaseModelAdapter

# Create a mock adapter for testing
class MockAdapter(BaseModelAdapter):
    def generate(self, prompts):
        # Return valid SQL for testing
        return ["SELECT * FROM users WHERE id > 100"] * len(prompts)
    
    def model_name(self):
        return "mock-model"
    
    def model_family(self):
        return "test"
    
    def decoding_config(self):
        return {"temperature": 0.0, "max_tokens": 512}

def test_enhanced_logging():
    """Test that logging includes all enhanced metadata fields"""
    print("=" * 60)
    print("Testing Fix #4: Enhanced Logging Metadata")
    print("=" * 60)
    
    # Create execution engine
    output_file = "/tmp/test_enhanced_logging.jsonl"
    if os.path.exists(output_file):
        os.remove(output_file)
    
    adapter = MockAdapter()
    engine = ExecutionEngine(adapter, "test-run-logging", output_file)
    
    # Test 1: Create sample test data with full metadata
    print("\n[Test 1] Creating sample test data with metadata...")
    test_data = [
        {
            "id": 101,
            "complexity": "simple",
            "sql": "SELECT * FROM users WHERE id > 100",
            "tables": ["users"],
            "generated_perturbations": {
                "original": {
                    "nl_prompt": "Get all users where id is greater than 100"
                },
                "single_perturbations": [
                    {
                        "perturbation_id": 1,
                        "perturbation_name": "typos",
                        "applicable": True,
                        "perturbed_nl_prompt": "Get all usres where id is grater than 100",
                        "changes_made": "Injected typos"
                    }
                ]
            }
        }
    ]
    
    test_file = "/tmp/test_prompts_logging.json"
    with open(test_file, 'w') as f:
        json.dump(test_data, f)
    
    print("✅ Test data created")
    
    # Test 2: Run experiment to generate logs
    print("\n[Test 2] Running mini experiment to generate logs...")
    engine.execute_experiment(test_file)
    print("✅ Experiment completed")
    
    # Test 3: Read and verify log records
    print("\n[Test 3] Verifying enhanced log record structure...")
    assert os.path.exists(output_file), "❌ Output file not created"
    
    with open(output_file, 'r') as f:
        lines = f.readlines()
    
    assert len(lines) == 2, f"❌ Expected 2 log records (original + 1 perturbation), got {len(lines)}"
    
    # Parse both records
    records = [json.loads(line) for line in lines]
    
    # Test 4: Verify required fields exist in all records
    print("\n[Test 4] Checking all required fields are present...")
    required_fields = [
        "run_id", "model_name", "model_family", "prompt_id",
        "perturbation_type", "perturbation_id", "query_complexity",
        "tables_involved", "gold_sql", "raw_output", "normalized_sql",
        "evaluation_result", "decoding_config", "metadata", "timestamp"
    ]
    
    for i, record in enumerate(records):
        for field in required_fields:
            assert field in record, f"❌ Record {i} missing field: {field}"
    
    print(f"✅ All {len(required_fields)} required fields present in all records")
    
    # Test 5: Verify original record metadata
    print("\n[Test 5] Verifying original prompt metadata...")
    original_record = [r for r in records if r['perturbation_type'] == 'original'][0]
    
    assert original_record['perturbation_id'] == 0, "❌ Original should have perturbation_id=0"
    assert original_record['query_complexity'] == 'simple', "❌ Wrong complexity"
    assert original_record['tables_involved'] == ['users'], "❌ Wrong tables"
    assert original_record['gold_sql'] == "SELECT * FROM users WHERE id > 100", "❌ Wrong gold SQL"
    assert 'is_perturbed' in original_record['metadata'], "❌ Missing is_perturbed in metadata"
    assert original_record['metadata']['is_perturbed'] == False, "❌ Original should not be perturbed"
    
    print("✅ Original prompt metadata correct")
    
    # Test 6: Verify perturbed record metadata
    print("\n[Test 6] Verifying perturbed prompt metadata...")
    perturbed_record = [r for r in records if r['perturbation_type'] == 'typos'][0]
    
    assert perturbed_record['perturbation_id'] == 1, "❌ Wrong perturbation_id"
    assert perturbed_record['perturbation_type'] == 'typos', "❌ Wrong perturbation_type"
    assert perturbed_record['query_complexity'] == 'simple', "❌ Wrong complexity"
    assert perturbed_record['tables_involved'] == ['users'], "❌ Wrong tables"
    assert perturbed_record['gold_sql'] == "SELECT * FROM users WHERE id > 100", "❌ Same gold SQL as original"
    assert 'is_perturbed' in perturbed_record['metadata'], "❌ Missing is_perturbed in metadata"
    assert perturbed_record['metadata']['is_perturbed'] == True, "❌ Perturbed should be marked"
    
    print("✅ Perturbed prompt metadata correct")
    
    # Display sample log record
    print("\n" + "=" * 60)
    print("Sample Enhanced Log Record:")
    print("=" * 60)
    print(json.dumps(records[0], indent=2))
    print("=" * 60)
    
    print("\n✅ ALL TESTS PASSED ✅")
    print("\nFix #4 (Gap #4: Enhanced Logging) is working correctly!")
    print("\nNew log fields:")
    print("  - perturbation_type")
    print("  - perturbation_id")
    print("  - query_complexity")
    print("  - tables_involved")
    print("  - gold_sql")
    print("  - expanded metadata\n")
    
    return True

if __name__ == "__main__":
    try:
        test_enhanced_logging()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
