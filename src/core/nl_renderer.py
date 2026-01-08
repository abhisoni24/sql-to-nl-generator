"""
Syntax-Directed Translation (SDT) Framework for SQL to Natural Language
This module provides deterministic, template-based rendering of SQL ASTs to NL prompts.
"""

from enum import Enum, auto
from dataclasses import dataclass, field
import random
from typing import List, Dict, Optional, Set
from sqlglot import exp

class PerturbationType(Enum):
    """
    Enumeration of the 10 specific perturbation categories.
    """
    UNDER_SPECIFICATION = "under_specification"
    IMPLICIT_BUSINESS_LOGIC = "implicit_business_logic"
    SYNONYM_SUBSTITUTION = "synonym_substitution"
    INCOMPLETE_JOINS = "incomplete_joins"
    RELATIVE_TEMPORAL = "relative_temporal"
    AMBIGUOUS_PRONOUNS = "ambiguous_pronouns"
    VAGUE_AGGREGATION = "vague_aggregation"
    COLUMN_VARIATIONS = "column_variations"
    MISSING_WHERE_DETAILS = "missing_where_details"
    TYPOS = "typos"

@dataclass
class PerturbationConfig:
    """
    Configuration for perturbations (The 'Bit-Vector').
    Controls which perturbations are active and provides the seed for determinism.
    """
    active_perturbations: Set[PerturbationType] = field(default_factory=set)
    seed: int = 42

    def is_active(self, p_type: PerturbationType) -> bool:
        return p_type in self.active_perturbations

