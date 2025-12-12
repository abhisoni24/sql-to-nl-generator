from sqlglot import exp

try:
    # Current approach
    values = [exp.Literal.number(1), exp.Literal.string('test')]
    ins1 = exp.insert(
        exp.Tuple(expressions=values),
        "users",
        columns=[exp.Identifier(this='id', quoted=False), exp.Identifier(this='name', quoted=False)]
    )
    print(f"Current: {ins1.sql(dialect='mysql')}")
    
    # Correct approach?
    # exp.insert(expression=values_expression, ...)
    # Maybe use exp.Values?
    
    vals = exp.Values(expressions=[exp.Tuple(expressions=values)])
    ins2 = exp.insert(
        vals,
        "users",
        columns=[exp.Identifier(this='id', quoted=False), exp.Identifier(this='name', quoted=False)]
    )
    print(f"With exp.Values: {ins2.sql(dialect='mysql')}")

except Exception as e:
    print(f"Error: {e}")
