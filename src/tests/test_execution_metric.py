
import unittest
import sys
import os
import sqlite3

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from metrics.execution_metric import ExecutionVerifier
from core.schema import SCHEMA, FOREIGN_KEYS

class TestExecutionVerifier(unittest.TestCase):
    def setUp(self):
        # Use Real Schema
        self.verifier = ExecutionVerifier(SCHEMA, FOREIGN_KEYS)

    def test_basic_match(self):
        # Even with random data, identical SQL should match
        sql = "SELECT id, username FROM users"
        # Using default num_rows (100) or specify
        self.assertTrue(self.verifier.verify(sql, sql, num_rows=100), "Identical SQL should return True")

    def test_basic_mismatch(self):
        # Different semantics should mismatch
        sql1 = "SELECT id FROM users"
        sql2 = "SELECT id FROM posts" # Different table, different data IDs likely unless coincidental
        # With 100 rows, IDs might overlap (1..100) but bag equality of entire result set? 
        # IDs are generated 1..N per table. So Users has 1..100, Posts has 1..100.
        # So "SELECT id FROM users" returns [1..100]. "SELECT id FROM posts" returns [1..100].
        # THEY WILL MATCH if we only select ID!
        # WARNING: This test case is tricky if we simplified ID generation to be 1..N for all tables.
        # Let's check something that differs, like 'count(*)' or data content.
        # Or "SELECT username FROM users" vs "SELECT content FROM posts".
        
        sql1 = "SELECT username FROM users"
        sql2 = "SELECT content FROM posts" 
        self.assertFalse(self.verifier.verify(sql1, sql2, num_rows=50), "Different semantic queries should return False")

    def test_filter_match(self):
        # "SELECT username FROM users WHERE is_verified = 1"
        sql = "SELECT username FROM users WHERE is_verified = 1"
        self.assertTrue(self.verifier.verify(sql, sql, num_rows=50))
        
    def test_join_validity(self):
        # Verify JOINs work (FKs populated)
        # "SELECT users.username, posts.content FROM users JOIN posts ON users.id = posts.user_id"
        sql = "SELECT users.username, posts.content FROM users JOIN posts ON users.id = posts.user_id"
        # Should return True against itself, but also we hope it returns non-empty result?
        # The verifier only returns boolean match. To inspect, we'd need to debug. 
        # But if it crashes, it returns False.
        self.assertTrue(self.verifier.verify(sql, sql, num_rows=50))

    def test_bag_semantics(self):
        # "SELECT id FROM users WHERE id > 10"
        sql = "SELECT id FROM users WHERE id > 10"
        self.assertTrue(self.verifier.verify(sql, sql, num_rows=50))

    def test_order_by_strictness(self):
        # Gold: Ordered
        gold = "SELECT id FROM users ORDER BY id DESC"
        # Gen: Unordered (default ASC usually)
        gen = "SELECT id FROM users" 
        
        self.assertFalse(self.verifier.verify(gold, gen, num_rows=50), "Should fail if Gold expects order and Gen mismatch")
        self.assertTrue(self.verifier.verify(gold, gold, num_rows=50))

    def test_syntax_error(self):
        self.assertFalse(self.verifier.verify("SELECT * FROM users", "SELECT * FROM"), "Syntax error should return False")

if __name__ == '__main__':
    unittest.main()
