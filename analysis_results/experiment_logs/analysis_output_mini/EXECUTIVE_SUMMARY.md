# Experiment Results - Executive Summary

**Generated**: 2026-01-14 00:55:32

**Data Source**: experiment_logs/mini_run_20260114_005503.jsonl

---

## 📊 Overall Statistics

- **Total Test Cases**: 53
- **Models Tested**: 1
- **Overall Accuracy**: 3.77%
- **Average Similarity Score**: 0.1739

## 🤖 Model Performance

| model_name           | Accuracy   |   Avg TED Score |
|:---------------------|:-----------|----------------:|
| gemini-2.0-flash-exp | 3.77%      |          0.1739 |

## 🔄 Perturbation Robustness

Top 10 Perturbation Types by Accuracy:

- **original**: 14.29%
- **under_specification**: 14.29%
- **ambiguous_pronouns**: 0.00%
- **column_variations**: 0.00%
- **implicit_business_logic**: 0.00%
- **incomplete_joins**: 0.00%
- **missing_where_details**: 0.00%
- **relative_temporal**: 0.00%
- **synonym_substitution**: 0.00%
- **typos**: 0.00%

## 📈 Query Complexity Impact

- **advanced**: 0.00%
- **aggregate**: 28.57%
- **delete**: 0.00%
- **insert**: 0.00%
- **join**: 0.00%
- **simple**: 0.00%
- **update**: 0.00%

## ⚠️ Failure Analysis

- **empty**: 42 (79.25%)
- **mismatch**: 9 (16.98%)

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
