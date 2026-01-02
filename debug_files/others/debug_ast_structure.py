"""Debug script to inspect AST structure."""

from sqlglot import parse_one

# Test SELECT
sql1 = "SELECT * FROM users WHERE id > 10"
ast1 = parse_one(sql1, dialect='mysql')
print("SELECT AST:")
print(f"Type: {type(ast1)}")
print(f"Args: {ast1.args.keys()}")
from_node = ast1.args.get('from')
print(f"FROM node: {from_node}")
if from_node:
    print(f"FROM.this: {from_node.this}")
    print(f"FROM.this type: {type(from_node.this)}")
    if hasattr(from_node.this, 'name'):
        print(f"FROM.this.name: {from_node.this.name}")

print("\n" + "="*80 + "\n")

# Test INSERT
sql2 = "INSERT INTO users (username, email) VALUES ('test', 'test@example.com')"
ast2 = parse_one(sql2, dialect='mysql')
print("INSERT AST:")
print(f"Type: {type(ast2)}")
print(f"this: {ast2.this}")
print(f"this type: {type(ast2.this)}")
if hasattr(ast2.this, 'name'):
    print(f"this.name: {ast2.this.name}")
