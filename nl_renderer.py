"""
Syntax-Directed Translation (SDT) Framework for SQL to Natural Language
This module provides deterministic, template-based rendering of SQL ASTs to NL prompts.
"""

from sqlglot import exp


class SQLToNLRenderer:
    """Renders SQL AST nodes to natural language using deterministic templates."""
    
    def __init__(
        self,
        use_variations=True,
        verbosity='normal',
        operator_style='mixed',
        add_fluff=False,
        code_switch_probability=0.0
    ):
        """
        Initialize renderer with perturbation settings.
        
        Args:
            use_variations: Enable lexical variation and aggregate variety
            verbosity: 'terse', 'normal', or 'verbose'
            operator_style: 'words', 'symbols', or 'mixed'
            add_fluff: Add conversational prefixes/suffixes
            code_switch_probability: Probability (0.0-1.0) of using SQL keywords
        """
        self.use_variations = use_variations
        self.verbosity = verbosity
        self.operator_style = operator_style
        self.add_fluff = add_fluff
        self.code_switch_prob = code_switch_probability
        
        # Synonym mappings for lexical variation
        self.synonyms = {
            'get': ['Get', 'Retrieve', 'Fetch', 'Select', 'Show', 'Find', 'Pull'],
            'where': ['where', 'filtering by', 'with condition', 'such that', 'that match'],
            'from': ['from', 'in', 'within', 'from table'],
            'grouped by': ['grouped by', 'group by', 'organized by', 'categorized by', 'partitioned by'],
            'ordered by': ['ordered by', 'sorted by', 'arranged by', 'organized by'],
            'limited to': ['limited to', 'with limit of', 'taking only', 'restricted to', 'top'],
            'having': ['having', 'with condition', 'where aggregate', 'filtered by'],
            'joined with': ['joined with', 'join', 'combined with', 'merged with'],
            'equals': ['equals', 'is', 'matches', '='],
            'not equals': ['not equals', 'is not', 'differs from', '!=', '<>'],
            'greater than': ['greater than', 'more than', 'exceeds', 'above', '>'],
            'less than': ['less than', 'below', 'under', 'fewer than', '<'],
            'greater than or equal to': ['greater than or equal to', 'at least', '>=', 'no less than'],
            'less than or equal to': ['less than or equal to', 'at most', '<=', 'no more than'],
            'like': ['like', 'matching pattern', 'similar to', 'matches'],
            'in': ['in', 'within', 'among', 'one of'],
        }
        
        # Aggregate description variations
        self.agg_variations = {
            'count': ['count of', 'number of', 'how many', 'total count of', 'tally of'],
            'sum': ['sum of', 'total', 'add up', 'combined', 'total of'],
            'avg': ['average of', 'mean', 'avg', 'average value of', 'mean value of'],
            'min': ['minimum of', 'smallest', 'lowest', 'min', 'minimum value of'],
            'max': ['maximum of', 'largest', 'highest', 'max', 'maximum value of']
        }
        
        # Contextual fluff for conversational style
        self.fluff_prefixes = [
            "I need to", "Please", "Can you", "Let's", 
            "I want to", "Show me how to", "Help me",
            "Could you", "I'd like to", ""
        ]
        
        self.fluff_suffixes = [
            "please", "thanks", "for me", "if possible",
            "when you get a chance", ""
        ]
        
        # SQL keyword mappings for code-switching
        self.sql_keyword_map = {
            'get': 'SELECT',
            'where': 'WHERE',
            'from': 'FROM',
            'grouped by': 'GROUP BY',
            'ordered by': 'ORDER BY',
            'limited to': 'LIMIT',
            'having': 'HAVING',
            'joined with': 'JOIN',
            'left joined with': 'LEFT JOIN',
            'right joined with': 'RIGHT JOIN',
        }
    
    def _choose_word(self, canonical_form):
        """Select a synonym based on variation mode."""
        import random
        if not self.use_variations:
            # Return default (first option for most, or canonical for operators)
            options = self.synonyms.get(canonical_form, [canonical_form])
            return options[0] if options else canonical_form
        return random.choice(self.synonyms.get(canonical_form, [canonical_form]))
    
    def _choose_agg_variant(self, agg_type):
        """Choose variation for aggregate description."""
        import random
        if not self.use_variations:
            return self.agg_variations[agg_type][0]
        return random.choice(self.agg_variations.get(agg_type, ['aggregate']))
    
    def _format_operator(self, op_type):
        """Get operator representation based on style."""
        import random
        operator_maps = {
            'words': {
                'eq': 'equals', 'neq': 'not equals',
                'gt': 'greater than', 'gte': 'greater than or equal to',
                'lt': 'less than', 'lte': 'less than or equal to',
                'like': 'like', 'in': 'in'
            },
            'symbols': {
                'eq': '=', 'neq': '!=',
                'gt': '>', 'gte': '>=',
                'lt': '<', 'lte': '<=',
                'like': 'LIKE', 'in': 'IN'
            }
        }
        
        if self.operator_style == 'mixed':
            style = random.choice(['words', 'symbols'])
        else:
            style = self.operator_style
        
        return operator_maps[style].get(op_type, op_type)
    
    def _maybe_sql_keyword(self, nl_word):
        """Randomly decide to use SQL keyword instead of NL."""
        import random
        if self.code_switch_prob > 0 and random.random() < self.code_switch_prob:
            return self.sql_keyword_map.get(nl_word, nl_word)
        return nl_word
    
    def render(self, ast):
        """Main entry point: render any SQL statement to NL."""
        import random
        
        # Generate base NL
        if isinstance(ast, exp.Select):
            base_nl = self.render_select(ast)
        elif isinstance(ast, exp.Insert):
            base_nl = self.render_insert(ast)
        elif isinstance(ast, exp.Update):
            base_nl = self.render_update(ast)
        elif isinstance(ast, exp.Delete):
            base_nl = self.render_delete(ast)
        else:
            base_nl = f"Execute statement: {ast.sql()}"
        
        # Apply fluff if enabled
        if self.add_fluff and random.random() < 0.7:  # 70% chance to add fluff
            prefix = random.choice(self.fluff_prefixes)
            suffix = random.choice(self.fluff_suffixes)
            
            if prefix:
                # Adjust capitalization: "I need to get users" not "I need to Get users"
                base_nl = base_nl[0].lower() + base_nl[1:] if base_nl else base_nl
                base_nl = f"{prefix} {base_nl}"
            
            if suffix:
                # Remove trailing period before adding suffix
                base_nl = base_nl.rstrip('.')
                base_nl = f"{base_nl} {suffix}."
        
        return base_nl
    
    # ========== SELECT Statement ==========
    
    def render_select(self, node):
        """Render SELECT statement."""
        parts = []
        
        # SELECT clause
        select_clause = self._render_select_clause(node)
        parts.append(select_clause)
        
        # FROM clause
        from_clause = self._render_from_clause(node)
        if from_clause:
            parts.append(from_clause)
        
        # WHERE clause
        where_clause = self._render_where_clause(node)
        if where_clause:
            parts.append(where_clause)
        
        # GROUP BY clause
        group_clause = self._render_group_by_clause(node)
        if group_clause:
            parts.append(group_clause)
        
        # HAVING clause
        having_clause = self._render_having_clause(node)
        if having_clause:
            parts.append(having_clause)
        
        # ORDER BY clause
        order_clause = self._render_order_by_clause(node)
        if order_clause:
            parts.append(order_clause)
        
        # LIMIT clause
        limit_clause = self._render_limit_clause(node)
        if limit_clause:
            parts.append(limit_clause)
        
        return " ".join(parts) + "."
    
    def _render_select_clause(self, node):
        """Render SELECT column list."""
        expressions = node.expressions
        if not expressions:
            get_word = self._maybe_sql_keyword('get')
            get_word = self._choose_word(get_word if get_word != 'SELECT' else 'get')
            return f"{get_word} all columns"
        
        col_descriptions = []
        for expr in expressions:
            if isinstance(expr, exp.Star):
                col_descriptions.append("all columns")
            elif isinstance(expr, exp.Alias):
                # Aggregates or aliased expressions
                inner = expr.this
                if isinstance(inner, (exp.Count, exp.Sum, exp.Avg, exp.Min, exp.Max)):
                    col_descriptions.append(self._render_aggregate(inner))
                else:
                    col_descriptions.append(self._render_expression(inner))
            elif isinstance(expr, (exp.Count, exp.Sum, exp.Avg, exp.Min, exp.Max)):
                # Aggregates without alias
                col_descriptions.append(self._render_aggregate(expr))
            else:
                col_descriptions.append(self._render_expression(expr))
        
        # Apply variations to "Get" keyword
        get_word = self._maybe_sql_keyword('get')
        if get_word == 'SELECT':
            select_word = 'SELECT'
        else:
            select_word = self._choose_word('get')
        
        # Apply verbosity
        if self.verbosity == 'terse':
            return f"{select_word} {', '.join(col_descriptions)}"
        elif self.verbosity == 'verbose':
            if len(col_descriptions) == 1:
                return f"I need to retrieve the following column: {col_descriptions[0]}"
            else:
                return f"I need to retrieve the following columns: {', '.join(col_descriptions)}"
        else:  # normal
            if len(col_descriptions) == 1:
                return f"{select_word} {col_descriptions[0]}"
            else:
                return f"{select_word} {', '.join(col_descriptions)}"
    
    def _render_from_clause(self, node):
        """Render FROM clause with tables and joins."""
        from_node = node.args.get('from_')  # Note: key is 'from_' not 'from'
        if not from_node:
            return None
        
        # Get base table
        table_expr = from_node.this
        table_name = self._render_table(table_expr)
        
        # Apply variations to "from" keyword
        from_word = self._maybe_sql_keyword('from')
        if from_word == 'FROM':
            from_word = 'FROM'
        else:
            from_word = self._choose_word('from')
        
        # Apply verbosity
        if self.verbosity == 'verbose':
            parts = [f"from the table named {table_name}"]
        else:
            parts = [f"{from_word} {table_name}"]
        
        # Add joins
        joins = node.args.get('joins', [])
        for join in joins:
            parts.append(self._render_join(join))
        
        return " ".join(parts)
    
    def _render_where_clause(self, node):
        """Render WHERE clause."""
        where_node = node.args.get('where')
        if not where_node:
            return None
        
        condition = self._render_expression(where_node.this)
        
        # Apply variations to "where" keyword
        where_word = self._maybe_sql_keyword('where')
        if where_word == 'WHERE':
            where_word = 'WHERE'
        else:
            where_word = self._choose_word('where')
        
        # Apply verbosity
        if self.verbosity == 'terse':
            return f"{where_word} {condition}"
        elif self.verbosity == 'verbose':
            return f"specifically filtering for records where the condition is: {condition}"
        else:  # normal
            return f"{where_word} {condition}"
    
    def _render_group_by_clause(self, node):
        """Render GROUP BY clause."""
        group = node.args.get('group')
        if not group:
            return None
        
        expressions = group.expressions if hasattr(group, 'expressions') else [group]
        cols = [self._render_expression(expr) for expr in expressions]
        
        # Apply variations
        grouped_word = self._maybe_sql_keyword('grouped by')
        if grouped_word == 'GROUP BY':
            grouped_phrase = 'GROUP BY'
        else:
            grouped_phrase = self._choose_word('grouped by')
        
        if len(cols) == 1:
            return f"{grouped_phrase} {cols[0]}"
        else:
            return f"{grouped_phrase} {', '.join(cols)}"
    
    def _render_having_clause(self, node):
        """Render HAVING clause."""
        having = node.args.get('having')
        if not having:
            return None
        
        condition = self._render_expression(having.this)
        
        # Apply variations
        having_word = self._maybe_sql_keyword('having')
        if having_word == 'HAVING':
            having_phrase = 'HAVING'
        else:
            having_phrase = self._choose_word('having')
        
        return f"{having_phrase} {condition}"
    
    def _render_order_by_clause(self, node):
        """Render ORDER BY clause."""
        order = node.args.get('order')
        if not order:
            return None
        
        expressions = order.expressions if hasattr(order, 'expressions') else [order]
        order_parts = []
        for expr in expressions:
            if isinstance(expr, exp.Ordered):
                col = self._render_expression(expr.this)
                desc = expr.args.get('desc', False)
                direction = "descending" if desc else "ascending"
                order_parts.append(f"{col} {direction}")
            else:
                order_parts.append(self._render_expression(expr))
        
        # Apply variations
        ordered_word = self._maybe_sql_keyword('ordered by')
        if ordered_word == 'ORDER BY':
            ordered_phrase = 'ORDER BY'
        else:
            ordered_phrase = self._choose_word('ordered by')
        
        return f"{ordered_phrase} {', '.join(order_parts)}"
    
    def _render_limit_clause(self, node):
        """Render LIMIT clause."""
        limit = node.args.get('limit')
        if not limit:
            return None
        
        # LIMIT can be an Expression wrapping the actual value
        if isinstance(limit, exp.Limit):
            limit_val = self._render_expression(limit.expression)
        else:
            limit_val = self._render_expression(limit)
        
        # Apply variations
        limited_word = self._maybe_sql_keyword('limited to')
        if limited_word == 'LIMIT':
            return f"LIMIT {limit_val}"
        else:
            limited_phrase = self._choose_word('limited to')
            return f"{limited_phrase} {limit_val} results"
    
    # ========== INSERT Statement ==========
    
    def render_insert(self, node):
        """Render INSERT statement."""
        # node.this is an exp.Schema object for INSERT
        # We need to extract the table name from it
        schema_node = node.this
        if isinstance(schema_node, exp.Schema):
            # The table appears as the first expression in the schema
            if schema_node.this:
                table = self._render_expression(schema_node.this)
            else:
                table = "table"
        else:
            table = self._render_table(schema_node)
        
        # Get columns
        cols = node.args.get('columns', [])
        if cols:
            col_names = [self._render_expression(c) for c in cols]
            col_str = f" ({', '.join(col_names)})"
        else:
            col_str = ""
        
        # Get values
        expression = node.expression
        if isinstance(expression, exp.Values):
            value_tuples = expression.expressions
            if value_tuples:
                first_tuple = value_tuples[0]
                if isinstance(first_tuple, exp.Tuple):
                    values = [self._render_expression(v) for v in first_tuple.expressions]
                    value_str = f"values ({', '.join(values)})"
                else:
                    value_str = "values"
            else:
                value_str = "values"
        else:
            value_str = "values from expression"
        
        return f"Insert into {table}{col_str} the {value_str}."
    
    # ========== UPDATE Statement ==========
    
    def render_update(self, node):
        """Render UPDATE statement."""
        table = self._render_table(node.this)
        
        # Get SET assignments
        expressions = node.expressions
        assignments = []
        for expr in expressions:
            if isinstance(expr, exp.EQ):
                col = self._render_expression(expr.this)
                val = self._render_expression(expr.expression)
                assignments.append(f"{col} to {val}")
        
        assignment_str = ", ".join(assignments) if assignments else "columns"
        
        # Get WHERE clause
        where = node.args.get('where')
        if where:
            condition = self._render_expression(where.this)
            where_str = f" where {condition}"
        else:
            where_str = ""
        
        return f"Update {table} setting {assignment_str}{where_str}."
    
    # ========== DELETE Statement ==========
    
    def render_delete(self, node):
        """Render DELETE statement."""
        table = self._render_table(node.this)
        
        # Get WHERE clause
        where = node.args.get('where')
        if where:
            condition = self._render_expression(where.this)
            where_str = f" where {condition}"
        else:
            where_str = ""
        
        return f"Delete from {table}{where_str}."
    
    # ========== Helper Methods ==========
    
    def _render_table(self, table_expr):
        """Render table reference."""
        if isinstance(table_expr, exp.Table):
            name = table_expr.name
            alias = table_expr.alias
            if alias:
                return f"{name} (as {alias})"
            return name
        elif isinstance(table_expr, exp.Subquery):
            # Recursively render the inner query
            inner_query = table_expr.this
            if isinstance(inner_query, exp.Select):
                inner_nl = self.render_select(inner_query)
                # Remove trailing period from inner query
                inner_nl = inner_nl.rstrip('.')
                alias = table_expr.alias
                if alias:
                    return f"subquery (as {alias}) that: {inner_nl}"
                return f"subquery that: {inner_nl}"
            else:
                alias = table_expr.alias
                return f"subquery{f' (as {alias})' if alias else ''}"
        elif isinstance(table_expr, exp.Identifier):
            return str(table_expr.this)
        elif isinstance(table_expr, str):
            return table_expr
        else:
            # Fallback: try to extract table name from AST
            if hasattr(table_expr, 'name'):
                return table_expr.name
            return "table"
    
    def _render_join(self, join_node):
        """Render JOIN clause."""
        # Get join type
        side = join_node.args.get('side', '')
        join_type = f"{side} " if side else ""
        
        # Get table
        table = self._render_table(join_node.this)
        
        # Get ON condition
        on = join_node.args.get('on')
        if on:
            condition = self._render_expression(on)
            on_str = f" on {condition}"
        else:
            on_str = ""
        
        return f"{join_type}joined with {table}{on_str}"
    
    def _render_aggregate(self, agg_node):
        """Render aggregate function."""
        if isinstance(agg_node, exp.Count):
            if isinstance(agg_node.this, exp.Star):
                return "count of all rows"
            else:
                col = self._render_expression(agg_node.this)
                return f"count of {col}"
        elif isinstance(agg_node, exp.Sum):
            col = self._render_expression(agg_node.this)
            return f"sum of {col}"
        elif isinstance(agg_node, exp.Avg):
            col = self._render_expression(agg_node.this)
            return f"average of {col}"
        elif isinstance(agg_node, exp.Min):
            col = self._render_expression(agg_node.this)
            return f"minimum of {col}"
        elif isinstance(agg_node, exp.Max):
            col = self._render_expression(agg_node.this)
            return f"maximum of {col}"
        else:
            return "aggregate"
    
    def _render_expression(self, expr):
        """Render generic expression."""
        if isinstance(expr, exp.Column):
            table = expr.table
            name = expr.name
            if table:
                return f"{table}.{name}"
            return name
        
        elif isinstance(expr, exp.Literal):
            return str(expr.this)
        
        elif isinstance(expr, exp.Boolean):
            return str(expr.this).upper()
        
        elif isinstance(expr, exp.Anonymous):
            return f"{expr.this}()"
        
        # Aggregates (check before binary operations since aggregates can appear in comparisons)
        elif isinstance(expr, (exp.Count, exp.Sum, exp.Avg, exp.Min, exp.Max)):
            return self._render_aggregate(expr)
        
        # Table reference
        elif isinstance(expr, exp.Table):
            return self._render_table(expr)
        
        # Binary operations
        elif isinstance(expr, exp.EQ):
            left = self._render_expression(expr.this)
            right = self._render_expression(expr.expression)
            return f"{left} equals {right}"
        
        elif isinstance(expr, exp.NEQ):
            left = self._render_expression(expr.this)
            right = self._render_expression(expr.expression)
            return f"{left} not equals {right}"
        
        elif isinstance(expr, exp.GT):
            left = self._render_expression(expr.this)
            right = self._render_expression(expr.expression)
            return f"{left} greater than {right}"
        
        elif isinstance(expr, exp.GTE):
            left = self._render_expression(expr.this)
            right = self._render_expression(expr.expression)
            return f"{left} greater than or equal to {right}"
        
        elif isinstance(expr, exp.LT):
            left = self._render_expression(expr.this)
            right = self._render_expression(expr.expression)
            return f"{left} less than {right}"
        
        elif isinstance(expr, exp.LTE):
            left = self._render_expression(expr.this)
            right = self._render_expression(expr.expression)
            return f"{left} less than or equal to {right}"
        
        elif isinstance(expr, exp.Like):
            left = self._render_expression(expr.this)
            right = self._render_expression(expr.expression)
            return f"{left} like {right}"
        
        elif isinstance(expr, exp.In):
            left = self._render_expression(expr.this)
            
            # Check for subquery in 'query' attribute first
            query_subq = expr.args.get('query')
            if query_subq and isinstance(query_subq, exp.Subquery):
                inner_query = query_subq.this
                if isinstance(inner_query, exp.Select):
                    inner_nl = self.render_select(inner_query)
                    inner_nl = inner_nl.rstrip('.')
                    return f"{left} in (subquery that: {inner_nl})"
            
            # Get the IN list/subquery from expressions
            right_exprs = expr.expressions if hasattr(expr, 'expressions') else []
            if right_exprs:
                if isinstance(right_exprs[0], exp.Select):
                    # Recursively render the subquery
                    inner_nl = self.render_select(right_exprs[0])
                    # Remove trailing period
                    inner_nl = inner_nl.rstrip('.')
                    return f"{left} in (subquery that: {inner_nl})"
                else:
                    values = [self._render_expression(v) for v in right_exprs]
                    return f"{left} in ({', '.join(values)})"
            return f"{left} in (values)"
        
        elif isinstance(expr, exp.DateSub):
            # DATE_SUB(NOW(), INTERVAL X DAY)
            days = self._render_expression(expr.expression)
            unit = expr.args.get('unit')
            unit_str = self._render_expression(unit) if unit else "DAY"
            return f"date minus {days} {unit_str}"
        
        elif isinstance(expr, exp.Var):
            return str(expr.this)
        
        elif isinstance(expr, exp.Identifier):
            return str(expr.this)
        
        # Subquery
        elif isinstance(expr, exp.Select):
            return "subquery"
        
        # Fallback
        else:
            return f"expression"

    def generate_variations(self, ast, num_variations=3):
        """
        Generate vanilla prompt plus multiple perturbed variations.
        
        Args:
            ast: Parsed SQL AST
            num_variations: Number of perturbed variations to generate
        
        Returns:
            dict with 'vanilla' and 'variations' keys
        """
        import random
        
        # Generate vanilla version (no perturbations)
        vanilla_renderer = SQLToNLRenderer(
            use_variations=False,
            verbosity='normal',
            operator_style='words',
            add_fluff=False,
            code_switch_probability=0.0
        )
        vanilla_prompt = vanilla_renderer.render(ast)
        
        # Generate perturbed variations
        variations = []
        for _ in range(num_variations):
            # Randomize perturbation settings
            perturbed_renderer = SQLToNLRenderer(
                use_variations=random.choice([True, False]),
                verbosity=random.choice(['terse', 'normal', 'verbose']),
                operator_style=random.choice(['words', 'symbols', 'mixed']),
                add_fluff=random.choice([True, False]),
                code_switch_probability=random.uniform(0.0, 0.5)
            )
            variation_prompt = perturbed_renderer.render(ast)
            variations.append(variation_prompt)
        
        return {
            'vanilla': vanilla_prompt,
            'variations': variations
        }
