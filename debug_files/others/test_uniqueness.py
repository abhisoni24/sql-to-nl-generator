"""
Test script to verify the uniqueness improvement in variations.
"""

from sqlglot import parse_one
from nl_renderer import SQLToNLRenderer

# Test with multiple queries
test_queries = [
    "SELECT * FROM users WHERE id > 10",
    "SELECT user_id, COUNT(*) FROM posts GROUP BY user_id",
    "SELECT u.username, p.content FROM users u JOIN posts p ON u.id = p.user_id",
    "INSERT INTO users (username) VALUES ('test')",
    "UPDATE posts SET view_count = 100 WHERE id = 1",
]

renderer = SQLToNLRenderer()

print("Testing Variation Uniqueness Improvement")
print("="*80)

all_unique = 0
has_duplicates = 0

for i, sql in enumerate(test_queries, 1):
    ast = parse_one(sql, dialect='mysql')
    results = renderer.generate_variations(ast, num_variations=3)
    
    variations = results['variations']
    unique_count = len(set(variations))
    
    print(f"\nQuery {i}: {sql[:60]}...")
    print(f"Vanilla: {results['vanilla']}")
    print("Variations:")
    for j, var in enumerate(variations, 1):
        print(f"  {j}. {var}")
    
    if unique_count == 3:
        print("✓ All 3 variations are unique")
        all_unique += 1
    else:
        print(f"⚠️  Only {unique_count} unique variations")
        has_duplicates += 1

print("\n" + "="*80)
print(f"Results: {all_unique}/{len(test_queries)} queries have all unique variations")
print(f"Success rate: {all_unique/len(test_queries)*100:.0f}%")
print("="*80)
