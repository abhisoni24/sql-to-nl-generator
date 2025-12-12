"""
Test script to verify the NL renderer works on a sample query.
"""

from sqlglot import parse_one
from nl_renderer import SQLToNLRenderer

# Test queries
test_queries = [
    "SELECT * FROM users WHERE id > 10",
    "SELECT u.username, p.content FROM users AS u JOIN posts AS p ON u.id = p.user_id WHERE p.view_count > 100",
    "SELECT user_id, COUNT(*) FROM posts GROUP BY user_id HAVING COUNT(*) > 5",
    "INSERT INTO users (username, email) VALUES ('test', 'test@example.com')",
    "UPDATE posts SET view_count = 100 WHERE id = 1",
    "DELETE FROM comments WHERE id < 10",
]

renderer = SQLToNLRenderer()

print("Testing NL Renderer on Sample Queries:")
print("=" * 80)

for i, sql in enumerate(test_queries, 1):
    print(f"\nTest {i}:")
    print(f"SQL: {sql}")
    try:
        ast = parse_one(sql, dialect='mysql')
        nl = renderer.render(ast)
        print(f"NL:  {nl}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
