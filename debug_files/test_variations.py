"""
Test script to verify NL renderer variations work correctly.
"""

from sqlglot import parse_one
from nl_renderer import SQLToNLRenderer

# Test query
sql = "SELECT user_id, COUNT(*) FROM posts WHERE view_count > 100 GROUP BY user_id HAVING COUNT(*) > 5"

print("Testing NL Renderer Variations")
print("="*80)
print(f"SQL: {sql}\n")

# Parse SQL
ast = parse_one(sql, dialect='mysql')

# Initialize renderer
renderer = SQLToNLRenderer()

# Generate variations
results = renderer.generate_variations(ast, num_variations=3)

print("Vanilla NL Prompt:")
print(f"  {results['vanilla']}\n")

print("Variations:")
for i, var in enumerate(results['variations'], 1):
    print(f"  {i}. {var}")

print("="*80)
print("Test completed successfully!")
