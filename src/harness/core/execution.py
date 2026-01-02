"""
Execution Engine.
Orchestrates the generation and evaluation loop.
"""
import json
import os
import time
import uuid
from datetime import datetime
from typing import List, Dict, Any
from ..adapters.base import BaseModelAdapter
from .normalization import normalize_sql
from .evaluation import Evaluator

class ExecutionEngine:
    
    def __init__(self, adapter: BaseModelAdapter, run_id: str, output_path: str):
        self.adapter = adapter
        self.run_id = run_id
        self.output_path = output_path
        self.evaluator = Evaluator()
        
        # Determine batch size
        if adapter.model_family() == "open": # VLLM
            self.batch_size = 32
        else: # API
            self.batch_size = 5

    def execute_experiment(self, prompts_path: str):
        """
        Run the full experiment for the loaded adapter.
        
        Args:
            prompts_path: Path to input JSON/JSONL file.
        """
        
        # 1. Load Prompts
        # Support both the project's existing JSON format and requested JSONL
        prompts_data = self._load_prompts(prompts_path)
        print(f"Loaded {len(prompts_data)} prompts from {prompts_path}")

        # 2. Batching
        batches = [prompts_data[i:i + self.batch_size] for i in range(0, len(prompts_data), self.batch_size)]
        
        print(f"Processing {len(batches)} batches with size {self.batch_size}...")

        # 3. Execution Loop
        for batch in batches:
            prompt_texts = [p['prompt_text'] for p in batch]
            
            # Generate
            # "No retries unless explicitly configured" - adapter handles this (or doesn't)
            raw_outputs = self.adapter.generate(prompt_texts)
            
            # Process outputs
            for i, raw_output in enumerate(raw_outputs):
                prompt_item = batch[i]
                
                # Normalize
                normalized_sql = normalize_sql(raw_output)
                
                # Evaluate
                # Need gold sql from prompt item
                gold_sql = prompt_item.get('sql', '') # Assuming 'sql' key in input
                
                eval_result = self.evaluator.evaluate(gold_sql, normalized_sql)
                
                # Log Record
                record = {
                    "run_id": self.run_id,
                    "model_name": self.adapter.model_name(),
                    "model_family": self.adapter.model_family(),
                    "prompt_id": prompt_item.get('id', str(uuid.uuid4())),
                    "prompt_text": prompt_item['prompt_text'],
                    "prompt_metadata": prompt_item.get('metadata', {}),
                    "raw_output": raw_output,
                    "normalized_sql": normalized_sql,
                    "evaluation_result": {
                        "correctness": eval_result.execution_match, # Boolean as per req
                        "similarity_score": eval_result.similarity_score,
                        "failure_type": eval_result.failure_type
                    },
                    "decoding_config": self.adapter.decoding_config(),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                self._log_record(record)
                
    def _load_prompts(self, path: str) -> List[Dict[str, Any]]:
        """Load prompts from JSON or JSONL."""
        data = []
        with open(path, 'r') as f:
            if path.endswith('.jsonl'):
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
            else:
                # Assume standard JSON list
                content = json.load(f)
                # Map to standard interface if necessary. 
                # Existing social_media_queries.json has 'nl_prompt' and 'sql'.
                # We need 'prompt_text'
                for item in content:
                    # Adapt existing schema to harness schema
                    start_prompt = item.get('nl_prompt', '')
                    if not start_prompt and 'prompt_text' in item:
                        start_prompt = item['prompt_text']
                        
                    # Also support variations if this file contains them?
                    # For now, simplistic mapping.
                    item['prompt_text'] = start_prompt
                    data.append(item)
                    
        return data

    def _log_record(self, record: Dict[str, Any]):
        """Append-only logging."""
        with open(self.output_path, 'a') as f:
            f.write(json.dumps(record) + "\n")
