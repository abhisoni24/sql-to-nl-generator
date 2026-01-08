# Repository Cleanup Summary
**Date:** 2026-01-08  
**Action:** Archived debug files and temporary scripts

## Files Archived

### Moved to `debug_files/others/`

1. **debug_insert.py** (1.9 KB)
   - Debug script to inspect INSERT AST structure
   - Used during INSERT vanilla rendering fix
   - No longer needed in main directory

2. **patch_insert.py** (3.7 KB)
   - Automated patch script for INSERT rendering
   - Temporary solution during development
   - No longer needed in main directory

3. **extract_samples.py** (937 bytes)
   - Script to extract sample entries from dataset
   - Used for quality evaluation
   - Useful for future debugging, archived for clean main directory

4. **sample_entries.json** (28.9 KB)
   - Sample dataset entries from quality evaluation
   - Historical record of evaluation process
   - Archived from prog_report/

## Current Repository Structure

```
sql-generator/
├── main.py                     # Main dataset generation orchestrator
├── experiments.yaml            # Experiment configuration  
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── .env                        # Environment variables
├── .gitignore                  # Git ignore rules
│
├── src/                        # Source code
│   ├── core/                   # Core modules
│   │   ├── generator.py        # SQL query generator
│   │   ├── nl_renderer.py      # SQL-to-NL renderer (SDT engine)
│   │   └── schema.py           # Database schema
│   ├── scripts/                # Utility scripts
│   │   ├── analyze_results.py  # Dataset analysis
│   │   └── generate_benchmark.py
│   ├── harness/                # Experiment harness
│   └── tests/                  # Unit tests
│
├── dataset/                    # Generated datasets
│   ├── current/                # Latest production dataset
│   │   ├── nl_social_media_queries.json        (8.7 MB)
│   │   ├── nl_social_media_queries_perturbed.json (13 MB)
│   │   └── raw_social_media_queries.json       (426 KB)
│   └── archive/                # Historical datasets
│       └── 2025/
│
├── prog_report/                # Progress reports & documentation
│   ├── complete_implementation_report.md
│   ├── final_quality_report.md
│   ├── improvement_results.md
│   ├── insert_fix_analysis.md
│   ├── quality_evaluation_report.md
│   └── sdt_refactor_report.md
│
├── debug_files/                # Debug & test scripts (archived)
│   ├── llm_clients/
│   └── others/                 # Newly archived files here
│       ├── debug_insert.py     ← MOVED
│       ├── patch_insert.py     ← MOVED
│       ├── extract_samples.py  ← MOVED
│       ├── sample_entries.json ← MOVED
│       └── ... (28 other debug files)
│
├── visualizations_verify/      # Analysis visualizations
│   ├── perturbation_applicability.png
│   ├── perturbation_length_impact.png
│   └── ...
│
└── analysis_results/           # Analysis outputs
```

## Benefits

✅ **Clean Root Directory**: Only essential production files remain  
✅ **Clear Organization**: Debug/temporary files properly archived  
✅ **Preserved History**: All debug files kept for future reference  
✅ **Professional Structure**: Easy for new contributors to navigate  
✅ **Git Cleanliness**: No clutter in version control

## Next Steps (Recommended)

1. ✅ Update `.gitignore` to exclude `debug_files/` if desired
2. ✅ Verify all tests still run correctly
3. ✅ Document the cleanup in commit message
4. ✅ Consider adding a CONTRIBUTING.md for folder structure guidelines

## Archived File Purpose Reference

| File | Original Purpose | Keep For |
|------|-----------------|----------|
| debug_insert.py | INSERT AST inspection | Future AST debugging |
| patch_insert.py | Automated INSERT fix | Reference implementation |
| extract_samples.py | Quality evaluation | Future evaluations |
| sample_entries.json | Evaluation records | Historical tracking |

All files have been preserved for potential future use while keeping the main directory clean and professional.
