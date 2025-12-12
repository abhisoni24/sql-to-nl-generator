from sqlglot import exp

try:
    print("Testing select().from_()...")
    q = exp.select("*").from_("users", alias="u")
    print(q.sql())
except Exception as e:
    print(f"Error in from_: {e}")

try:
    print("Testing join()...")
    q = exp.select("*").from_("users", alias="u").join("posts", alias="p", on=exp.EQ(this=exp.column("id", table="u"), expression=exp.column("user_id", table="p")))
    print(q.sql())
except Exception as e:
    print(f"Error in join: {e}")

try:
    print("Testing column()...")
    c = exp.column("id", table="u")
    print(c.sql())
except Exception as e:
    print(f"Error in column: {e}")
