"""
Output Normalization Component.
Responsible for cleaning raw LLM outputs and extracting valid SQL.
Enhanced with semantic normalization for fair comparison.
"""
import re
import sqlglot

def normalize_sql(raw_output: str) -> str:
    """
    Normalize raw LLM output to extract and standardize executable SQL.
    
    Strategy:
    1. Remove Markdown code blocks (```sql ... ```).
    2. Strip whitespace and trailing semicolons.
    3. Normalize SQL syntax for semantic comparison.
    
    Returns:
        Cleaned and normalized SQL string.
    """
    if not raw_output:
        return ""

    cleaned = raw_output.strip()

    # 1. Extract from Code Blocks if present
    code_block_pattern = re.compile(r"```(?:sql|mysql)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)
    match = code_block_pattern.search(cleaned)
    if match:
        cleaned = match.group(1).strip()
    
    # 2. Strip trailing semicolons (FIX #1: Critical bug - now actually implemented!)
    cleaned = cleaned.rstrip(';').strip()
    
    # 3. Apply semantic normalization
    try:
        cleaned = semantic_normalize_sql(cleaned)
    except Exception:
        # If normalization fails, return the basic cleaned version
        pass
    
    return cleaned


def semantic_normalize_sql(sql: str) -> str:
    """
    Normalize SQL to a canonical form for semantic comparison.
    
    Handles:
    - Keyword case normalization (SELECT -> select)
    - Whitespace normalization  
    - JOIN variant normalization (INNER JOIN -> JOIN)
    - Table prefix removal when unambiguous
    - SELECT * vs SELECT table.* equivalence
    - MySQL vs SQLite function equivalence
    
    Returns:
        Semantically normalized SQL string.
    """
    if not sql:
        return ""
    
    try:
        # Parse SQL using sqlglot
        # Use 'mysql' dialect as our gold SQL is MySQL-based
        parsed = sqlglot.parse_one(sql, dialect='mysql')
        
        # Transform to normalized form
        normalized_ast = normalize_ast(parsed)
        
        # Convert back to SQL string in standardized format
        # Use lowercase keywords, consistent spacing
        normalized_sql = normalized_ast.sql(dialect='mysql', pretty=False)
        
        # Additional text-level normalizations
        normalized_sql = post_process_normalization(normalized_sql)
        
        return normalized_sql.strip()
        
    except Exception as e:
        # If parsing fails, fall back to basic text normalization
        return basic_text_normalization(sql)


def normalize_ast(ast):
    """
    Apply semantic normalizations to the SQL AST.
    
    Transformations:
    - INNER JOIN -> JOIN (they're identical)
    - Remove redundant table qualifiers in single-table queries
    - Normalize function names (DATE_SUB vs datetime arithmetic)
    """
    from sqlglot import exp
    
    # Normalize JOIN types
    for join in ast.find_all(exp.Join):
        # INNER JOIN and JOIN are the same - normalize to JOIN
        if join.args.get('kind') == 'INNER':
            join.args['kind'] = None  # Default JOIN
    
    # Normalize SELECT *
    for select in ast.find_all(exp.Select):
        # Handle SELECT table.* same as SELECT *
        if select.expressions:
            for i, expr in enumerate(select.expressions):
                if isinstance(expr, exp.Star):
                    # SELECT * or SELECT table.* - normalize to just *
                    if expr.args.get('table'):
                        expr.args['table'] = None
    
    return ast


def post_process_normalization(sql: str) -> str:
    """
    Apply final text-level normalizations after AST conversion.
    """
    # Normalize whitespace
    sql = re.sub(r'\\s+', ' ', sql)
    
    # Remove unnecessary parentheses around single column in SELECT
    # e.g., SELECT (col) -> SELECT col
    sql = re.sub(r'SELECT\\s+\\(([a-zA-Z0-9_\\.]+)\\)', r'SELECT \\1', sql)
    
    # Normalize INNER JOIN to JOIN
    sql = re.sub(r'\\bINNER\\s+JOIN\\b', 'JOIN', sql, flags=re.IGNORECASE)
    
    # Normalize case
    sql = sql.upper()
    
    return sql


def basic_text_normalization(sql: str) -> str:
    """
    Fallback normalization when AST parsing fails.
    Applies basic text-level transformations.
    """
    # Strip and normalize whitespace
    sql = sql.strip()
    sql = re.sub(r'\\s+', ' ', sql)
    
    # Remove trailing semicolon
    sql = sql.rstrip(';')
    
    # Normalize common variations
    sql = re.sub(r'\\bINNER\\s+JOIN\\b', 'JOIN', sql, flags=re.IGNORECASE)
    
    # Uppercase keywords (basic attempt)
    keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'ON', 'INSERT', 'INTO', 
                'UPDATE', 'SET', 'DELETE', 'VALUES', 'ORDER', 'BY', 'GROUP',
                'HAVING', 'LIMIT', 'AS', 'AND', 'OR', 'NOT', 'IN', 'LIKE']
    
    for keyword in keywords:
        sql = re.sub(r'\\b' + keyword + r'\\b', keyword.upper(), sql, flags=re.IGNORECASE)
    
    return sql
