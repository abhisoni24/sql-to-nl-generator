"""Debug WHERE IN subquery."""
from sqlglot import parse_one, exp

sql = "SELECT * FROM users WHERE id IN (SELECT user_id FROM posts WHERE view_count > 1000)"
ast = parse_one(sql, dialect='mysql')

where_node = ast.args.get('where')
if where_node:
    print(f"WHERE condition type: {type(where_node.this)}")
    in_expr = where_node.this
    if isinstance(in_expr, exp.In):
        print("It's an IN expression")
        print(f"expressions attr exists: {hasattr(in_expr, 'expressions')}")
        exprs = in_expr.expressions if hasattr(in_expr, 'expressions') else []
        print(f"Number of expressions: {len(exprs)}")
        if exprs:
            print(f"First expression type: {type(exprs[0])}")
            print(f"First expression: {exprs[0]}")
