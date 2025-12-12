"""Debug WHERE IN subquery structure more thoroughly."""
from sqlglot import parse_one, exp

sql = "SELECT * FROM users WHERE id IN (SELECT user_id FROM posts WHERE view_count > 1000)"
ast = parse_one(sql, dialect='mysql')

where_node = ast.args.get('where')
if where_node:
    in_expr = where_node.this
    print("IN expression attributes:")
    print(f"args: {in_expr.args.keys()}")
    print()
    for key, val in in_expr.args.items():
        print(f"{key}: {val}")
        print(f"  type: {type(val)}")
        print()
