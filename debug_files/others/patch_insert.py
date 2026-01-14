import sys

# Read the file
with open('src/core/nl_renderer.py', 'r') as f:
    lines = f.readlines()

# Find and replace the render_insert method
new_insert_method = '''    def render_insert(self, node):
        """Render INSERT with column/value details."""
        # Get Schema object which contains table + columns
        schema = node.this
        
        # Extract table name and columns from Schema
        if isinstance(schema, exp.Schema):
            table_node = schema.this
            # Columns are stored as Identifier objects in schema.expressions
            columns_list = schema.expressions if hasattr(schema, 'expressions') else []
        else:
            table_node = schema
            columns_list = []
        
        # Extract values from 'expression' field (not 'values')
        values_expr = node.args.get('expression')
        values_list = []
        
        if isinstance(values_expr, exp.Values) and hasattr(values_expr, 'expressions'):
            # Get first tuple
            first_tuple = values_expr.expressions[0]
            if isinstance(first_tuple, exp.Tuple) and hasattr(first_tuple, 'expressions'):
                values_list = first_tuple.expressions
        
        # Build with perturbations
        if columns_list and values_list:
            # Render columns - handle Identifier objects
            cols_rendered = []
            for i, c in enumerate(columns_list):
                if isinstance(c, exp.Identifier):
                    col_name = str(c.this)
                    # Apply column perturbations manually
                    if self.config.is_active(PerturbationType.COLUMN_VARIATIONS):
                        rng = self._get_rng(f"insert_col_{i}")
                        if "_" in col_name:
                            parts = col_name.split('_')
                            if rng.choice([True, False]):
                                col_name = parts[0] + ''.join(x.title() for x in parts[1:])
                    cols_rendered.append(col_name)
                else:
                    cols_rendered.append(self._render_expression(c, f"insert_col_{i}"))
            
            # Render values
            vals_rendered = [self._render_expression(v, f"insert_val_{i}") for i, v in enumerate(values_list)]
            
            # Render table with perturbations
            table_display = self._render_table(table_node, "insert_table")
            
            # Build column=value pairs
            pairs = [f"{c} {v}" for c, v in zip(cols_rendered, vals_rendered)]
            
            return f"Insert into {table_display} with {', '.join(pairs)}."
        
        # Fallback
        table_display = self._render_table(table_node if isinstance(schema, exp.Schema) else schema, "insert_table")
        return f"Insert into {table_display}."
        
'''

# Find the start of render_insert
start_idx = None
for i, line in enumerate(lines):
    if 'def render_insert(self, node):' in line:
        start_idx = i
        break

if start_idx is None:
    print("ERROR: Could not find render_insert method")
    sys.exit(1)

# Find the end (next method def)
end_idx = None
for i in range(start_idx + 1, len(lines)):
    if lines[i].strip().startswith('def ') and not lines[i].strip().startswith('def _'):
        end_idx = i
        break

if end_idx is None:
    print("ERROR: Could not find end of render_insert method")
    sys.exit(1)

# Replace
new_lines = lines[:start_idx] + [new_insert_method] + lines[end_idx:]

# Write back
with open('src/core/nl_renderer.py', 'w') as f:
    f.writelines(new_lines)

print(f"Successfully replaced render_insert method (lines {start_idx+1} to {end_idx})")