class SQLToNLRenderer:
    """Renders SQL AST nodes to natural language using deterministic templates."""
    
    def __init__(self, config: Optional[PerturbationConfig] = None):
        """
        Initialize renderer with perturbation configuration.
        
        Args:
            config: PerturbationConfig object controlling active perturbations and seed.
        """
        self.config = config or PerturbationConfig()
        
        # Synonym mappings for lexical variation (SYNONYM_SUBSTITUTION)
        self.synonyms = {
            'get': ['Get', 'Retrieve', 'Fetch', 'Select', 'Show', 'Find', 'Pull', 'Extract', 'Obtain', 'Display'],
            'where': ['where', 'filtering by', 'with condition', 'such that', 'that match', 'when', 'having condition'],
            'from': ['from', 'in', 'within', 'from table', 'out of', 'using'],
            'grouped by': ['grouped by', 'group by', 'organized by', 'categorized by', 'partitioned by', 'arranged by', 'split by'],
            'ordered by': ['ordered by', 'sorted by', 'arranged by', 'organized by', 'ranked by', 'sequenced by'],
            'limited to': ['limited to', 'with limit of', 'taking only', 'restricted to', 'top', 'capped at', 'max'],
            'having': ['having', 'with condition', 'where aggregate', 'filtered by', 'with filter'],
            'joined with': ['joined with', 'join', 'combined with', 'merged with', 'linked to', 'connected to'],
            'equals': ['equals', 'is', 'matches', '=', 'is equal to'],
            'not equals': ['not equals', 'is not', 'differs from', '!=', '<>', 'does not equal'],
            'greater than': ['greater than', 'more than', 'exceeds', 'above', '>', 'larger than'],
            'less than': ['less than', 'below', 'under', 'fewer than', '<', 'smaller than'],
            'greater than or equal to': ['greater than or equal to', 'at least', '>=', 'no less than', 'minimum of'],
            'less than or equal to': ['less than or equal to', 'at most', '<=', 'no more than', 'maximum of'],
            'like': ['like', 'matching pattern', 'similar to', 'matches', 'containing', 'with pattern'],
            'in': ['in', 'within', 'among', 'one of', 'part of', 'included in'],
        }
        
        # Aggregate description variations
        self.agg_variations = {
            'count': ['count of', 'number of', 'how many', 'total count of', 'tally of', 'quantity of'],
            'sum': ['sum of', 'total', 'add up', 'combined', 'total of', 'aggregate of'],
            'avg': ['average of', 'mean', 'avg', 'average value of', 'mean value of', 'typical'],
            'min': ['minimum of', 'smallest', 'lowest', 'min', 'minimum value of', 'least'],
            'max': ['maximum of', 'largest', 'highest', 'max', 'maximum value of', 'greatest']
        }
        
        # Pronoun maps (AMBIGUOUS_PRONOUNS)
        self.pronouns = {
            'table': ['it', 'that table', 'them', 'those'],
            'column': ['that field', 'it', 'the column', 'that value'],
            'id': ['that one', 'it', 'that ID', 'the specified one']
        }

        # Typo patterns (TYPOS)
        # Deterministic typo injection
        self.typo_patterns = {
            'swap': lambda w, rng: w if len(w) < 2 else w[:max(0, rng.randint(0, len(w)-2))] + w[min(len(w)-1, rng.randint(0, len(w)-2) + 1)] + w[min(len(w)-1, rng.randint(0, len(w)-2))] + w[min(len(w), rng.randint(0, len(w)-2) + 2):],
            'miss': lambda w, rng: w if len(w) < 3 else w[:rng.randint(0, len(w)-1)] + w[rng.randint(0, len(w)-1)+1:],
        }

    def _get_rng(self, extra_seed: str = "") -> random.Random:
        """Get a deterministic RNG based on config seed and context."""
        seed_str = f"{self.config.seed}_{extra_seed}"
        return random.Random(seed_str)

    def _choose_word(self, canonical_form: str, context_seed: str) -> str:
        """Select a synonym based on variation mode. Deterministic."""
        if not self.config.is_active(PerturbationType.SYNONYM_SUBSTITUTION):
            # Return default (first option for most)
            options = self.synonyms.get(canonical_form, [canonical_form])
            return options[0] if options else canonical_form
        
        rng = self._get_rng(f"synonym_{canonical_form}_{context_seed}")
        return rng.choice(self.synonyms.get(canonical_form, [canonical_form]))

    def render(self, ast) -> str:
        """
        Main entry point: render any SQL statement to NL.
        The process is deterministic based on self.config.seed.
        """
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
        
        # TYPOS: Applied at the end
        if self.config.is_active(PerturbationType.TYPOS):
            base_nl = self._apply_typos(base_nl)

        return base_nl

    # For later
    # Need to replace this with collecting the valid perturbations for the current nl_prompt and make a hybrid prompt
    def render_randomly(self, ast, seed=None) -> str:
        """
        Render the AST with random valid perturbation settings.
        Used for generating 'nl_prompt_variations' payload.
        """
        # Pick 1-3 random perturbations
        rng = random.Random(seed)
        all_types = list(PerturbationType)
        # Select a random subset
        num_active = rng.randint(0, 3) 
        active = set(rng.sample(all_types, num_active))
        
        # Create temp config
        temp_config = PerturbationConfig(active_perturbations=active, seed=rng.randint(0, 10000))
        temp_renderer = SQLToNLRenderer(temp_config)
        return temp_renderer.render(ast)

    def is_applicable(self, ast: exp.Expression, p_type: PerturbationType) -> bool:
        """
        Check if a specifically perturbation type is applicable to the given AST.
        """
        if p_type == PerturbationType.TYPOS:
            return True
        elif p_type == PerturbationType.SYNONYM_SUBSTITUTION:
            return True
        elif p_type == PerturbationType.UNDER_SPECIFICATION:
            # Applicable if there are tables or columns
            return bool(list(ast.find_all(exp.Table)) or list(ast.find_all(exp.Column)))
        elif p_type == PerturbationType.IMPLICIT_BUSINESS_LOGIC:
            # Applicable if there is a WHERE clause
            return bool(ast.find(exp.Where))
        elif p_type == PerturbationType.INCOMPLETE_JOINS:
            # Applicable if there are JOINs
            return bool(ast.find(exp.Join))
        elif p_type == PerturbationType.RELATIVE_TEMPORAL:
            # Applicable if there are date/time literals or types (simplified check)
            # Check for date literals or known functions
            # This is a heuristic.
            for node in ast.walk():
                if isinstance(node, exp.Literal) and isinstance(node.this, str):
                    if '-' in node.this and any(c.isdigit() for c in node.this): # Weak date check
                        return True
                if isinstance(node, (exp.CurrentDate, exp.CurrentTime, exp.CurrentTimestamp, exp.DateSub, exp.DateAdd)):
                    return True
            return False
        elif p_type == PerturbationType.AMBIGUOUS_PRONOUNS:
            return bool(list(ast.find_all(exp.Table)) or list(ast.find_all(exp.Column)))
        elif p_type == PerturbationType.VAGUE_AGGREGATION:
            # Applicable if there are aggregates or GROUP BY
            if ast.find(exp.Group): return True
            if any(isinstance(n, (exp.Count, exp.Sum, exp.Avg, exp.Min, exp.Max)) for n in ast.walk()): return True
            return False
        elif p_type == PerturbationType.COLUMN_VARIATIONS:
            return bool(list(ast.find_all(exp.Column)))
        elif p_type == PerturbationType.MISSING_WHERE_DETAILS:
             return bool(ast.find(exp.Where))
             
        return True

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
            
        full_sentence = " ".join(parts)
        if not full_sentence.endswith('.'):
            full_sentence += "."
            
        return full_sentence
    
    def _render_select_clause(self, node):
        """Render SELECT column list."""
        expressions = node.expressions
        get_word = self._choose_word('get', 'select_clause_verb')
        
        if not expressions:
            return f"{get_word} all columns"
        
        col_descriptions = []
        for i, expr in enumerate(expressions):
            if isinstance(expr, exp.Star):
                col_descriptions.append("all columns")
            elif isinstance(expr, (exp.Count, exp.Sum, exp.Avg, exp.Min, exp.Max)):
                col_descriptions.append(self._render_aggregate(expr, f"expr_{i}"))
            else:
                col_descriptions.append(self._render_expression(expr, f"expr_{i}"))
        
        return f"{get_word} {', '.join(col_descriptions)}"
    
    def _render_from_clause(self, node):
        """Render FROM clause."""
        from_node = node.args.get('from_')
        if not from_node:
            return None
            
        table_expr = from_node.this
        table_name = self._render_table(table_expr, "from_table")
        
        from_word = self._choose_word('from', 'from_clause')
        parts = [f"{from_word} {table_name}"]
        
        joins = node.args.get('joins', [])
        for i, join in enumerate(joins):
             parts.append(self._render_join(join, f"join_{i}"))
             
        return " ".join(parts)

    def _render_where_clause(self, node):
        """Render WHERE clause."""
        where_node = node.args.get('where')
        if not where_node:
            return None
            
        condition = self._render_expression(where_node.this, "where_condition")
        where_word = self._choose_word('where', 'where_clause')
        return f"{where_word} {condition}"

    def _render_group_by_clause(self, node):
        group = node.args.get('group')
        if not group:
            return None
        
        expressions = group.expressions if hasattr(group, 'expressions') else [group]
        cols = [self._render_expression(expr, f"group_{i}") for i, expr in enumerate(expressions)]
        
        grouped_word = self._choose_word('grouped by', 'group_clause')
        
        # VAGUE_AGGREGATION: "Replace GROUP BY with 'by', 'for each', 'per'"
        if self.config.is_active(PerturbationType.VAGUE_AGGREGATION):
           rng = self._get_rng("vague_group")
           grouped_word = rng.choice(['by', 'for each', 'per'])

        return f"{grouped_word} {', '.join(cols)}"

    def _render_having_clause(self, node):
        having = node.args.get('having')
        if not having:
            return None
        condition = self._render_expression(having.this, "having_condition")
        having_word = self._choose_word('having', 'having_clause')
        return f"{having_word} {condition}"

    def _render_order_by_clause(self, node):
        order = node.args.get('order')
        if not order:
            return None
            
        expressions = order.expressions if hasattr(order, 'expressions') else [order]
        order_parts = []
        for i, expr in enumerate(expressions):
            if isinstance(expr, exp.Ordered):
                col = self._render_expression(expr.this, f"order_{i}")
                desc = expr.args.get('desc', False)
                direction = "descending" if desc else "ascending"
                order_parts.append(f"{col} {direction}")
            else:
                order_parts.append(self._render_expression(expr, f"order_{i}"))
                
        ordered_word = self._choose_word('ordered by', 'order_clause')
        return f"{ordered_word} {', '.join(order_parts)}"

    def _render_limit_clause(self, node):
        limit = node.args.get('limit')
        if not limit:
            return None
            
        if isinstance(limit, exp.Limit):
            limit_val = self._render_expression(limit.expression, "limit_val")
        else:
            limit_val = self._render_expression(limit, "limit_val")
            
        limited_word = self._choose_word('limited to', 'limit_clause')
        return f"{limited_word} {limit_val} results"

    # ========== Expression Rendering (The meat of perturbations) ==========

    def _render_table(self, table_expr, seed_context):
        """Render table reference with perturbations."""
        rng = self._get_rng(seed_context)
        
        name = "table"
        alias = ""
        
        if isinstance(table_expr, exp.Table):
            name = table_expr.name
            alias = table_expr.alias
        elif isinstance(table_expr, exp.Identifier):
            name = str(table_expr.this)
        elif isinstance(table_expr, str):
            name = table_expr
            
        # UNDER_SPECIFICATION
        if self.config.is_active(PerturbationType.UNDER_SPECIFICATION):
             if isinstance(table_expr, (exp.Table, exp.Identifier, str)):
                 return "the appropriate table"

        # AMBIGUOUS_PRONOUNS
        if self.config.is_active(PerturbationType.AMBIGUOUS_PRONOUNS):
            return rng.choice(self.pronouns['table'])
            
        res = name
        if alias and not self.config.is_active(PerturbationType.UNDER_SPECIFICATION): 
            res += f" (as {alias})"
        
        return res

    def _render_column(self, col_expr, seed_context):
        """Render column reference with perturbations."""
        rng = self._get_rng(seed_context)
        
        if isinstance(col_expr, exp.Column):
            name = col_expr.name
            table = col_expr.table
        else:
            name = str(col_expr) # fallback
            table = None
            
        # UNDER_SPECIFICATION
        if self.config.is_active(PerturbationType.UNDER_SPECIFICATION):
            table = None
            
        # COLUMN_VARIATIONS
        if self.config.is_active(PerturbationType.COLUMN_VARIATIONS):
            # "Convert snake_case to camelCase" with proper spacing
            if "_" in name:
                parts = name.split('_')
                if rng.choice([True, False]):
                    name = parts[0] + ''.join(x.title() for x in parts[1:])
                # Don't introduce spacing errors - remove the "name = ' '.join(parts)" option
        
        # AMBIGUOUS_PRONOUNS - Only in WHERE/HAVING clauses, never in SELECT list
        if self.config.is_active(PerturbationType.AMBIGUOUS_PRONOUNS):
            # Only apply in WHERE/HAVING contexts, not in SELECT/GROUP/ORDER
            if any(ctx in seed_context.lower() for ctx in ['where', 'having']) and rng.random() < 0.4:
                return rng.choice(self.pronouns['column'])
            
        if table:
            return f"{table}.{name}"
        return name

    def _render_expression(self, expr, seed_context):
        """Render generic expression with recursive perturbations."""
        
        if isinstance(expr, exp.Column):
            return self._render_column(expr, seed_context)
            
        elif isinstance(expr, exp.Literal):
            val = str(expr.this)
            # RELATIVE_TEMPORAL check
            if self.config.is_active(PerturbationType.RELATIVE_TEMPORAL):
                # Heuristic: simplistic date check
                if len(val) >= 10 and val[0:4].isdigit() and '-' in val:
                    rng = self._get_rng(seed_context + "_temporal")
                    return rng.choice(["recently", "last month", "yesterday", "this week"])
            
            # AMBIGUOUS_PRONOUNS for values - only in WHERE contexts
            if self.config.is_active(PerturbationType.AMBIGUOUS_PRONOUNS):
                 if val.isdigit() and 'where' in seed_context.lower():
                     rng = self._get_rng(seed_context + "_ambig_val")
                     if rng.random() < 0.3:
                         return rng.choice(self.pronouns['id'])

            return val
            
        elif isinstance(expr, exp.Boolean):
             return str(expr.this).upper()

        elif isinstance(expr, (exp.Count, exp.Sum, exp.Avg, exp.Min, exp.Max)):
            return self._render_aggregate(expr, seed_context)

        elif isinstance(expr, (exp.EQ, exp.NEQ, exp.GT, exp.GTE, exp.LT, exp.LTE, exp.Like)):
             return self._render_binary_op(expr, seed_context)

        elif isinstance(expr, exp.In):
             left = self._render_expression(expr.this, seed_context + "_left")
             
             # Check for subquery in 'query' field (IN with SELECT)
             subquery = expr.args.get('query')
             if subquery and isinstance(subquery, exp.Subquery):
                 # Render the subquery SELECT statement
                 inner_select = subquery.this
                 if isinstance(inner_select, exp.Select):
                     inner = self.render_select(inner_select)
                     inner = inner.rstrip('.')
                     return f"{left} in ({inner})"
                 else:
                     # Fallback if not a Select
                     return f"{left} in (subquery)"
             
             # Handle IN list (multiple values)
             right_exprs = expr.expressions if hasattr(expr, 'expressions') else []
             if right_exprs:
                 vals = [self._render_expression(v, seed_context + f"_in_{i}") for i,v in enumerate(right_exprs)]
                 return f"{left} in ({', '.join(vals)})"
             
             # Empty IN clause (shouldn't happen but handle gracefully)
             return f"{left} in ()"
        
        # Function calls (DATE_SUB, NOW, etc.)
        elif isinstance(expr, exp.Anonymous):
            func_name = expr.this if isinstance(expr.this, str) else str(expr.this)
            args = expr.expressions if hasattr(expr, 'expressions') else []
            arg_strs = [self._render_expression(a, f"{seed_context}_arg_{i}") for i, a in enumerate(args)]
            return f"{func_name}({', '.join(arg_strs)})"
        
        elif isinstance(expr, (exp.CurrentDate, exp.CurrentTime, exp.CurrentTimestamp)):
            return "NOW()"
        
        elif isinstance(expr, exp.DateSub):
            # DATE_SUB(date, INTERVAL n unit)
            date_expr = self._render_expression(expr.this, seed_context + "_date")
            interval = expr.expression
            if isinstance(interval, exp.Interval):
                unit = interval.unit.this if hasattr(interval.unit, 'this') else str(interval.unit)
                value = self._render_expression(interval.this, seed_context + "_interval_val")
                return f"{date_expr} minus {value} {unit.lower()}s"
            return f"date subtraction from {date_expr}"
        
        elif isinstance(expr, exp.DateAdd):
            date_expr = self._render_expression(expr.this, seed_context + "_date")
            interval = expr.expression
            if isinstance(interval, exp.Interval):
                unit = interval.unit.this if hasattr(interval.unit, 'this') else str(interval.unit)
                value = self._render_expression(interval.this, seed_context + "_interval_val")
                return f"{date_expr} plus {value} {unit.lower()}s"
            return f"date addition to {date_expr}"
        
        elif isinstance(expr, exp.Interval):
            value = self._render_expression(expr.this, seed_context + "_val")
            unit = expr.unit.this if hasattr(expr.unit, 'this') else str(expr.unit)
            return f"{value} {unit.lower()}s"

        return "expression"

    def _render_binary_op(self, expr, seed_context):
        left = self._render_expression(expr.this, seed_context + "_left")
        right = self._render_expression(expr.expression, seed_context + "_right")
        
        op_map = {
            exp.EQ: 'equals', exp.NEQ: 'not equals', 
            exp.GT: 'greater than', exp.GTE: 'greater than or equal to',
            exp.LT: 'less than', exp.LTE: 'less than or equal to',
            exp.Like: 'like'
        }
        op_canonical = op_map.get(type(expr), 'op')
        
        # IMPLICIT_BUSINESS_LOGIC - ONLY apply in WHERE clauses, not JOINs
        if self.config.is_active(PerturbationType.IMPLICIT_BUSINESS_LOGIC):
             if 'where' in seed_context.lower() and 'join' not in seed_context.lower():
                 rng = self._get_rng(seed_context + "_biz")
                 if type(expr) == exp.EQ:
                     return f"{left} is {rng.choice(['valid', 'active'])}"
        
        # MISSING_WHERE_DETAILS - Replace literal values with subjective terms
        if self.config.is_active(PerturbationType.MISSING_WHERE_DETAILS):
             if 'where' in seed_context.lower():
                 rng = self._get_rng(seed_context + "_where_miss")
                 if type(expr) in [exp.GT, exp.GTE]:
                     return f"{left} {self._choose_word(op_canonical, seed_context)} the high threshold"
                 if type(expr) in [exp.LT, exp.LTE]:
                     return f"{left} {self._choose_word(op_canonical, seed_context)} the low threshold"
                 if type(expr) == exp.EQ:
                     return f"{left} is the relevant one"
                 if type(expr) == exp.Like:
                     return f"{left} matches the pattern"

        op_str = self._choose_word(op_canonical, seed_context + "_op")
        return f"{left} {op_str} {right}"

    def _render_aggregate(self, agg_node, seed_context):
        """Render aggregate function."""
        agg_type_map = {
            exp.Count: 'count', exp.Sum: 'sum', exp.Avg: 'avg',
            exp.Min: 'min', exp.Max: 'max'
        }
        agg_type = agg_type_map.get(type(agg_node), 'count')
        
        rng = self._get_rng(seed_context + "_agg_var")
        options = self.agg_variations.get(agg_type, [f"{agg_type} of"])
        
        # VAGUE_AGGREGATION - use vague terms for aggregate functions
        if self.config.is_active(PerturbationType.VAGUE_AGGREGATION):
            vague_maps = {
                'count': ['number', 'total', 'how many'],
                'sum': ['total', 'combined amount'],
                'avg': ['average', 'typical value'],
                'min': ['smallest', 'minimum'],
                'max': ['largest', 'maximum']
            }
            template = rng.choice(vague_maps.get(agg_type, ['value']))
        elif not self.config.is_active(PerturbationType.SYNONYM_SUBSTITUTION):
             template = options[0]
        else:
             template = rng.choice(options)
             
        if isinstance(agg_node.this, exp.Star):
             return f"{template} of all rows" if 'of' not in template else f"{template} all rows"
        else:
             col_str = self._render_expression(agg_node.this, seed_context + "_inner")
             return f"{template} of {col_str}" if 'of' not in template else f"{template} {col_str}"

    def _render_join(self, join_node, seed_context):
        # INCOMPLETE_JOINS
        if self.config.is_active(PerturbationType.INCOMPLETE_JOINS):
            rng = self._get_rng(seed_context + "_inc_join")
            connector = rng.choice(["with", "and their", "along with"])
            table = self._render_table(join_node.this, seed_context + "_join_table")
            return f"{connector} {table}"

        side = join_node.args.get('side', '')
        join_type = f"{side} " if side else ""
        table = self._render_table(join_node.this, seed_context + "_join_table")
        
        on = join_node.args.get('on')
        if on:
            condition = self._render_expression(on, seed_context + "_on")
            on_str = f" on {condition}"
        else:
            on_str = ""
            
        join_word = self._choose_word('joined with', seed_context + "_join_kw")
        return f"{join_type}{join_word} {table}{on_str}"

    # ========== Other Statements ==========
    def render_insert(self, node):
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
        
    def render_update(self, node):
        """Render UPDATE with SET and WHERE clauses."""
        table = self._render_table(node.this, "update_table")
        parts = [f"Update {table}"]
        
        # SET clause
        expressions = node.expressions
        if expressions:
            set_parts = []
            for i, expr in enumerate(expressions):
                if isinstance(expr, exp.EQ):
                    col = self._render_expression(expr.this, f"update_col_{i}")
                    val = self._render_expression(expr.expression, f"update_val_{i}")
                    set_parts.append(f"{col} = {val}")
            if set_parts:
                parts.append(f"set {', '.join(set_parts)}")
        
        # WHERE clause  
        where_node = node.args.get('where')
        if where_node:
            condition = self._render_expression(where_node.this, "update_where")
            where_word = self._choose_word('where', 'update_where_clause')
            parts.append(f"{where_word} {condition}")
        
        return " ".join(parts) + "."
        
    def render_delete(self, node):
        """Render DELETE with WHERE clause."""
        table = self._render_table(node.this, "delete_table")
        parts = [f"Delete from {table}"]
        
        # WHERE clause
        where_node = node.args.get('where')
        if where_node:
            condition = self._render_expression(where_node.this, "delete_where")
            where_word = self._choose_word('where', 'delete_where_clause')
            parts.append(f"{where_word} {condition}")
        
        return " ".join(parts) + "."

    # ========== Post-processing ==========
    def _apply_typos(self, text: str) -> str:
        """Inject realistic typos deterministically - sparse and natural."""
        rng = self._get_rng("typos")
        words = text.split()
        if not words: return text
        
        # Reduce density: max 1-2 typos total, with lower probability
        if len(words) < 5:
            num_typos = 1 if rng.random() < 0.7 else 0
        else:
            num_typos = rng.choice([1, 2]) if rng.random() < 0.8 else 0
        
        if num_typos == 0:
            return text
            
        # Protect SQL keywords
        protected = {'select', 'from', 'where', 'insert', 'update', 'delete', 'join', 'group', 'order', 'limit'}
        
        # Find typo-able indices (not protected words)
        typoable_indices = [i for i, w in enumerate(words) if w.lower() not in protected and len(w) > 3]
        
        if not typoable_indices:
            return text
            
        indices = rng.sample(typoable_indices, min(num_typos, len(typoable_indices)))
        
        for idx in indices:
            word = words[idx]
            # Improved typo patterns
            pattern_choice = rng.random()
            if pattern_choice < 0.5:  # Adjacent key swap
                if len(word) > 2:
                    pos = rng.randint(0, len(word)-2)
                    word = word[:pos] + word[pos+1] + word[pos] + word[pos+2:]
            elif pattern_choice < 0.8:  # Missing letter
                if len(word) > 3:
                    pos = rng.randint(1, len(word)-1)
                    word = word[:pos] + word[pos+1:]
            else:  # Double letter
                pos = rng.randint(0, len(word)-1)
                word = word[:pos] + word[pos] + word[pos:]
            
            words[idx] = word
            
        return " ".join(words)
