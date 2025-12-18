"""
Functional Accuracy Verification Script for SQL Queries.

Compares baseline SQL queries with LLM-generated SQL queries using:
1. Syntax Check - Parse both queries to validate SQL syntax
2. AST Comparison - Normalize and compare abstract syntax trees for structural equivalence
"""

import json
import sqlglot
import os
from sqlglot.optimizer import normalize, qualify
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
import sys


class SQLVerifier:
    """Verify functional accuracy of generated SQL against baseline."""
    
    def __init__(self, dialect: str = 'mysql'):
        """
        Initialize SQL verifier.
        
        Args:
            dialect: SQL dialect to use for parsing (default: mysql)
        """
        self.dialect = dialect
    
    def verify_single_query(
        self, 
        baseline_sql: str, 
        generated_sql: str
    ) -> Dict[str, Any]:
        """
        Verify a single generated SQL query against its baseline.
        
        Args:
            baseline_sql: Ground truth SQL query
            generated_sql: LLM-generated SQL query
        
        Returns:
            Dict with verification results:
                - status: 'PASS_FAST', 'SYNTAX_ERROR', 'STRUCTURAL_MISMATCH'
                - stage: Which stage determined the result
                - baseline_parsed: Boolean if baseline parsed successfully
                - generated_parsed: Boolean if generated parsed successfully
                - match: Boolean if queries match (AST level)
                - error: Error message if any
        """
        result = {
            'baseline_sql': baseline_sql,
            'generated_sql': generated_sql,
            'status': None,
            'stage': None,
            'baseline_parsed': False,
            'generated_parsed': False,
            'match': False,
            'error': None,
            'baseline_normalized': None,
            'generated_normalized': None
        }
        
        # Stage 1: Syntax Check
        try:
            baseline_ast = sqlglot.parse_one(baseline_sql, dialect=self.dialect)
            result['baseline_parsed'] = True
        except Exception as e:
            result['status'] = 'SYNTAX_ERROR'
            result['stage'] = 'STAGE_1_SYNTAX'
            result['error'] = f"Baseline syntax error: {str(e)}"
            return result
        
        try:
            generated_ast = sqlglot.parse_one(generated_sql, dialect=self.dialect)
            result['generated_parsed'] = True
        except Exception as e:
            result['status'] = 'SYNTAX_ERROR'
            result['stage'] = 'STAGE_1_SYNTAX'
            result['error'] = f"Generated syntax error: {str(e)}"
            return result
        
        # Stage 2: AST Comparison
        try:
            # Normalize both ASTs (normalize doesn't take dialect parameter)
            baseline_normalized = normalize.normalize(baseline_ast)
            generated_normalized = normalize.normalize(generated_ast)
            
            # Convert to canonical SQL strings
            baseline_canonical = baseline_normalized.sql(dialect=self.dialect)
            generated_canonical = generated_normalized.sql(dialect=self.dialect)
            
            result['baseline_normalized'] = baseline_canonical
            result['generated_normalized'] = generated_canonical
            
            # Compare
            if baseline_canonical == generated_canonical:
                result['status'] = 'PASS_FAST'
                result['stage'] = 'STAGE_2_AST'
                result['match'] = True
            else:
                result['status'] = 'STRUCTURAL_MISMATCH'
                result['stage'] = 'STAGE_2_AST'
                result['match'] = False
                result['error'] = 'ASTs do not match after normalization'
        
        except Exception as e:
            result['status'] = 'AST_COMPARISON_ERROR'
            result['stage'] = 'STAGE_2_AST'
            result['error'] = f"AST comparison error: {str(e)}"
        
        return result
    
    def verify_from_results_file(self, results_file: str) -> Dict[str, Any]:
        """
        Verify all queries from an LLM test results file.
        
        Args:
            results_file: Path to JSON file with LLM test results
        
        Returns:
            Dict with verification summary and detailed results
        """
        # Load results
        with open(results_file, 'r') as f:
            llm_results = json.load(f)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        verification_results = {
            'metadata': {
                'timestamp': timestamp,
                'source_file': results_file,
                'llm_provider': llm_results['metadata'].get('llm_provider'),
                'llm_model': llm_results['metadata'].get('model_name'),
                'num_samples': llm_results['metadata'].get('num_samples'),
                'num_total_tests': llm_results['metadata'].get('num_total_tests')
            },
            'summary': {
                'total_verified': 0,
                'pass_fast': 0,
                'syntax_errors': 0,
                'structural_mismatches': 0,
                'ast_errors': 0
            },
            'tests': []
        }
        
        # Verify each test
        for test in llm_results['tests']:
            sample_id = test['sample_id']
            baseline_sql = test['ground_truth_sql']
            
            test_results = {
                'sample_id': sample_id,
                'baseline_sql': baseline_sql,
                'complexity': test.get('complexity'),
                'vanilla_result': None,
                'variation_results': []
            }
            
            # Verify vanilla prompt
            if test['vanilla']['success'] and test['vanilla']['generated_sql']:
                vanilla_verification = self.verify_single_query(
                    baseline_sql,
                    test['vanilla']['generated_sql']
                )
                test_results['vanilla_result'] = vanilla_verification
                self._update_summary(verification_results['summary'], vanilla_verification)
            
            # Verify variations
            for var in test['variations']:
                if var['success'] and var['generated_sql']:
                    var_verification = self.verify_single_query(
                        baseline_sql,
                        var['generated_sql']
                    )
                    test_results['variation_results'].append(var_verification)
                    self._update_summary(verification_results['summary'], var_verification)
            
            verification_results['tests'].append(test_results)
        
        return verification_results
    
    def _update_summary(self, summary: Dict, result: Dict):
        """Update summary statistics."""
        summary['total_verified'] += 1
        
        if result['status'] == 'PASS_FAST':
            summary['pass_fast'] += 1
        elif result['status'] == 'SYNTAX_ERROR':
            summary['syntax_errors'] += 1
        elif result['status'] == 'STRUCTURAL_MISMATCH':
            summary['structural_mismatches'] += 1
        elif result['status'] == 'AST_COMPARISON_ERROR':
            summary['ast_errors'] += 1


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Verify functional accuracy of LLM-generated SQL queries'
    )
    parser.add_argument(
        'results_file',
        help='Path to JSON file with LLM test results'
    )
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='Output file for verification results (default: verification_results_<timestamp>.json)'
    )
    parser.add_argument(
        '-d', '--dialect',
        default='mysql',
        help='SQL dialect (default: mysql)'
    )
    
    args = parser.parse_args()
    
    # Initialize verifier
    verifier = SQLVerifier(dialect=args.dialect)
    
    print(f"Verifying queries from: {args.results_file}")
    print("="*80)
    
    # Run verification
    results = verifier.verify_from_results_file(args.results_file)
    
    # Determine output directory and file
    output_dir = "analysis_results"
    os.makedirs(output_dir, exist_ok=True)
    
    if args.output:
        output_file = os.path.join(output_dir, args.output)
    else:
        timestamp = results['metadata']['timestamp']
        output_file = os.path.join(output_dir, f"verification_results_{timestamp}.json")
    
    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\nVerification Summary:")
    print("-" * 40)
    summary = results['summary']
    print(f"Total Verified: {summary['total_verified']}")
    print(f"  PASS_FAST (identical): {summary['pass_fast']} ({summary['pass_fast']/summary['total_verified']*100:.1f}%)")
    print(f"  Syntax Errors: {summary['syntax_errors']} ({summary['syntax_errors']/summary['total_verified']*100:.1f}%)")
    print(f"  Structural Mismatches: {summary['structural_mismatches']} ({summary['structural_mismatches']/summary['total_verified']*100:.1f}%)")
    print(f"  AST Errors: {summary['ast_errors']} ({summary['ast_errors']/summary['total_verified']*100:.1f}%)")
    print("="*80)
    print(f"✓ Results saved to: {output_file}")


if __name__ == "__main__":
    main()
