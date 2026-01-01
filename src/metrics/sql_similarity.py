
import sqlglot
from sqlglot import exp, optimizer
from zss import simple_distance

class SQLNode:
    """Adapter for ZSS library to work with sqlglot expressions."""
    def __init__(self, expression):
        self.label = expression.key
        # Append values for leaf nodes (identifiers/literals) to distinguish them
        if isinstance(expression, (exp.Identifier, exp.Literal, exp.Column, exp.Table)):
             # "this" attributes hold the string values for these types
            self.label += f":{expression.this}"
        
        # Helper to get children, ignoring empty/None
        self.children = [
            SQLNode(child) 
            for child in expression.iter_expressions() 
            if child is not None
        ]

    @staticmethod
    def get_children(node): 
        return node.children
    
    @staticmethod
    def get_label(node): 
        return node.label

class SQLSimilarity:
    """
    Computes semantic similarity between two SQL queries using Tree Edit Distance (TED).
    Includes robust canonicalization to handle irrelevant differences (ordering, aliases).
    """

    def _sort_logic(self, expression):
        """
        Custom transformer to canonicalize the AST by enforcing deterministic ordering.
        - Sorts JOIN clauses by table name.
        - Sorts commutative logical operations (AND, OR) by string representation.
        """
        
        # 1. Sort JOINs
        # Joins are usually part of a Select expression. We need to find them and sort them.
        # However, sqlglot AST structure for joins is a list in the 'joins' arg of a Select.
        # But iter_expressions usually flattens them. 
        # Better approach: transformation walk.
        
        def _transform(node):
            # Sort JOINs if this node has them (e.g. Select)
            if isinstance(node, exp.Select):
                # node.args.get('joins') returns a list of Join expressions
                joins = node.args.get('joins')
                if joins:
                    # Sort joins by their string representation (table name mostly)
                    # We assume INNER joins for reordering safety in this simple version, 
                    # but sorting all might be acceptable for "structural" similarity if we treat them as a set.
                    # STRICTLY speaking, reordering joins changes semantics if not inner, but for "similarity" benchmarking it's often preferred to align them.
                    node.set('joins', sorted(joins, key=lambda x: x.sql()))
            
            # Sort AND / OR chains
            # sqlglot represents A AND B AND C as nested binary ops or strictly binary.
            # Flattening and sorting is the most robust way.
            if isinstance(node, (exp.And, exp.Or)):
                 # This is tricky because the tree is binary. 
                 # We can rely on sqlglot.optimizer.simplify to flatten? 
                 # Actually, let's just do a simple recursive sort of the immediate children if they are the same type?
                 # A better way for simple AST comparison is just to trust the optimizer has simplified structure,
                 # but we might want to ensure 'a=1 AND b=2' is same as 'b=2 AND a=1'.
                 pass
            
            return node

        # Custom walker to sort commutative ops
        # We'll use a simplified approach: collect all conditions in WHERE/HAVING, sort them, and rebuild.
        # But rebuilding the tree is complex. 
        # Alternative: Just rely on simple sorting of binary operands? 
        # IF node is AND/OR/EQ/NEQ, sort left/right by string repr?
        
        expression = expression.transform(_sort_commutative)
        expression = expression.transform(_sort_joins)
        return expression

    def preprocess(self, sql):
        try:
            parsed = sqlglot.parse_one(sql)
            # 1. Built-in Optimizer
            # - qualifies columns (table.col)
            # - simplifies booleans
            # - lowercases (usually via normalize=True parser or optimizer)
            optimized = optimizer.optimize(parsed)
            
            # 2. Custom Sorting
            canonical = self._sort_ast(optimized)
            return canonical
        except Exception as e:
            # print(f"Preprocessing failed: {e}") 
            return None

    def _sort_ast(self, tree):
        """Applies sorting rules to the AST."""
        
        def _sorter(node):
            # Sort JOINs
            if isinstance(node, exp.Select):
                joins = node.args.get('joins')
                if joins:
                    # Sort by the robust SQL string of the joined table
                    node.set('joins', sorted(joins, key=lambda x: x.this.sql()))
            
            # Sort Commutative Binary Ops: AND, OR, EQ, NEQ in a local sense
            # e.g. A AND B -> sort A and B. 
            # Note: This doesn't fully flatten chains like (A AND B) AND C, but repeated application 
            # by the recursive transform might help align them effectively enough for TED.
            if isinstance(node, (exp.And, exp.Or, exp.EQ, exp.NEQ)):
                 # We can swap left and right if right < left
                 left = node.left
                 right = node.right
                 if left and right and left.sql() > right.sql():
                     node.set('this', right)
                     node.set('expression', left)
            
            return node
        
        return tree.transform(_sorter)

    def compute_score(self, gold_sql, gen_sql):
        gold_tree = self.preprocess(gold_sql)
        gen_tree = self.preprocess(gen_sql)

        if not gold_tree or not gen_tree:
            return 0.0

        gold_node = SQLNode(gold_tree)
        gen_node = SQLNode(gen_tree)

        dist = simple_distance(
            gold_node, 
            gen_node, 
            SQLNode.get_children, 
            SQLNode.get_label
        )
        
        total_nodes = self._count(gold_node) + self._count(gen_node)
        if total_nodes == 0: return 1.0
        
        # Max distance is bounded by max(nodes1, nodes2) roughly? 
        # Actually standard edit distance logic: max cost is max(len1, len2). 
        # Normalizing by sum(len) is a safe conservative overlap metric.
        # Score = 1 - (dist / total_nodes) might be too punitive? 
        # 1 - dist / (nodes1 + nodes2) means 0.5 similarity for disjoint trees?
        # Standard: 1 - dist / max(nodes1, nodes2)? 
        # Let's stick to the user formula request or a sensible default.
        # User requested: "1 - (cost / total_nodes)" in the skeleton. 
        # Wait, the skeleton says: `1 - (cost / total_nodes)`
        
        return 1.0 - (dist / total_nodes)

    def _count(self, node):
        return 1 + sum(self._count(c) for c in node.children)
