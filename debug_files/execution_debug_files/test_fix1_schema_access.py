#!/usr/bin/env python3
"""
Test script for Fix #1: Schema Access in ExecutionEngine
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.harness.core.execution import ExecutionEngine
from src.harness.adapters.base import BaseModelAdapter

# Create a mock adapter for testing
class MockAdapter(BaseModelAdapter):
    def generate(self, prompts):
        return ["SELECT * FROM users"] * len(prompts)
    
    def model_name(self):
        return "mock-model"
    
    def model_family(self):
        return "test"
    
    def decoding_config(self):
        return {"temperature": 0.0}

def test_schema_access():
    """Test that ExecutionEngine can access schema"""
    print("=" * 60)
    print("Testing Fix #1: Schema Access")
    print("=" * 60)
    
    # Create execution engine
    adapter = MockAdapter()
    engine = ExecutionEngine(adapter, "test-run", "/tmp/test_output.jsonl")
    
    # Test 1: Check schema is accessible
    print("\n[Test 1] Checking schema access...")
    assert hasattr(engine, 'schema'), "❌ ExecutionEngine missing 'schema' attribute"
    assert engine.schema is not None, "❌ Schema is None"
    assert 'users' in engine.schema, "❌ 'users' table not in schema"
    print("✅ Schema is accessible")
    
    # Test 2: Check foreign keys are accessible
    print("\n[Test 2] Checking foreign keys access...")
    assert hasattr(engine, 'foreign_keys'), "❌ ExecutionEngine missing 'foreign_keys' attribute"
    assert engine.foreign_keys is not None, "❌ Foreign keys is None"
    print("✅ Foreign keys are accessible")
    
    # Test 3: Check schema formatting method exists
    print("\n[Test 3] Checking _format_schema_text method...")
    assert hasattr(engine, '_format_schema_text'), "❌ Missing _format_schema_text method"
    print("✅ _format_schema_text method exists")
    
    # Test 4: Test schema formatting output
    print("\n[Test 4] Testing schema formatting output...")
    schema_text = engine._format_schema_text()
    assert schema_text, "❌ Schema text is empty"
    assert "Database Schema:" in schema_text, "❌ Missing 'Database Schema:' header"
    assert "TABLES:" in schema_text, "❌ Missing 'TABLES:' section"
    assert "users" in schema_text, "❌ 'users' table not in schema text"
    assert "posts" in schema_text, "❌ 'posts' table not in schema text"
    assert "FOREIGN KEY RELATIONSHIPS:" in schema_text, "❌ Missing 'FOREIGN KEY RELATIONSHIPS:' section"
    print("✅ Schema text formatted correctly")
    
    # Display formatted schema
    print("\n" + "=" * 60)
    print("Formatted Schema Output:")
    print("=" * 60)
    print(schema_text)
    print("=" * 60)
    
    print("\n✅ ALL TESTS PASSED ✅")
    print("\nFix #1 (Gap #3: Schema Access) is working correctly!\n")
    
    return True

if __name__ == "__main__":
    try:
        test_schema_access()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
