import sqlglot
from sqlglot import exp

# Test INSERT statement
sql = "INSERT INTO comments (user_id, post_id, comment_text, created_at) VALUES (124, 334, 'Sample text 33', NOW())"

# Parse it
ast = sqlglot.parse_one(sql)

print("AST Type:", type(ast))
print("\nAST Args:")
for key, value in ast.args.items():
    print(f"  {key}: {type(value)} = {value}")

print("\nDetailed Inspection:")
print("  this:", ast.this)
print("  this type:", type(ast.this))

# Check columns
columns = ast.args.get('columns')
print(f"\nColumns: {columns}")
if columns:
    print(f"  Type: {type(columns)}")
    if hasattr(columns, '__iter__') and not isinstance(columns, str):
        for i, col in enumerate(columns):
            print(f"  Column {i}: {col} (type: {type(col)})")

# Check values
values = ast.args.get('values')
print(f"\nValues: {values}")
if values:
    print(f"  Type: {type(values)}")
    print(f"  Has expressions: {hasattr(values, 'expressions')}")
    if hasattr(values, 'expressions'):
        print(f"  Expressions: {values.expressions}")
        for i, expr in enumerate(values.expressions):
            print(f"  Value expr {i}: {expr} (type: {type(expr)})")
            if hasattr(expr, 'expressions'):
                print(f"    Inner expressions: {expr.expressions}")
                for j, inner in enumerate(expr.expressions):
                    print(f"      Value {j}: {inner} (type: {type(inner)})")

# Check expression field
expression = ast.args.get('expression')
print(f"\nExpression: {expression}")
if expression:
    print(f"  Type: {type(expression)}")
    print(f"  Has expressions: {hasattr(expression, 'expressions')}")
    if hasattr(expression, 'expressions'):
        for i, e in enumerate(expression.expressions):
            print(f"  Tuple {i}: {e} (type: {type(e)})")
            if hasattr(e, 'expressions'):
                for j, val in enumerate(e.expressions):
                    print(f"    Val {j}: {val}")
