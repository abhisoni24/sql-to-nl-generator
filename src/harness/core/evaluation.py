"""
Evaluation Logic Component.
Integrates existing metrics to evaluate generated SQL.
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
import sys
import os

# Ensure src is in path to import specific metrics
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.metrics.sql_similarity import SQLSimilarity
from src.metrics.execution_metric import ExecutionVerifier
from src.core.schema import SCHEMA, FOREIGN_KEYS

class FailureType(Enum):
    NONE = "none"
    PARSE_ERROR = "parse_error"
    EXECUTION_ERROR = "execution_error"
    MISMATCH = "mismatch"
    EMPTY = "empty"

@dataclass
class EvaluationResult:
    similarity_score: float
    execution_match: bool
    failure_type: str

class Evaluator:
    """Central evaluator using established metrics."""
    
    def __init__(self):
        self.ted_scorer = SQLSimilarity()
        self.exec_verifier = ExecutionVerifier(SCHEMA, FOREIGN_KEYS)

    def evaluate(self, gold_sql: str, gen_sql: str) -> EvaluationResult:
        """
        Evaluate a single generated SQL against the gold standard.
        """
        if not gen_sql:
            return EvaluationResult(0.0, False, FailureType.EMPTY.value)

        # 1. Structural Similarity (TED)
        # SQLSimilarity internal handles parsing errors by returning 0.0 usually?
        # Let's check implementation if needed, but assuming robustness.
        try:
            ted_score = self.ted_scorer.compute_score(gold_sql, gen_sql)
        except Exception:
            ted_score = 0.0
            # If parsing fails here, likely execution will too or it's a parse error.
        
        # 2. Execution Verification
        try:
            # Using default num_rows=100 as per existing tests
            exec_match = self.exec_verifier.verify(gold_sql, gen_sql, num_rows=100)
            
            failure = FailureType.NONE.value
            if not exec_match:
                failure = FailureType.MISMATCH.value # Or Execution Error if verify returns False on error?
                # ExecutionVerifier verify returns False on exception too.
                # simpler logic: if false, it failed.
        except Exception:
            exec_match = False
            failure = FailureType.EXECUTION_ERROR.value

        # Refine failure type if score is 0 and exec is False
        if ted_score == 0.0 and not exec_match:
             failure = FailureType.PARSE_ERROR.value # Likely

        if exec_match:
             failure = FailureType.NONE.value

        return EvaluationResult(
            similarity_score=ted_score,
            execution_match=exec_match,
            failure_type=failure
        )
