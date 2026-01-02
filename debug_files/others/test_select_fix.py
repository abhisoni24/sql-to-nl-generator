"""
Test script to verify the redundant SELECT clause fix works correctly.
"""

from generator import SQLQueryGenerator
from schema import SCHEMA, FOREIGN_KEYS

# Initialize generator
gen = SQLQueryGenerator(SCHEMA, FOREIGN_KEYS)

# Generate 20 JOIN queries to test
print("Testing redundant SELECT clause fix...")
print("="*80)

redundant_count = 0
total_joins = 0

for i in range(100):
    query_ast, complexity = gen.generate_query()
    
    if complexity == 'join':
        total_joins += 1
        sql = query_ast.sql(dialect='mysql')
        
        # Check for redundancy: look for pattern "SELECT ..., * FROM"
        # This is a simple heuristic - if we have *, it should be the only thing selected
        select_clause = sql.split('FROM')[0] if 'FROM' in sql else sql
        
        # Check if both specific columns and * are present
        has_star = '*' in select_clause
        has_comma_before_star = ', *' in select_clause
        
        if has_star and has_comma_before_star:
            redundant_count += 1
            print(f"\n❌ REDUNDANT FOUND (Query {i}):")
            print(f"   {sql}")
        elif i < 10 and complexity == 'join':  # Show first 10 JOIN queries as examples
            print(f"\n✓ Query {i} ({complexity}):")
            print(f"   {sql}")

print("\n" + "="*80)
print(f"Total JOIN queries tested: {total_joins}")
print(f"Redundant queries found: {redundant_count}")

if redundant_count == 0:
    print("✅ SUCCESS: No redundant SELECT clauses detected!")
else:
    print(f"⚠️  FAILED: Found {redundant_count} redundant queries")

print("="*80)
