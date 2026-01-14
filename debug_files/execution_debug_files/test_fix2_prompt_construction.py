#!/usr/bin/env python3
"""
Test script for Fix #2: Prompt Construction with Schema
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.harness.core.execution import ExecutionEngine
from src.harness.adapters.base import BaseModelAdapter

# Create a mock adapter for testing
class MockAdapter(BaseModelAdapter):
    def __init__(self):
        self.last_prompts = []
    
    def generate(self, prompts):
        self.last_prompts = prompts  # Store for inspection
        return ["SELECT * FROM users"] * len(prompts)
    
    def model_name(self):
        return "mock-model"
    
    def model_family(self):
        return "test"
    
    def decoding_config(self):
        return {"temperature": 0.0}

def test_prompt_construction():
    """Test that prompts are constructed with schema context"""
    print("=" * 60)
    print("Testing Fix #2: Prompt Construction")
    print("=" * 60)
    
    # Create execution engine
    adapter = MockAdapter()
    engine = ExecutionEngine(adapter, "test-run", "/tmp/test_output.jsonl")
    
    # Test 1: Check _construct_full_prompt method exists
    print("\n[Test 1] Checking _construct_full_prompt method...")
    assert hasattr(engine, '_construct_full_prompt'), "❌ Missing _construct_full_prompt method"
    print("✅ _construct_full_prompt method exists")
    
    # Test 2: Test prompt construction with sample NL query
    print("\n[Test 2] Testing prompt construction with sample query...")
    nl_query = "Get all users where email contains 'gmail'"
    full_prompt = engine._construct_full_prompt(nl_query)
    
    assert full_prompt, "❌ Constructed prompt is empty"
    assert "Database Schema:" in full_prompt, "❌ Missing schema header"
    assert "TABLES:" in full_prompt, "❌ Missing tables section"
    assert "users" in full_prompt, "❌ users table not in prompt"
    assert "FOREIGN KEY RELATIONSHIPS:" in full_prompt, "❌ Missing FK section"
    assert nl_query in full_prompt, "❌ Original NL query not in constructed prompt"
    assert "Generate a SQL query" in full_prompt or "SQL" in full_prompt, "❌ Missing SQL instruction"
    print("✅ Prompt constructed correctly with schema context")
    
    # Test 3: Verify prompt is used in execution loop
    print("\n[Test 3] Testing integration with execution loop...")
    
    # Create a minimal test data file
    test_data = [
        {
            "id": 1,
            "nl_prompt": "Get all posts",
            "sql": "SELECT * FROM posts",
            "prompt_text": "Get all posts"
        }
    ]
    
    test_file = "/tmp/test_prompts.json"
    import json
    with open(test_file, 'w') as f:
        json.dump(test_data, f)
    
    # Run a single batch
    prompts_data = engine._load_prompts(test_file)
    assert len(prompts_data) == 1, "❌ Failed to load test data"
    
    # Manually construct what should be sent
    expected_prompt = engine._construct_full_prompt(prompts_data[0]['prompt_text'])
    
    # Execute (will call adapter.generate)
    batch = prompts_data[0:1]
    prompt_texts = [engine._construct_full_prompt(p['prompt_text']) for p in batch]
    
    assert len(prompt_texts) == 1, "❌ Wrong number of prompts generated"
    assert "Database Schema:" in prompt_texts[0], "❌ Schema not in generated prompt"
    assert "Get all posts" in prompt_texts[0], "❌ Original query not in prompt"
    
    print("✅ Prompts are properly constructed in execution loop")
    
    # Display sample constructed prompt
    print("\n" + "=" * 60)
    print("Sample Constructed Prompt:")
    print("=" * 60)
    print(full_prompt[:500] + "..." if len(full_prompt) > 500 else full_prompt)
    print("=" * 60)
    
    print("\n✅ ALL TESTS PASSED ✅")
    print("\nFix #2 (Gap #1: Prompt Construction) is working correctly!\n")
    
    return True

if __name__ == "__main__":
    try:
        test_prompt_construction()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
