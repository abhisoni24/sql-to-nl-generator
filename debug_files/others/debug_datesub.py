from sqlglot import exp

try:
    now = exp.Anonymous(this='NOW')
    days = 7
    interval = exp.Interval(this=exp.Literal.number(days), unit=exp.Var(this='DAY'))
    
    # Case 1: Passing Interval object
    ds1 = exp.DateSub(this=now, expression=interval)
    print(f"Case 1 (Interval obj): {ds1.sql(dialect='mysql')}")
    
    # Case 2: Passing Literal number? (Unlikely to work for MySQL DATE_SUB which needs unit)
    ds2 = exp.DateSub(this=now, expression=exp.Literal.number(days))
    print(f"Case 2 (Literal): {ds2.sql(dialect='mysql')}")

    # Case 3: Passing Literal number AND unit
    ds3 = exp.DateSub(this=now, expression=exp.Literal.number(days), unit=exp.Var(this='DAY'))
    print(f"Case 3 (Literal + Unit): {ds3.sql(dialect='mysql')}")

except Exception as e:
    print(f"Error: {e}")
