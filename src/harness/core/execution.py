"""
Execution Engine.
Orchestrates the generation and evaluation loop.
"""
import json
import os
import time
import uuid
import sys
from datetime import datetime
from typing import List, Dict, Any
from ..adapters.base import BaseModelAdapter
from .normalization import normalize_sql
from .evaluation import Evaluator

# Import schema for prompt construction
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from src.core.schema import SCHEMA, FOREIGN_KEYS

class ExecutionEngine:
    
    def __init__(self, adapter: BaseModelAdapter, run_id: str, output_path: str, rate_limit_config: Dict[str, Any] = None):
        self.adapter = adapter
        self.run_id = run_id
        self.output_path = output_path
        self.evaluator = Evaluator()
        self.schema = SCHEMA
        self.foreign_keys = FOREIGN_KEYS
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Rate limiting configuration
        self.rate_limit_config = rate_limit_config or {}
        self.requests_per_minute = self.rate_limit_config.get('requests_per_minute', None)
        self.max_retries = self.rate_limit_config.get('max_retries', 0)
        
        # Calculate delay between batches if rate limiting is enabled
        if self.requests_per_minute:
            # Add a small buffer to be safe
            self.batch_delay = (60.0 / self.requests_per_minute) * 1.1
            print(f"⏱️  Rate limiting enabled: {self.requests_per_minute} req/min (delay: {self.batch_delay:.1f}s between batches)")
        else:
            self.batch_delay = 0
            print(f"⚡ No rate limiting (local model or unlimited API)")
        
        # Determine batch size
        if adapter.model_family() == "open": # VLLM
            self.batch_size = 32
        else: # API
            self.batch_size = 5

    def execute_experiment(self, prompts_path: str):
        """End-to-end execution: load, batch, generate, normalize, evaluate, log."""
        # 1. Load Prompts (extracts all perturbations)
        prompts_data = self._load_prompts(prompts_path)
        print(f"Loaded {len(prompts_data)} prompts from {prompts_path}")

        # 2. Batching
        batches = [prompts_data[i:i + self.batch_size] for i in range(0, len(prompts_data), self.batch_size)]
        
        print(f"Processing {len(batches)} batches with size {self.batch_size}...")

        # 3. Execution Loop with Rate Limiting
        for batch_idx, batch in enumerate(batches):
            # Apply rate limiting delay before each batch (except first)
            if batch_idx > 0 and self.batch_delay > 0:
                print(f"  ⏳ Rate limit delay: {self.batch_delay:.1f}s...")
                time.sleep(self.batch_delay)
            
            # Construct full prompts with schema context
            prompt_texts = [self._construct_full_prompt(p['prompt_text']) for p in batch]
            
            # Generate with retry logic for rate limit errors
            raw_outputs = self._generate_with_retry(prompt_texts)
            
            # Process outputs
            for i, raw_output in enumerate(raw_outputs):
                prompt_item = batch[i]
                
                # Normalize
                normalized_sql = normalize_sql(raw_output)
                
                # Evaluate
                # Need gold sql from prompt item
                gold_sql = prompt_item.get('sql', '') # Assuming 'sql' key in input
                
                eval_result = self.evaluator.evaluate(gold_sql, normalized_sql)
                
                # Log Record with comprehensive metadata
                record = {
                    # Run and model identification
                    "run_id": self.run_id,
                    "model_name": self.adapter.model_name(),
                    "model_family": self.adapter.model_family(),
                    
                    # Prompt identification (now includes perturbation info)
                    "prompt_id": prompt_item.get('prompt_id', str(uuid.uuid4())),
                    "prompt_text": prompt_item['prompt_text'],
                    
                    # NEW: Perturbation tracking
                    "perturbation_type": prompt_item.get('perturbation_type', 'unknown'),
                    "perturbation_id": prompt_item.get('perturbation_id', -1),
                    
                    # NEW: Query characteristics
                    "query_complexity": prompt_item.get('complexity', 'unknown'),
                    "tables_involved": prompt_item.get('tables', []),
                    
                    # NEW: Gold standard for offline analysis
                    "gold_sql": gold_sql,
                    
                    # Generation outputs
                    "raw_output": raw_output,
                    "normalized_sql": normalized_sql,
                    
                    # Evaluation results
                    "evaluation_result": {
                        "correctness": eval_result.execution_match,
                        "similarity_score": eval_result.similarity_score,
                        "failure_type": eval_result.failure_type
                    },
                    
                    # Configuration and metadata
                    "decoding_config": self.adapter.decoding_config(),
                    "metadata": prompt_item.get('metadata', {}),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                self._log_record(record)
    
    def _generate_with_retry(self, prompt_texts: List[str]) -> List[str]:
        """
        Generate with retry logic for rate limit errors.
        
        Args:
            prompt_texts: List of prompts to generate for
            
        Returns:
            List of generated SQL strings (empty string on failure)
        """
        for attempt in range(self.max_retries + 1):
            try:
                return self.adapter.generate(prompt_texts)
            except Exception as e:
                error_str = str(e)
                # Check if it's a rate limit error (429 or RESOURCE_EXHAUSTED)
                is_rate_limit = '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str or 'rate' in error_str.lower()
                
                if is_rate_limit and attempt < self.max_retries:
                    # Exponential backoff: 2, 4, 8 seconds
                    delay = 2 ** (attempt + 1)
                    print(f"  ⚠️  Rate limit hit, retrying in {delay}s... (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(delay)
                else:
                    # Non-rate-limit error or out of retries - return empty strings
                    import logging
                    logging.error(f"Generation failed after {attempt + 1} attempts: {error_str}")
                    return [""] * len(prompt_texts)
        
        # Should never reach here, but just in case
        return [""] * len(prompt_texts)
                
    def _load_prompts(self, path: str) -> List[Dict[str, Any]]:
        """
        Load prompts from JSON or JSONL, extracting ALL perturbations.
        
        For each query in the dataset, this creates:
        - 1 test case for the original prompt
        - N test cases for each applicable perturbation
        
        This expands ~2100 queries to ~16,800 test cases.
        """
        data = []
        with open(path, 'r') as f:
            if path.endswith('.jsonl'):
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        data.extend(self._extract_all_prompts_from_query(item))
            else:
                # Assume standard JSON list (our nl_social_media_queries.json format)
                content = json.load(f)
                for item in content:
                    data.extend(self._extract_all_prompts_from_query(item))
                    
        return data
    
    def _extract_all_prompts_from_query(self, query_item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract all test cases from a single query item.
        
        Args:
            query_item: A single query from the dataset with perturbations.
            
        Returns:
            List of test case dictionaries, one for original + one per applicable perturbation.
        """
        test_cases = []
        
        # Base metadata from query
        query_id = query_item.get('id', str(uuid.uuid4()))
        gold_sql = query_item.get('sql', '')
        complexity = query_item.get('complexity', 'unknown')
        tables = query_item.get('tables', [])
        
        # Check if this query has the new perturbation structure
        if 'generated_perturbations' in query_item:
            perturbations = query_item['generated_perturbations']
            
            # 1. Add original prompt
            original = perturbations.get('original', {})
            original_prompt = original.get('nl_prompt', query_item.get('nl_prompt', ''))
            
            if original_prompt:
                test_cases.append({
                    'prompt_id': f"{query_id}_original",
                    'prompt_text': original_prompt,
                    'sql': gold_sql,
                    'complexity': complexity,
                    'tables': tables,
                    'perturbation_type': 'original',
                    'perturbation_id': 0,
                    'metadata': {
                        'query_id': query_id,
                        'is_perturbed': False
                    }
                })
            
            # 2. Add each applicable perturbation
            single_perts = perturbations.get('single_perturbations', [])
            for pert in single_perts:
                if pert.get('applicable', False):
                    perturbed_prompt = pert.get('perturbed_nl_prompt')
                    if perturbed_prompt:
                        test_cases.append({
                            'prompt_id': f"{query_id}_pert_{pert['perturbation_id']}",
                            'prompt_text': perturbed_prompt,
                            'sql': gold_sql,  # Same gold SQL for all perturbations
                            'complexity': complexity,
                            'tables': tables,
                            'perturbation_type': pert.get('perturbation_name', 'unknown'),
                            'perturbation_id': pert.get('perturbation_id', -1),
                            'metadata': {
                                'query_id': query_id,
                                'is_perturbed': True,
                                'changes_made': pert.get('changes_made', ''),
                                'original_prompt': original_prompt
                            }
                        })
        
        else:
            # Fallback for simple format without perturbations
            nl_prompt = query_item.get('nl_prompt', query_item.get('prompt_text', ''))
            if nl_prompt:
                test_cases.append({
                    'prompt_id': str(query_id),
                    'prompt_text': nl_prompt,
                    'sql': gold_sql,
                    'complexity': complexity,
                    'tables': tables,
                    'perturbation_type': 'original',
                    'perturbation_id': 0,
                    'metadata': {
                        'query_id': query_id,
                        'is_perturbed': False
                    }
                })
        
        return test_cases

    def _log_record(self, record: Dict[str, Any]):
        """Append-only logging."""
        with open(self.output_path, 'a') as f:
            f.write(json.dumps(record) + "\n")
    
    def _construct_full_prompt(self, nl_query: str) -> str:
        """
        Construct a complete prompt with schema context and instructions.
        
        Args:
            nl_query: The natural language query description.
            
        Returns:
            Complete prompt string ready for LLM.
        """
        schema_text = self._format_schema_text()
        
        prompt = f"""{schema_text}

Generate a SQL query for the following request. Return ONLY the SQL statement, no explanations or markdown formatting.

Request: {nl_query}

SQL:"""
        
        return prompt
    
    def _format_schema_text(self) -> str:
        """
        Format the database schema as text for LLM prompt context.
        
        Returns:
            Formatted string describing tables, columns, types, and foreign keys.
        """
        schema_lines = ["Database Schema:", ""]
        
        # Format tables and columns
        schema_lines.append("TABLES:")
        for table_name, columns in self.schema.items():
            col_defs = []
            for col_name, col_type in columns.items():
                col_defs.append(f"{col_name} {col_type.upper()}")
            schema_lines.append(f"  - {table_name} ({', '.join(col_defs)})")
        
        schema_lines.append("")
        schema_lines.append("FOREIGN KEY RELATIONSHIPS:")
        
        # Format foreign keys (deduplicate bidirectional relationships)
        seen_fks = set()
        for (left_table, right_table), (left_key, right_key) in self.foreign_keys.items():
            # Create a canonical representation to avoid duplicates
            fk_tuple = tuple(sorted([(left_table, left_key), (right_table, right_key)]))
            if fk_tuple not in seen_fks:
                seen_fks.add(fk_tuple)
                schema_lines.append(f"  - {left_table}.{left_key} -> {right_table}.{right_key}")
        
        return "\n".join(schema_lines)
