from sqlglot import parse_one, exp

sql = "SELECT * FROM a LEFT JOIN b ON a.id = b.id"
parsed = parse_one(sql)
print(f"Parsed SQL: {parsed.sql()}")

# Find the join
join = parsed.find(exp.Join)
print(f"Join args: {join.args}")
print(f"Join kind: {join.args.get('kind')}")
