# Experiment Results - Executive Summary

**Generated**: 2026-01-14 23:38:55

**Data Source**: experiment_logs/full_gemini_run_re_evaluated.jsonl

---

## 📊 Overall Statistics

- **Total Test Cases**: 16,272
- **Models Tested**: 1
- **Overall Accuracy**: 60.68%
- **Average Similarity Score**: 0.9002

## 🤖 Model Performance

| model_name            | Accuracy   |   Avg TED Score |
|:----------------------|:-----------|----------------:|
| gemini-2.5-flash-lite | 60.68%     |          0.9002 |

## 🔄 Perturbation Robustness

Top 10 Perturbation Types by Accuracy:

- **relative_temporal**: 78.52%
- **synonym_substitution**: 76.14%
- **original**: 73.49%
- **typos**: 72.48%
- **implicit_business_logic**: 69.01%
- **column_variations**: 65.21%
- **ambiguous_pronouns**: 58.26%
- **missing_where_details**: 38.14%
- **incomplete_joins**: 35.66%
- **under_specification**: 35.63%

## 📈 Query Complexity Impact

- **advanced**: 22.01%
- **aggregate**: 23.00%
- **delete**: 74.62%
- **insert**: 100.00%
- **join**: 56.77%
- **simple**: 69.04%
- **update**: 89.26%

## ⚠️ Failure Analysis

- **mismatch**: 6369 (39.14%)
- **parse_error**: 25 (0.15%)
- **empty**: 4 (0.02%)

## 📁 Generated Outputs

### Figures

- `complexity_accuracy_trend.png`
- `correlation_heatmap.png`
- `failure_distribution.png`
- `model_accuracy_comparison.png`
- `model_perturbation_heatmap.png`
- `model_similarity_boxplot.png`
- `perturbation_accuracy.png`

### Tables

- `complexity_performance.csv`
- `correlation_matrix.csv`
- `failure_modes.csv`
- `model_performance.csv`
- `perturbation_performance.csv`
- `summary_statistics.txt`
- `table1_model_performance.tex`
- `table2_perturbation_robustness.tex`
- `table3_complexity_analysis.tex`
