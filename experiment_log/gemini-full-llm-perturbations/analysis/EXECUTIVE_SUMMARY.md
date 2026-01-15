# Experiment Results - Executive Summary

**Generated**: 2026-01-15 02:13:00

**Data Source**: experiment_log/gemini-full-llm-perturbations/re_evaluated.jsonl

---

## 📊 Overall Statistics

- **Total Test Cases**: 3,960
- **Models Tested**: 1
- **Overall Accuracy**: 65.66%
- **Average Similarity Score**: 0.9425

## 🤖 Model Performance

| model_name            | Accuracy   |   Avg TED Score |
|:----------------------|:-----------|----------------:|
| gemini-2.5-flash-lite | 65.66%     |          0.9425 |

## 🔄 Perturbation Robustness

Top 10 Perturbation Types by Accuracy:

- **synonym_substitution**: 88.72%
- **typos**: 83.89%
- **original**: 83.55%
- **implicit_business_logic**: 82.96%
- **relative_temporal**: 80.65%
- **column_variations**: 74.11%
- **missing_where_details**: 57.25%
- **ambiguous_pronouns**: 52.87%
- **incomplete_joins**: 52.35%
- **under_specification**: 8.87%

## 📈 Query Complexity Impact

- **join**: 57.78%
- **simple**: 69.04%

## ⚠️ Failure Analysis

- **mismatch**: 1344 (33.94%)
- **parse_error**: 14 (0.35%)
- **empty**: 2 (0.05%)

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
