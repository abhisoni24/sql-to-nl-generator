# Progress Report: SDT Engine Refactor
**Date:** 2026-01-07
**Objective:** Refactor `sql-to-nl-generator` to use a deterministic, configuration-driven "Syntax-Directed Translation" (SDT) engine.

## 1. Process Overview

The goal was to replace the existing random-based perturbation logic with a deterministic system controlled by a "Bit-Vector" configuration. This required defining specific perturbation types, refactoring the core renderer, and updating the experiment harness to utilize the new capabilities systematically.

### Step 1: Definition of Perturbation Categories
**Input:** `debug_files/llm_clients/cache.py` (contained the definitions).
**Action:** Identified 10 distinct perturbation types:
1.  Under Specification
2.  Implicit Business Logic
3.  Synonym Substitution
4.  Incomplete Joins
5.  Relative Temporal
6.  Ambiguous Pronouns
7.  Vague Aggregation
8.  Column Variations
9.  Missing WHERE Details
10. Typos

**Implementation:** Defined an `Enum` called `PerturbationType` in `src/core/nl_renderer.py` to formally represent these categories.

### Step 2: Refactoring `SQLToNLRenderer`
**Goal:** Make rendering deterministic based on a seed and configuration.
**Action:**
- Introduced `PerturbationConfig` dataclass to hold the active perturbation flags and a master `seed`.
- Removed all `import random` usage.
- Implemented a `_get_rng(context)` helper that creates a local `random.Random` instance seeded by `f"{config.seed}_{context}"`. This ensures that even if we add new calls or change order in one part of the code, other parts remain stable relative to their context strings.
- Implemented modular rendering methods (`_render_table`, `_render_column`, etc.) that check `config.is_active(Type)` before applying changes.

**Roadblock 1: Complex File Edits**
- **Issue:** Using `replace_file_content` to essentially rewrite the entire class structure of `nl_renderer.py` failed because the tool couldn't match the context reliably for such a large change.
- **Alternative:** Apply small chunked edits.
- **Decision:** Use `write_to_file` to completely overwrite the file.
- **Reasoning:** The refactor was sweeping (changing `__init__`, signature of `render`, and almost all helper methods). Cleanly overwriting guaranteed the new structure was correct without lingering legacy code or merge conflicts.

### Step 3: Scaling the Harness
**Goal:** Update `src/harness/run_experiment.py` to generate the dataset systematically.
**Action:**
- Implemented `expand_dataset` function.
- Logic: For each input SQL, generate 11 versions: 1 Vanilla + 10 versions where exactly one perturbation bit is flipped on.
- This creates the requested "Bit-Vector" driven dataset.

**Roadblock 2: Environment Dependencies**
- **Issue:** When verifying the harness with a dry run, the script crashed because it imported `vllm` (via `ExecutionEngine` -> `Adapter`), and the local python environment (Python 3.9) had a version mismatch or missing dependencies for `vllm`.
- **Alternative:** Fix the environment (pip install).
- **Decision:** Use Lazy Imports.
- **Reasoning:** Fixing the ML environment can be time-consuming and might break other things. The task was to verify the *data generation* logic (`expand_dataset`), which does not depend on `vllm`. By moving the heavy imports inside `main()` (after the expansion step), I allowed the verification to proceed and the expansion logic to be robust in lightweight environments.

### Step 4: Verification
**Action:**
- Created `src/tests/test_renderer.py`.
- Verified determinism: Same seed = Identical output. Different seed = Different output.
- Verified perturbation logic: Checked specific output strings for expected changes (e.g., "typo" presence).
- Verified expansion: Ran `run_experiment.py` with dummy data and confirmed output file creation with 11 variations.

## 2. Conclusion
The system successfully implements the SDT approach. The randomness is now fully controlled, and the experiment harness can systematically generate the required benchmark data.

## 3. Architecture Correction (User Feedback)
**Feedback:** Harness should not handle generation; logic should be in `main.py`. Applicability checks were missing.
**Action:**
- Reverted `src/harness/run_experiment.py` to remove expansion logic.
- Implementation `is_applicable(ast, type)` in `nl_renderer.py`.
- Created `main.py` to orchestrate `generate -> render -> save` pipeline.
- Generated final `dataset/current/nl_social_media_queries.json` (2,100 items).

## 4. Current Pipeline State

**Final Architecture:**
```
SQLQueryGenerator -> SQLToNLRenderer (with PerturbationConfig) -> JSON Output
```

**Output Format:**
Each entry contains:
- Base SQL query
- Vanilla NL prompt (no perturbations)
- 10 single-perturbation variations with applicability flags
- Metadata: applicability rates, length impact

**Example Entry (Simple Complexity):**
```json
{
  "id": 1,
  "complexity": "simple",
  "sql": "SELECT u1.email FROM users AS u1 WHERE u1.id = 42",
  "generated_perturbations": {
    "original": {
      "nl_prompt": "Get u1.email from users (as u1) where u1.id equals 42."
    },
    "single_perturbations": [
      {
        "perturbation_name": "under_specification",
        "applicable": true,
        "perturbed_nl_prompt": "Get email from the table where id equals 42."
      },
      {
        "perturbation_name": "typos",
        "applicable": true,
        "perturbed_nl_prompt": "Get u1.email from usrs where u1.id eqals 42."
      }
    ]
  }
}
```

**Key Metrics from Analysis:**
- Total queries: 2,100 (300 per complexity type)
- Applicability rates: `ambiguous_pronouns` (100%), `incomplete_joins` (19.4%), `relative_temporal` (13%)
- Length impacts: `incomplete_joins` (-5.4 words), `ambiguous_pronouns` (+0.9 words)

