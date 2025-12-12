import random
from sqlglot import exp
from schema import SCHEMA, FOREIGN_KEYS, NUMERIC_TYPES, TEXT_TYPES, DATE_TYPES, BOOLEAN_TYPES

class SQLQueryGenerator:
    def __init__(self, schema, foreign_keys):
        self.schema = schema
        self.foreign_keys = foreign_keys
        self.queries = []

    def _get_column_type(self, table, column):
        return self.schema[table].get(column)

    def generate_select(self, table, use_aggregate=False, group_by_cols=None, alias=None):
        table_alias = alias if alias else table
        columns = list(self.schema[table].keys())
        
        if use_aggregate:
            # If grouping, we must select group_by columns + aggregates
            select_exprs = []
            if group_by_cols:
                for col in group_by_cols:
                    # Handle if col is already an expression or just a name
                    if isinstance(col, exp.Expression):
                         select_exprs.append(col)
                    else:
                         select_exprs.append(exp.column(col, table=table_alias))
            
            # Add an aggregate
            agg_type = random.choice(['COUNT', 'SUM', 'AVG', 'MIN', 'MAX'])
            agg_col = random.choice(columns)
            
            if agg_type == 'COUNT':
                if random.random() < 0.5:
                    select_exprs.append(exp.Count(this=exp.Star()).as_("count_all"))
                else:
                    select_exprs.append(exp.Count(this=exp.column(agg_col, table=table_alias)).as_(f"count_{agg_col}"))
            elif self._get_column_type(table, agg_col) in NUMERIC_TYPES:
                 # Only sum/avg numeric types
                 if agg_type == 'SUM':
                     select_exprs.append(exp.Sum(this=exp.column(agg_col, table=table_alias)).as_(f"sum_{agg_col}"))
                 elif agg_type == 'AVG':
                     select_exprs.append(exp.Avg(this=exp.column(agg_col, table=table_alias)).as_(f"avg_{agg_col}"))
                 elif agg_type == 'MIN':
                     select_exprs.append(exp.Min(this=exp.column(agg_col, table=table_alias)).as_(f"min_{agg_col}"))
                 elif agg_type == 'MAX':
                     select_exprs.append(exp.Max(this=exp.column(agg_col, table=table_alias)).as_(f"max_{agg_col}"))
            else:
                # Fallback to count for non-numeric
                select_exprs.append(exp.Count(this=exp.Star()).as_("count_all"))
                
            return select_exprs
        else:
            # Simple select
            if random.random() < 0.3:
                return [exp.Star()]
            else:
                num_cols = random.randint(1, min(4, len(columns)))
                selected_cols = random.sample(columns, num_cols)
                return [exp.column(col, table=table_alias) for col in selected_cols]

    def generate_where(self, table, alias=None):
        table_alias = alias if alias else table
        columns = list(self.schema[table].keys())
        col_name = random.choice(columns)
        col_type = self._get_column_type(table, col_name)
        col_expr = exp.column(col_name, table=table_alias)
        
        if col_type in NUMERIC_TYPES:
            op = random.choice(['=', '!=', '>', '<', '>=', '<='])
            val = random.randint(0, 1000)
            return self._create_binary_op(op, col_expr, exp.Literal.number(val))
        elif col_type in TEXT_TYPES:
            op = random.choice(['=', '!=', 'LIKE'])
            if op == 'LIKE':
                val = random.choice(['%a%', 'b%', '%c'])
                return exp.Like(this=col_expr, expression=exp.Literal.string(val))
            else:
                val = random.choice(['test', 'user', 'admin'])
                return self._create_binary_op(op, col_expr, exp.Literal.string(val))
        elif col_type in DATE_TYPES:
            op = random.choice(['>', '<', '>=', '<='])
            # Date arithmetic: NOW() - INTERVAL X DAY
            now = exp.Anonymous(this='NOW')
            days = random.randint(1, 30)
            # Use DateSub for cleaner SQL: DATE_SUB(NOW(), INTERVAL X DAY)
            date_expr = exp.DateSub(this=now, expression=exp.Literal.number(days), unit=exp.Var(this='DAY'))
            return self._create_binary_op(op, col_expr, date_expr)
        elif col_type in BOOLEAN_TYPES:
             val = random.choice([True, False])
             return exp.EQ(this=col_expr, expression=exp.Boolean(this=val))
        
        return None

    def _create_binary_op(self, op, left, right):
        if op == '=': return exp.EQ(this=left, expression=right)
        if op == '!=': return exp.NEQ(this=left, expression=right)
        if op == '>': return exp.GT(this=left, expression=right)
        if op == '<': return exp.LT(this=left, expression=right)
        if op == '>=': return exp.GTE(this=left, expression=right)
        if op == '<=': return exp.LTE(this=left, expression=right)
        return exp.EQ(this=left, expression=right)

    def generate_insert(self, table):
        columns = list(self.schema[table].keys())
        # Filter out 'id' if it's an auto-increment primary key (assuming 'id' is always PK)
        columns = [c for c in columns if c != 'id']
        
        values = []
        for col in columns:
            col_type = self._get_column_type(table, col)
            if col_type in NUMERIC_TYPES:
                values.append(exp.Literal.number(random.randint(1, 1000)))
            elif col_type in TEXT_TYPES:
                if 'email' in col:
                    values.append(exp.Literal.string(f"user{random.randint(1,1000)}@example.com"))
                elif 'username' in col:
                    values.append(exp.Literal.string(f"user{random.randint(1,1000)}"))
                else:
                    values.append(exp.Literal.string(f"Sample text {random.randint(1,100)}"))
            elif col_type in DATE_TYPES:
                values.append(exp.Anonymous(this='NOW'))
            elif col_type in BOOLEAN_TYPES:
                values.append(exp.Boolean(this=random.choice([True, False])))
            else:
                values.append(exp.Literal.string("val"))
                
        return exp.insert(
            exp.Values(expressions=[exp.Tuple(expressions=values)]),
            table,
            columns=[exp.Identifier(this=c, quoted=False) for c in columns]
        )

    def generate_update(self, table):
        columns = list(self.schema[table].keys())
        # Filter out 'id'
        columns = [c for c in columns if c != 'id']
        col_to_update = random.choice(columns)
        col_type = self._get_column_type(table, col_to_update)
        
        if col_type in NUMERIC_TYPES:
            val = exp.Literal.number(random.randint(1, 1000))
        elif col_type in TEXT_TYPES:
            val = exp.Literal.string(f"Updated text {random.randint(1,100)}")
        elif col_type in DATE_TYPES:
            val = exp.Anonymous(this='NOW')
        elif col_type in BOOLEAN_TYPES:
            val = exp.Boolean(this=random.choice([True, False]))
        else:
            val = exp.Literal.string("val")
            
        update_expr = exp.update(table, {col_to_update: val})
        
        # Add WHERE clause
        where = self.generate_where(table)
        if where:
            update_expr = update_expr.where(where)
            
        return update_expr

    def generate_delete(self, table):
        delete_expr = exp.delete(table)
        
        # Add WHERE clause
        where = self.generate_where(table)
        if where:
            delete_expr = delete_expr.where(where)
            
        return delete_expr

    def generate_join(self, current_table, current_alias, available_tables):
        # Find potential joins
        candidates = []
        for (t1, t2), (k1, k2) in self.foreign_keys.items():
            if t1 == current_table and t2 not in available_tables: # Avoid joining same table for simplicity in this level
                candidates.append((t2, k1, k2))
        
        if not candidates:
            return None
            
        target_table, left_key, right_key = random.choice(candidates)
        target_alias = f"{target_table[0]}{random.randint(1,9)}"
        
        join_condition = exp.EQ(
            this=exp.column(left_key, table=current_alias),
            expression=exp.column(right_key, table=target_alias)
        )
        
        return target_table, target_alias, join_condition

    def generate_query(self):
        root_table = random.choice(list(self.schema.keys()))
        root_alias = f"{root_table[0]}1"
        
        complexity = random.choices(
            ['simple', 'join', 'aggregate', 'advanced', 'insert', 'update', 'delete'],
            weights=[0.35, 0.25, 0.15, 0.05, 0.1, 0.05, 0.05]
        )[0]
        
        if complexity == 'insert':
            return self.generate_insert(root_table), complexity
        elif complexity == 'update':
            return self.generate_update(root_table), complexity
        elif complexity == 'delete':
            return self.generate_delete(root_table), complexity
            
        query = exp.select()
        query = query.from_(exp.to_table(root_table).as_(root_alias))
        
        if complexity == 'simple':
            selects = self.generate_select(root_table, alias=root_alias)
            for s in selects: query = query.select(s, copy=False)
            
            if random.random() < 0.5:
                where = self.generate_where(root_table, alias=root_alias)
                if where: query = query.where(where)
                
            if random.random() < 0.3:
                 cols = list(self.schema[root_table].keys())
                 query = query.order_by(exp.column(random.choice(cols), table=root_alias), desc=random.choice([True, False]))
                 
            if random.random() < 0.3:
                query = query.limit(random.randint(1, 100))

        elif complexity == 'join':
            # Try to add a join
            join_info = self.generate_join(root_table, root_alias, [])
            if join_info:
                target_table, target_alias, on_clause = join_info
                join_kind = random.choice(["INNER", "LEFT"])
                query = query.join(exp.to_table(target_table).as_(target_alias), on=on_clause, join_type=join_kind)
                
                # Select from both
                s1 = self.generate_select(root_table, alias=root_alias)
                s2 = self.generate_select(target_table, alias=target_alias)
                # Flatten and pick a few
                all_selects = s1 + s2
                final_selects = random.sample(all_selects, min(len(all_selects), 4))
                for s in final_selects: query = query.select(s, copy=False)
                
                if random.random() < 0.5:
                    where = self.generate_where(target_table, alias=target_alias)
                    if where: query = query.where(where)
            else:
                # Fallback to simple if no join possible
                selects = self.generate_select(root_table, alias=root_alias)
                for s in selects: query = query.select(s, copy=False)

        elif complexity == 'aggregate':
            # Group by 1 column
            cols = list(self.schema[root_table].keys())
            group_col = random.choice(cols)
            
            selects = self.generate_select(root_table, use_aggregate=True, group_by_cols=[group_col], alias=root_alias)
            for s in selects: query = query.select(s, copy=False)
            
            query = query.group_by(exp.column(group_col, table=root_alias))
            
            if random.random() < 0.4:
                # Having count > 5
                query = query.having(exp.GT(this=exp.Count(this=exp.Star()), expression=exp.Literal.number(5)))

        elif complexity == 'advanced':
            subtype = random.choice(['subquery_where', 'subquery_from', 'self_join'])
            
            if subtype == 'subquery_where':
                # Subquery in WHERE: WHERE col IN (SELECT ...)
                selects = self.generate_select(root_table, alias=root_alias)
                for s in selects: query = query.select(s, copy=False)
                
                # Find a foreign key to filter on
                candidates = []
                for (t1, t2), (k1, k2) in self.foreign_keys.items():
                    if t1 == root_table:
                        candidates.append((t2, k1, k2))
                
                if candidates:
                    target_table, left_key, right_key = random.choice(candidates)
                    # Create a meaningful subquery
                    sub_alias = f"sub_{target_table[0]}"
                    subquery = exp.select(exp.column(right_key, table=sub_alias)).from_(exp.to_table(target_table).as_(sub_alias))
                    
                    # Add a filter to the subquery to make it interesting
                    sub_where = self.generate_where(target_table, alias=sub_alias)
                    if sub_where:
                        subquery = subquery.where(sub_where)
                    
                    query = query.where(exp.In(this=exp.column(left_key, table=root_alias), expressions=[subquery]))
                else:
                     # Fallback
                     query = query.where(self.generate_where(root_table, alias=root_alias))

            elif subtype == 'subquery_from':
                # Subquery in FROM: FROM (SELECT ...) AS sub
                # 1. Generate inner query
                inner_alias = f"inner_{root_table}"
                inner_query = exp.select("*").from_(exp.to_table(root_table).as_(inner_alias))
                inner_where = self.generate_where(root_table, alias=inner_alias)
                if inner_where:
                    inner_query = inner_query.where(inner_where)
                
                # 2. Wrap in outer query
                outer_alias = "derived_table"
                query = exp.select("*").from_(inner_query.subquery(alias=outer_alias))
                
                # Add a filter on the outer query if possible
                if random.random() < 0.5:
                    # Pick a column from root_table (which is in * of derived table)
                    cols = list(self.schema[root_table].keys())
                    col_name = random.choice(cols)
                    # We need to manually construct the where because generate_where expects a table name for schema lookup
                    # We can reuse generate_where but pass root_table and outer_alias
                    outer_where = self.generate_where(root_table, alias=outer_alias)
                    if outer_where:
                        query = query.where(outer_where)

            elif subtype == 'self_join':
                # Self-join on 'follows' table
                # Ensure we start with 'follows' or switch to it
                if root_table != 'follows':
                    root_table = 'follows'
                    root_alias = 'f1'
                    query = exp.select().from_(exp.to_table(root_table).as_(root_alias))
                
                # Join f1.followee_id = f2.follower_id (Friend of Friend)
                target_alias = 'f2'
                
                # Select distinct followers from f1 and followees from f2
                query = query.select(
                    exp.column('follower_id', table=root_alias).as_('user'),
                    exp.column('followee_id', table=target_alias).as_('friend_of_friend')
                )
                
                join_cond = exp.EQ(
                    this=exp.column('followee_id', table=root_alias),
                    expression=exp.column('follower_id', table=target_alias)
                )
                
                query = query.join(exp.to_table('follows').as_(target_alias), on=join_cond)
                
                # Filter to avoid loops (user != friend_of_friend)
                query = query.where(
                    exp.NEQ(
                        this=exp.column('follower_id', table=root_alias),
                        expression=exp.column('followee_id', table=target_alias)
                    )
                )
                
                if random.random() < 0.3:
                    query = query.limit(10)

        return query, complexity
