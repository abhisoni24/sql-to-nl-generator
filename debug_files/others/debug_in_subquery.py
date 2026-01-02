from sqlglot import exp

try:
    print("Testing IN with Subquery...")
    
    # Construct a subquery: SELECT id FROM users
    subquery = exp.select(exp.column("id")).from_(exp.to_table("users").as_("u"))
    
    # Construct IN clause: col IN (subquery)
    # Attempt 1: expression=subquery (Failed)
    in_expr = exp.In(this=exp.column("user_id"), expression=subquery)
    print(f"Attempt 1 (expression=subquery): {in_expr.sql(dialect='mysql')}")

    # Attempt 2: expressions=[subquery] (Likely correct for list)
    in_expr_list = exp.In(this=exp.column("user_id"), expressions=[subquery])
    print(f"Attempt 2 (expressions=[subquery]): {in_expr_list.sql(dialect='mysql')}")
    
    # Attempt 3: expression=subquery.subquery() ?
    # in_sub = exp.In(this=exp.column("user_id"), expression=subquery.subquery())
    # print(f"Attempt 3 (expression=subquery.subquery()): {in_sub.sql(dialect='mysql')}")
    
    # Test with empty subquery? (Not possible to have empty select really)
    
    # Test with Tuple?
    tup = exp.Tuple(expressions=[])
    in_empty = exp.In(this=exp.column("user_id"), expression=tup)
    print(f"Empty Tuple: {in_empty.sql(dialect='mysql')}")

except Exception as e:
    print(f"Error: {e}")
