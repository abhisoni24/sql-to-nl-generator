# Experiment Results - Executive Summary

**Generated**: 2026-01-14 23:52:26

**Data Source**: experiment_logs/deepseek-full-perturbed/re_evaluated.jsonl

---

## 📊 Overall Statistics

- **Total Test Cases**: 16,142
- **Models Tested**: 1
- **Overall Accuracy**: 19.64%
- **Average Similarity Score**: 0.4742

## 🤖 Model Performance

| model_name                                  | Accuracy   |   Avg TED Score |
|:--------------------------------------------|:-----------|----------------:|
| deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct | 19.64%     |          0.4742 |

## 🔄 Perturbation Robustness

Top 10 Perturbation Types by Accuracy:

- **relative_temporal**: 40.60%
- **column_variations**: 31.62%
- **typos**: 31.38%
- **original**: 29.14%
- **under_specification**: 18.38%
- **synonym_substitution**: 12.64%
- **ambiguous_pronouns**: 12.20%
- **incomplete_joins**: 7.31%
- **missing_where_details**: 6.63%
- **implicit_business_logic**: 4.30%

## 📈 Query Complexity Impact

- **advanced**: 1.56%
- **aggregate**: 11.57%
- **delete**: 25.19%
- **insert**: 79.44%
- **join**: 5.22%
- **simple**: 24.09%
- **update**: 11.12%

## ⚠️ Failure Analysis

- **parse_error**: 6880 (42.62%)
- **mismatch**: 6091 (37.73%)

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
