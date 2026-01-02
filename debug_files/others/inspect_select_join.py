import inspect
from sqlglot import exp

print(inspect.signature(exp.Select.join))
