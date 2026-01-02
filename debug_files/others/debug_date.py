from sqlglot import exp

try:
    print("Testing Interval...")
    i = exp.Interval(this=exp.Literal.number(7), unit=exp.Var(this='DAY'))
    print(i.sql())
except Exception as e:
    print(f"Error in Interval: {e}")

try:
    print("Testing DateSub...")
    # posted_at > NOW() - INTERVAL 7 DAY
    # This is often exp.GT(this=col, expression=exp.Sub(this=exp.Anonymous(this='NOW'), expression=exp.Interval...))
    
    now = exp.Anonymous(this='NOW')
    interval = exp.Interval(this=exp.Literal.number(7), unit=exp.Var(this='DAY'))
    sub = exp.Sub(this=now, expression=interval)
    print(f"Subtraction: {sub.sql()}")
    
    # Or maybe DateSub function?
    ds = exp.DateSub(this=now, expression=interval)
    print(f"DateSub: {ds.sql()}")

except Exception as e:
    print(f"Error in Date logic: {e}")
