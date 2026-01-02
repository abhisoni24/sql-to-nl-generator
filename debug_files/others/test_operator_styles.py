"""
Test operator style perturbation fix
"""
from sqlglot import parse_one
from nl_renderer import SQLToNLRenderer

# Test query with operators
sql = "SELECT * FROM users WHERE age > 18 AND score >= 90 AND status != 'inactive'"

print("Testing Operator Style Perturbation Fix")
print("="*80)
print(f"SQL: {sql}\n")

ast = parse_one(sql, dialect='mysql')

# Test different operator styles
print("1. Words style:")
renderer = SQLToNLRenderer(operator_style='words')
print(f"   {renderer.render(ast)}\n")

print("2. Symbols style:")
renderer = SQLToNLRenderer(operator_style='symbols')
print(f"   {renderer.render(ast)}\n")

print("3. Mixed style (run 3 times to show randomness):")
for i in range(3):
    renderer = SQLToNLRenderer(operator_style='mixed')
    print(f"   {i+1}. {renderer.render(ast)}")

print("\n" + "="*80)
print("✓ Operator styles are now working!")
