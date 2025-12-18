# Walkthrough - AST-Guided SQL Generator

I have successfully implemented the AST-Guided SQL Generator using `sqlglot`. The tool generates valid, schema-aware SQL queries for a mock Social Media database, including advanced features like subqueries in FROM, date arithmetic, and self-joins.

## Implementation Details

The project is structured as follows:
- `schema.py`: Defines the database schema and foreign key relationships.
- `generator.py`: Contains the `SQLQueryGenerator` class which builds ASTs using `sqlglot`.
- `main.py`: Drives the generation process, producing 500 queries in `social_media_queries.json`.
- `analyze_results.py`: Analyzes the generated queries and produces visualizations.

## Results

I generated 500 queries with varying complexity levels.

### Complexity Distribution
The generator was configured to produce queries with the following probability distribution:
- Simple: 40%
- Join: 30%
- Aggregate: 20%
- Advanced: 10%

![Complexity Distribution](/Users/obby/.gemini/antigravity/brain/031bd415-c3c0-480f-937d-cc4d462f0a3f/complexity_distribution.png)

### Table Usage
The generator randomly selects root tables and joins related tables. Here is the frequency of table usage across the generated dataset:

![Table Usage](/Users/obby/.gemini/antigravity/brain/031bd415-c3c0-480f-937d-cc4d462f0a3f/table_usage.png)

## Sample Queries

Here are a few examples of generated queries:

### Simple
```sql
SELECT l1.user_id, l1.post_id FROM likes AS l1 WHERE l1.liked_at < NOW() ORDER BY l1.post_id
```

### Join
```sql
SELECT u1.country_code, u1.username, p2.content, p2.view_count 
FROM users AS u1 
JOIN posts AS p2 ON u1.id = p2.user_id 
WHERE p2.view_count > 450
```

### Aggregate
```sql
SELECT c1.user_id, COUNT(c1.comment_text) AS count_comment_text 
FROM comments AS c1 
GROUP BY c1.user_id 
HAVING COUNT(*) > 5
```

### Advanced (Subquery in WHERE)
```sql
SELECT u1.username, u1.email 
FROM users AS u1 
WHERE u1.id IN (SELECT p.user_id FROM posts AS p WHERE p.view_count = 1)
```

### Advanced (Subquery in FROM)
```sql
SELECT * 
FROM (SELECT * FROM comments AS inner_comments WHERE inner_comments.user_id < 257) AS derived_table 
WHERE derived_table.created_at >= DATE_SUB(NOW(), INTERVAL 6 DAY)
```

### Advanced (Self-Join)
```sql
SELECT f1.follower_id AS user, f2.followee_id AS friend_of_friend 
FROM follows AS f1 
JOIN follows AS f2 ON f1.followee_id = f2.follower_id 
WHERE f1.follower_id <> f2.followee_id 
LIMIT 10
```

### Date Arithmetic
```sql
SELECT p1.id, p1.posted_at 
FROM posts AS p1 
WHERE p1.posted_at >= DATE_SUB(NOW(), INTERVAL 18 DAY)
```

## Verification
- **Syntax Validity**: All queries were built using `sqlglot` expression builders, ensuring syntactic correctness.
- **Schema Awareness**: Joins are only created between tables with defined foreign keys.
- **Diversity**: The visualizations confirm that all complexity levels and tables are represented.
- **Advanced Features**: Verified presence of `DATE_SUB`, `INTERVAL`, nested `SELECT` in `FROM`, and self-joins in the output.
- **Bug Fixes**: Resolved issue where `IN` clauses were empty (`IN ()`). Now they correctly contain subqueries.
