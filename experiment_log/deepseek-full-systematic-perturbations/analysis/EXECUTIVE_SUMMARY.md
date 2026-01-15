# Experiment Results - Executive Summary

**Generated**: 2026-01-14 23:52:23

**Data Source**: experiment_logs/deepseek-full-nl/re_evaluated.jsonl

---

## 📊 Overall Statistics

- **Total Test Cases**: 15,622
- **Models Tested**: 1
- **Overall Accuracy**: 27.81%
- **Average Similarity Score**: 0.4391

## 🤖 Model Performance

| model_name                                  | Accuracy   |   Avg TED Score |
|:--------------------------------------------|:-----------|----------------:|
| deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct | 27.81%     |          0.4391 |

## 🔄 Perturbation Robustness

Top 10 Perturbation Types by Accuracy:

- **ambiguous_pronouns**: 46.00%
- **typos**: 43.10%
- **under_specification**: 31.90%
- **synonym_substitution**: 30.62%
- **incomplete_joins**: 28.43%
- **original**: 24.52%
- **column_variations**: 15.79%
- **implicit_business_logic**: 10.09%
- **missing_where_details**: 9.50%
- **vague_aggregation**: 5.00%

## 📈 Query Complexity Impact

- **advanced**: 1.60%
- **aggregate**: 8.38%
- **delete**: 35.89%
- **insert**: 90.60%
- **join**: 17.18%
- **simple**: 40.22%
- **update**: 24.87%

## ⚠️ Failure Analysis

- **parse_error**: 7723 (49.44%)
- **mismatch**: 3555 (22.76%)

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
