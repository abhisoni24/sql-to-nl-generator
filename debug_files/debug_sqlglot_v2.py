from sqlglot import exp

try:
    print("Testing select().from_(exp.to_table().as_())...")
    t = exp.to_table("users").as_("u")
    q = exp.select("*").from_(t)
    print(q.sql())
except Exception as e:
    print(f"Error in from_ v2: {e}")

try:
    print("Testing join(exp.to_table().as_())...")
    t1 = exp.to_table("users").as_("u")
    t2 = exp.to_table("posts").as_("p")
    q = exp.select("*").from_(t1).join(t2, on=exp.EQ(this=exp.column("id", table="u"), expression=exp.column("user_id", table="p")))
    print(q.sql())
except Exception as e:
    print(f"Error in join v2: {e}")
