from sqlglot import exp

try:
    print("Testing Count(Star)...")
    c = exp.Count(this=exp.Star())
    print(c.sql())
except Exception as e:
    print(f"Error in Count(Star): {e}")

try:
    print("Testing Like...")
    l = exp.Like(this=exp.column("c"), expression=exp.Literal.string("%a%"))
    print(l.sql())
except Exception as e:
    print(f"Error in Like: {e}")

try:
    print("Testing In...")
    i = exp.In(this=exp.column("c"), expression=exp.Tuple(expressions=[exp.Literal.string("a")]))
    print(i.sql())
except Exception as e:
    print(f"Error in In: {e}")
