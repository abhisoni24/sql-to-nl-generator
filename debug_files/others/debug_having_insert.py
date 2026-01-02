"""Debug script to inspect HAVING and INSERT structure."""

from sqlglot import parse_one

# Test HAVING
sql1 = "SELECT user_id, COUNT(*) FROM posts GROUP BY user_id HAVING COUNT(*) > 5"
ast1 = parse_one(sql1, dialect='mysql')
print("HAVING AST:")
having = ast1.args.get('having')
if having:
    print(f"HAVING type: {type(having)}")
    print(f"HAVING.this: {having.this}")
    print(f"HAVING.this type: {type(having.this)}")
    if hasattr(having.this, 'this'):
        print(f"HAVING.this.this: {having.this.this}")
        print(f"HAVING.this.this type: {type(having.this.this)}")

print("\n" + "="*80 + "\n")

# Test INSERT schema  
sql2 = "INSERT INTO users (username, email) VALUES ('test', 'test@example.com')"
ast2 = parse_one(sql2, dialect='mysql')
print("INSERT Schema:")
schema = ast2.this
print(f"Schema type: {type(schema)}")
print(f"Schema.this: {schema.this}")
print(f"Schema.this type: {type(schema.this)}")
