from sqlglot import exp

try:
    t1 = exp.to_table("users").as_("u")
    t2 = exp.to_table("posts").as_("p")
    
    # Test INNER
    q1 = exp.select("*").from_(t1).join(t2, on=exp.EQ(this=exp.column("id", table="u"), expression=exp.column("user_id", table="p")), kind="INNER")
    print(f"INNER: {q1.sql(dialect='mysql')}")
    
    # Test LEFT
    q2 = exp.select("*").from_(t1).join(t2, on=exp.EQ(this=exp.column("id", table="u"), expression=exp.column("user_id", table="p")), kind="LEFT")
    print(f"LEFT: {q2.sql(dialect='mysql')}")

    # Test LEFT OUTER
    q3 = exp.select("*").from_(t1).join(t2, on=exp.EQ(this=exp.column("id", table="u"), expression=exp.column("user_id", table="p")), kind="LEFT OUTER")
    print(f"LEFT OUTER: {q3.sql(dialect='mysql')}")
    
    # Test lowercase left
    q4 = exp.select("*").from_(t1).join(t2, on=exp.EQ(this=exp.column("id", table="u"), expression=exp.column("user_id", table="p")), kind="left")
    print(f"lowercase left: {q4.sql(dialect='mysql')}")

    # Test left_join method
    try:
        q5 = exp.select("*").from_(t1).left_join(t2, on=exp.EQ(this=exp.column("id", table="u"), expression=exp.column("user_id", table="p")))
        print(f"left_join method: {q5.sql(dialect='mysql')}")
    except AttributeError:
        print("left_join method does not exist")

    # Test join_type="LEFT"
    q7 = exp.select("*").from_(t1).join(t2, on=exp.EQ(this=exp.column("id", table="u"), expression=exp.column("user_id", table="p")), join_type="LEFT")
    print(f"join_type='LEFT': {q7.sql(dialect='mysql')}")


except Exception as e:
    print(f"Error: {e}")
