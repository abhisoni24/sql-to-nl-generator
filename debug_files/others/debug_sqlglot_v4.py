from sqlglot import exp

try:
    print("Testing Literal.number...")
    l = exp.Literal.number(1)
    print(l.sql())
except Exception as e:
    print(f"Error in Literal.number: {e}")

try:
    print("Testing Literal.string...")
    l = exp.Literal.string("abc")
    print(l.sql())
except Exception as e:
    print(f"Error in Literal.string: {e}")

try:
    print("Testing Boolean...")
    b = exp.Boolean(this=True)
    print(b.sql())
except Exception as e:
    print(f"Error in Boolean: {e}")
