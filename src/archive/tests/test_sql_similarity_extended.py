
import unittest
import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from metrics.sql_similarity import SQLSimilarity

class TestSQLSimilarity(unittest.TestCase):
    def setUp(self):
        self.scorer = SQLSimilarity()

    def test_identical_sql(self):
        sql = "SELECT * FROM table"
        score = self.scorer.compute_score(sql, sql)
        self.assertEqual(score, 1.0, "Identical SQL should have score 1.0")

    def test_canonicalization_and_reorder(self):
        # A AND B vs B AND A
        sql1 = "SELECT * FROM t WHERE a = 1 AND b = 2"
        sql2 = "SELECT * FROM t WHERE b = 2 AND a = 1"
        self.assertEqual(self.scorer.compute_score(sql1, sql2), 1.0, "Reordered AND should be identical")
        
        # A OR B vs B OR A
        sql1 = "SELECT * FROM t WHERE a = 1 OR b = 2"
        sql2 = "SELECT * FROM t WHERE b = 2 OR a = 1"
        self.assertEqual(self.scorer.compute_score(sql1, sql2), 1.0, "Reordered OR should be identical")

        # JOIN reordering (assuming inner joins usually)
        sql1 = "SELECT * FROM t1 JOIN t2 ON t1.id = t2.id"
        sql2 = "SELECT * FROM t2 JOIN t1 ON t1.id = t2.id" 
        # Note: the ON clause might also need normalization if t1.id=t2.id vs t2.id=t1.id
        # Our sort logic handles JOIN order in the list, but let's see if it works.
        # However, "FROM t1 JOIN t2" structure in sqlglot might be "SELECT * FROM t1" with "JOIN t2" in args.
        # "FROM t2 JOIN t1" is "SELECT * FROM t2" with "JOIN t1". 
        # These are structurally different roots (FROM table). 
        # Our sorter only sorts the `joins` list. It does NOT swap the FROM table with a JOIN table currently.
        # That is a much harder semantic equivalence problem. 
        # Let's test just the JOIN list order if we have multiple joins.
        
        sql_joins_1 = "SELECT * FROM main JOIN a ON main.id=a.id JOIN b ON main.id=b.id"
        sql_joins_2 = "SELECT * FROM main JOIN b ON main.id=b.id JOIN a ON main.id=a.id"
        self.assertEqual(self.scorer.compute_score(sql_joins_1, sql_joins_2), 1.0, "Reordered JOIN list should be identical")

    def test_canonicalization_casing_alias(self):
        # Case insensitivity
        sql1 = "SELECT * FROM table"
        sql2 = "select * from TABLE"
        self.assertEqual(self.scorer.compute_score(sql1, sql2), 1.0, "Case differences should be ignored")
        
        # Optimizer should handle basic qualification if schema is not needed or inferred?
        # Without schema, sqlglot optimizer might not fully qualify everything, but it standardizes.
        # Let's verify standard normalization.
        sql1 = "SELECT id FROM table"
        sql2 = "SELECT id FROM table" # trivial
        self.assertEqual(self.scorer.compute_score(sql1, sql2), 1.0)

    def test_ted_accuracy(self):
        # Small difference
        sql1 = "SELECT col1 FROM table"
        sql2 = "SELECT col2 FROM table"
        score_small = self.scorer.compute_score(sql1, sql2)
        self.assertTrue(0.0 < score_small < 1.0, "Small difference should have high but <1 score")
        
        # Large difference
        sql3 = "SELECT * FROM other_table WHERE x=1 GROUP BY y"
        score_large = self.scorer.compute_score(sql1, sql3)
        self.assertTrue(score_large < score_small, f"Large difference score ({score_large}) should be < small difference score ({score_small})")

    def test_edge_cases(self):
        # Syntax Error
        score = self.scorer.compute_score("SELECT * FROM", "SELECT * FROM table")
        self.assertEqual(score, 0.0, "Syntax error should return 0.0")

        # None input
        score = self.scorer.compute_score(None, "SELECT 1")
        self.assertEqual(score, 0.0, "None input should return 0.0")
        
        # Set operations
        sql1 = "SELECT * FROM a UNION SELECT * FROM b"
        sql2 = "SELECT * FROM a UNION SELECT * FROM b"
        self.assertEqual(self.scorer.compute_score(sql1, sql2), 1.0)

if __name__ == '__main__':
    unittest.main()
