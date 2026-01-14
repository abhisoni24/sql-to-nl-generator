# Experiment Results - Executive Summary

**Generated**: 2026-01-14 02:10:36

**Data Source**: experiment_logs/fixed_multi_model_run.jsonl

---

## 📊 Overall Statistics

- **Total Test Cases**: 212
- **Models Tested**: 4
- **Overall Accuracy**: 39.62%
- **Average Similarity Score**: 0.8164

## 🤖 Model Performance

| model_name                 | Accuracy   |   Avg TED Score |
|:---------------------------|:-----------|----------------:|
| Qwen/Qwen2.5-0.5B-Instruct | 18.87%     |          0.5574 |
| claude-haiku-4-5-20251001  | 39.62%     |          0.9055 |
| gemini-2.5-flash-lite      | 52.83%     |          0.9164 |
| gpt-4o                     | 47.17%     |          0.8864 |

## 🔄 Perturbation Robustness

Top 10 Perturbation Types by Accuracy:

- **vague_aggregation**: 75.00%
- **column_variations**: 50.00%
- **incomplete_joins**: 50.00%
- **original**: 46.43%
- **typos**: 46.43%
- **ambiguous_pronouns**: 39.29%
- **synonym_substitution**: 32.14%
- **under_specification**: 32.14%
- **implicit_business_logic**: 31.25%
- **missing_where_details**: 31.25%

## 📈 Query Complexity Impact

- **advanced**: 33.33%
- **aggregate**: 96.43%
- **delete**: 75.00%
- **insert**: 0.00%
- **join**: 75.00%
- **simple**: 0.00%
- **update**: 0.00%

## ⚠️ Failure Analysis

- **mismatch**: 111 (52.36%)
- **parse_error**: 17 (8.02%)

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
