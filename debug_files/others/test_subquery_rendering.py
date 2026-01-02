"""
Test script to investigate subquery rendering issue.
"""

from sqlglot import parse_one
from nl_renderer import SQLToNLRenderer

# The problematic query from the dataset
sql = """
SELECT * FROM (SELECT * FROM posts AS inner_posts 
WHERE inner_posts.posted_at >= DATE_SUB(NOW(), INTERVAL 13 DAY)) AS derived_table
"""

print("SQL:")
print(sql.strip())
print("\n" + "="*80 + "\n")

# Parse and inspect AST
ast = parse_one(sql, dialect='mysql')
print("AST Structure:")
from_node = ast.args.get('from_')
if from_node:
    table_expr = from_node.this
    print(f"FROM table type: {type(table_expr)}")
    print(f"Is Subquery: {type(table_expr).__name__ == 'Subquery'}")
    if hasattr(table_expr, 'this'):
        print(f"Subquery inner type: {type(table_expr.this)}")
        print(f"Subquery inner SQL: {table_expr.this.sql()}")

print("\n" + "="*80 + "\n")

# Current rendering
renderer = SQLToNLRenderer()
nl = renderer.render(ast)
print("Current NL:")
print(nl)

print("\n" + "="*80)
