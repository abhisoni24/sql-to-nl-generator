"""
Output Normalization Component.
Responsible for cleaning raw LLM outputs and extracting valid SQL.
"""
import re

def normalize_sql(raw_output: str) -> str:
    """
    Normalize raw LLM output to extract executable SQL.
    
    Strategy:
    1. Remove Markdown code blocks (```sql ... ```).
    2. Remove generic markdown fences (``` ... ```).
    3. Strip whitespace.
    4. Remove trailing semi-colons (optional, but good for some parsers, though adapters handle stops).
    5. Taking the first non-empty line(s) that look like SQL if mixed with text? 
       Actually, the prompt instructions usually enforce "ONLY SQL".
       But we must be robust.
    
    Returns:
        Cleaned SQL string.
    """
    if not raw_output:
        return ""

    cleaned = raw_output.strip()

    # 1. Extract from Code Blocks if present
    # Regex to capture content inside ```sql ... ``` or ``` ... ```
    # Non-greedy match for the first block
    code_block_pattern = re.compile(r"```(?:sql|mysql)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)
    match = code_block_pattern.search(cleaned)
    if match:
        cleaned = match.group(1).strip()
    else:
        # If no code blocks, assume the whole text might be SQL, 
        # but try to strip common "Here is the SQL:" prefixes if simple stripping didn't work.
        # However, strictly per requirements: "Removes markdown/code fences".
        # We shouldn't over-engineer "smart" extraction unless specified. 
        # "No output rewriting" was for adapters. Here we normalize.
        pass

    # 2. Strip comments (basic -- style)? 
    # Maybe risky if strings contain --. SQLGlot handles comments fine usually.
    # Let's stick to structural cleanup.
    
    return cleaned
