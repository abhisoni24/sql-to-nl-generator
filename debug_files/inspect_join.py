import inspect
from sqlglot import exp

print(inspect.signature(exp.Join.__init__))
