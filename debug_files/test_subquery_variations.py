"""
Test script for various subquery scenarios.
"""

from sqlglot import parse_one
from nl_renderer import SQLToNLRenderer

renderer = SQLToNLRenderer()

test_queries = [
    # Subquery in FROM
    "SELECT * FROM (SELECT * FROM posts WHERE view_count > 100) AS popular_posts",
    
    # Subquery in WHERE IN
    "SELECT * FROM users WHERE id IN (SELECT user_id FROM posts WHERE view_count > 1000)",
    
    # Nested subquery (subquery within subquery)
    "SELECT * FROM (SELECT * FROM (SELECT * FROM users WHERE is_verified = TRUE) AS verified) AS outer_query",
]

for i, sql in enumerate(test_queries, 1):
    print(f"Test {i}:")
    print(f"SQL: {sql}")
    try:
        ast = parse_one(sql, dialect='mysql')
        nl = renderer.render(ast)
        print(f"NL:  {nl}")
    except Exception as e:
        print(f"ERROR: {e}")
    print()
