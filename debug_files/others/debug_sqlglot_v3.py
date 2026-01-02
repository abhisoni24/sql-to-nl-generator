from sqlglot import exp

try:
    print("Testing column with table string...")
    c = exp.column("id", table="u")
    print(c.sql())
except Exception as e:
    print(f"Error in column: {e}")

try:
    print("Testing Func(this='NOW')...")
    f = exp.Func(this='NOW')
    print(f.sql())
except Exception as e:
    print(f"Error in Func: {e}")

try:
    print("Testing Anonymous func...")
    f = exp.Anonymous(this="NOW")
    print(f.sql())
except Exception as e:
    print(f"Error in Anonymous: {e}")
