# SQLSimilarity Implementation Walkthrough

We have implemented a robust `SQLSimilarity` class in `src/metrics/sql_similarity.py` that benchmarks LLM-generated SQL against Gold Standard SQL using **Tree Edit Distance (TED)**.

## Key Features

1.  **Robust Canonicalization**:
    *   **Optimization**: Uses `sqlglot` to qualify columns, simplify booleans, and normalize casing.
    *   **Custom Sorting**: Sorts `JOIN` clauses and `AND`/`OR` chains to ensure that semantically identical but structurally slightly different queries (reordered) receive a perfect score.

2.  **Tree Edit Distance (TED)**:
    *   Uses the **Zhang-Shasha** algorithm via the `zss` library.
    *   Computes a normalized similarity score (0.0 to 1.0).

3.  **Adapter Pattern**:
    *   `SQLNode` adapts `sqlglot` expressions for `zss` compatibility.

## Changes

### New Files
*   `src/metrics/sql_similarity.py`: Core implementation.
*   `tests/test_sql_similarity_extended.py`: Comprehensive test suite.

## Verification Results

We verified the implementation with an extensive test suite covering:
*   **Identical SQL**: Score 1.0.
*   **Reordered `AND` / `OR`**: Score 1.0 (Canonicalization verified).
*   **Reordered `JOIN`**: Score 1.0 (Canonicalization verified).
*   **Case Insensitivity**: Score 1.0.
*   **TED Accuracy**: Differentiates between small and large structural changes.
*   **Edge Cases**: Syntactically invalid SQL returns 0.0.

### Test Output

```
.....
----------------------------------------------------------------------
Ran 5 tests in 0.049s

OK
```

All 5 test categories passed successfully.

## Tested Examples

| Category | SQL A | SQL B | Resulting Score |
| :--- | :--- | :--- | :--- |
| **Identical** | `SELECT * FROM table` | `SELECT * FROM table` | 1.0000 |
| **Reordered AND** | `SELECT * FROM t WHERE a = 1 AND b = 2` | `SELECT * FROM t WHERE b = 2 AND a = 1` | 1.0000 |
| **Reordered OR** | `SELECT * FROM t WHERE a = 1 OR b = 2` | `SELECT * FROM t WHERE b = 2 OR a = 1` | 1.0000 |
| **Reordered JOIN** | `SELECT * FROM main JOIN a ON main.id=a.id JOIN b ON main.id=b.id` | `SELECT * FROM main JOIN b ON main.id=b.id JOIN a ON main.id=a.id` | 1.0000 |
| **Case Insensitivity** | `SELECT * FROM table` | `select * from TABLE` | 1.0000 |
| **Small Difference** | `SELECT col1 FROM table` | `SELECT col2 FROM table` | 0.8636 |
| **Large Difference** | `SELECT col1 FROM table` | `SELECT * FROM other_table WHERE x=1 GROUP BY y` | 0.3929 |
| **Syntax Error** | `SELECT * FROM` | `SELECT * FROM table` | 0.0000 |
| **Union** | `SELECT * FROM a UNION SELECT * FROM b` | `SELECT * FROM a UNION SELECT * FROM b` | 1.0000 |


## Usage Example

```python
from metrics.sql_similarity import SQLSimilarity

scorer = SQLSimilarity()
gold = "SELECT id FROM users WHERE age > 25 AND city = 'NY'"
gen = "SELECT id FROM users WHERE city = 'NY' AND age > 25"

score = scorer.compute_score(gold, gen)
print(f"Similarity Score: {score}")  # Output: 1.0
```
