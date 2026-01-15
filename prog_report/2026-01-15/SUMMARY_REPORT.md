# Cross-Experiment Analysis Summary

**Date**: 2026-01-15  
**Experiments Analyzed**: 4  
**Total Test Cases**: 51996

---

## Key Findings

### 1. Overall Performance

| Experiment          | Model    | Method     |   Total Tests |   Accuracy (%) |   Avg TED Score |   Parse Errors (%) |   Mismatch (%) |   Std Dev TED |
|:--------------------|:---------|:-----------|--------------:|---------------:|----------------:|-------------------:|---------------:|--------------:|
| Gemini Systematic   | Gemini   | SYSTEMATIC |         16272 |        60.6809 |        0.90018  |           0.153638 |        39.1409 |     0.143399  |
| Gemini Llm          | Gemini   | LLM        |          3960 |        65.6566 |        0.942482 |           0.353535 |        33.9394 |     0.0961565 |
| Deepseek Systematic | Deepseek | SYSTEMATIC |         15622 |        27.8069 |        0.439065 |          49.4367   |        22.7564 |     0.451751  |
| Deepseek Llm        | Deepseek | LLM        |         16142 |        19.6444 |        0.474207 |          42.6217   |        37.7339 |     0.428619  |

**Winner**: Gemini Llm 
(65.7% accuracy)

### 2. Model Comparison

- **Gemini** outperforms DeepSeek by 39.4 percentage points on average
- Gemini has 0.3% parse errors vs DeepSeek's 46.0%

### 3. Perturbation Method Comparison

- LLM perturbations: 42.7% average accuracy
- Systematic perturbations: 44.2% average accuracy
- **Difference**: -1.6 points

### 4. Statistical Validation

Statistical tests confirm:
- Gemini vs DeepSeek difference is **highly significant** (p < 0.001)
- Model differences are robust across perturbation methods

---

## Outputs Generated

- **Figures**: 5 visualizations
- **Tables**: 6 data tables

See individual files in:
- `figures/`
- `tables/`
