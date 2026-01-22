import unittest
from sqlglot import parse_one
from src.core.nl_renderer import SQLToNLRenderer, PerturbationConfig, PerturbationType

class TestSQLToNLRenderer(unittest.TestCase):
    
    def test_determinism(self):
        sql = "SELECT * FROM users"
        ast = parse_one(sql)
        
        # Run 1
        cfg1 = PerturbationConfig(active_perturbations={PerturbationType.SYNONYM_SUBSTITUTION}, seed=123)
        r1 = SQLToNLRenderer(cfg1)
        out1 = r1.render(ast)
        
        # Run 2 (Same Seed)
        cfg2 = PerturbationConfig(active_perturbations={PerturbationType.SYNONYM_SUBSTITUTION}, seed=123)
        r2 = SQLToNLRenderer(cfg2)
        out2 = r2.render(ast)
        
        # Run 3 (Diff Seed)
        cfg3 = PerturbationConfig(active_perturbations={PerturbationType.SYNONYM_SUBSTITUTION}, seed=456)
        r3 = SQLToNLRenderer(cfg3)
        out3 = r3.render(ast)
        
        print(f"Seed 123: {out1}")
        print(f"Seed 456: {out3}")
        
        self.assertEqual(out1, out2, "Renderer should be deterministic with same seed")
        # Note: out1 vs out3 might be same by chance if synonyms distribution is small, but generally should differ over many runs.
        
    def test_vanilla(self):
        sql = "SELECT id FROM users"
        ast = parse_one(sql)
        cfg = PerturbationConfig(active_perturbations=set())
        r = SQLToNLRenderer(cfg)
        out = r.render(ast)
        # Should use default terms
        self.assertIn("Get id", out)
        self.assertIn("from users", out)

    def test_synonyms(self):
         sql = "SELECT id FROM users"
         ast = parse_one(sql)
         cfg = PerturbationConfig(active_perturbations={PerturbationType.SYNONYM_SUBSTITUTION}, seed=999)
         r = SQLToNLRenderer(cfg)
         out = r.render(ast)
         print(f"Synonym output: {out}")
         # Just check it runs and produces something valid
         self.assertTrue(len(out) > 0)

    def test_typos(self):
        sql = "SELECT * FROM users"
        ast = parse_one(sql)
        cfg = PerturbationConfig(active_perturbations={PerturbationType.TYPOS}, seed=42)
        r = SQLToNLRenderer(cfg)
        out = r.render(ast)
        print(f"Typo output: {out}")
        self.assertNotEqual(out, "Get all columns from users.") # Should have typos
        
if __name__ == '__main__':
    unittest.main()
