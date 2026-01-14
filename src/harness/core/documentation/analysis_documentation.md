# Analysis Script Documentation

## Overview

The [analyze_results.py](file:///Users/obby/Documents/experiment/gemini-cli/sql-generator/src/harness/core/analyze_results.py) script provides comprehensive statistical analysis and visualization of experiment results, generating academic-quality outputs suitable for research papers.

**Location**: [src/harness/core/analyze_results.py](file:///Users/obby/Documents/experiment/gemini-cli/sql-generator/src/harness/core/analyze_results.py)

---

## Usage

```bash
python src/harness/core/analyze_results.py <input_jsonl> <output_dir>
```

**Example**:
```bash
python src/harness/core/analyze_results.py \
  results/experiment_run1.jsonl \
  analysis_output/run1/
```

---

## Generated Outputs

The script creates three main directories:

### 📁 `figures/` - Visualizations (7 charts)

1. **`model_accuracy_comparison.png`**
   - Bar chart comparing accuracy across models
   - Shows percentage accuracy with value labels
   - Useful for: Model comparison in papers

2. **`model_similarity_boxplot.png`**
   - Box plots of TED similarity scores by model
   - Shows distribution, quartiles, and outliers
   - Useful for: Understanding score variance

3. **`perturbation_accuracy.png`**
   - Horizontal bar chart of accuracy per perturbation type
   - Original prompt highlighted in green
   - Useful for: Robustness analysis

4. **`model_perturbation_heatmap.png`**
   - 2D heatmap: Models × Perturbation Types
   - Color-coded accuracy (red-yellow-green scale)
   - Useful for: Identifying model-specific weaknesses

5. **`complexity_accuracy_trend.png`**
   - Line plot showing accuracy degradation with complexity
   - Ordered from simple → advanced queries
   - Useful for: Demonstrating difficulty scaling

6. **`failure_distribution.png`**
   - Pie chart of failure types (parse error, mismatch, etc.)
   - Useful for: Error analysis

7. **`correlation_heatmap.png`**
   - Correlation matrix for key metrics
   - Useful for: Understanding metric relationships

### 📊 [tables/](file:///Users/obby/Documents/experiment/gemini-cli/sql-generator/src/metrics/execution_metric.py#17-21) - Statistical Tables

#### CSV Tables (6 files)

1. **`summary_statistics.txt`**
   ```
   Total Records: 300
   Models Tested: 3
   Overall Accuracy: 62.00%
   Mean Similarity Score: 0.6482
   ```

2. **`model_performance.csv`**
   | model_name | Total Tests | Correct | Accuracy | Avg Similarity | Std Similarity |
   |------------|------------|---------|----------|----------------|----------------|
   | gpt-4o     | 113        | 69      | 61.06%   | 0.6511         | 0.2827         |

3. **`perturbation_performance.csv`**
   - Accuracy and similarity score per perturbation type
   - Sorted by accuracy (descending)

4. **`complexity_performance.csv`**
   - Performance metrics per complexity level
   - Ordered: simple → moderate → complex → advanced

5. **`failure_modes.csv`**
   - Count and percentage of each failure type

6. **`correlation_matrix.csv`**
   - Pearson correlations between metrics

#### LaTeX Tables (3 files - ready for academic papers)

1. **`table1_model_performance.tex`**
   - Model comparison in LaTeX format
   - Reference in paper: `\ref{tab:model_perf}`

2. **`table2_perturbation_robustness.tex`**
   - Perturbation analysis table
   - Reference: `\ref{tab:pert_robust}`

3. **`table3_complexity_analysis.tex`**
   - Complexity impact table
   - Reference: `\ref{tab:complexity}`

### 📄 `EXECUTIVE_SUMMARY.md`

Markdown report containing:
- Overall statistics
- Model performance comparison
- Top perturbations by accuracy
- Complexity impact analysis
- Failure breakdown
- List of all generated files

---

## Analysis Features

### 1. Summary Statistics
- Total records processed
- Number of unique models/perturbations/complexities
- Overall accuracy and similarity scores
- Failure counts and rates

### 2. Per-Model Analysis
- Test counts per model
- Accuracy percentage
- Mean and standard deviation of similarity scores
- Failure counts
- Comparative visualizations

### 3. Perturbation Robustness
- Accuracy per perturbation type
- Identifies which perturbations are most challenging
- Heatmap showing model-specific vulnerabilities
- Comparison against original (unperturbed) baseline

### 4. Query Complexity Analysis
- Performance degradation as complexity increases
- Trend visualization
- Statistical breakdown by complexity level

### 5. Failure Mode Analysis
- Distribution of failure types:
  - `none`: Success
  - `parse_error`: SQL parsing failed
  - `execution_error`: SQL execution failed
  - `mismatch`: Results don't match gold standard
  - `empty`: No SQL generated
- Helps identify common error patterns

### 6. Correlation Analysis
- Relationship between correctness and similarity scores
- Impact of perturbation type on performance
- Statistical validation of metrics

### 7. Academic Tables
- LaTeX-formatted tables ready for publications
- Follows academic formatting conventions
- Includes captions and labels

---

## Key Metrics Explained

### Accuracy
- **Definition**: Percentage of test cases where generated SQL matches gold SQL (execution-based)
- **Formula**: [(Correct / Total) × 100](file:///Users/obby/Documents/experiment/gemini-cli/sql-generator/src/harness/core/analyze_results.py#545-562)
- **Range**: 0% - 100%

### TED Similarity Score
- **Definition**: Tree Edit Distance normalized similarity
- **Formula**: `1 - (edit_distance / total_nodes)`
- **Range**: 0.0 (completely different) - 1.0 (identical)
- **Captures**: Structural similarity even when execution fails

### Failure Types
- **`none`**: Successful execution match
- **`parse_error`**: SQL could not be parsed
- **`execution_error`**: SQL valid but execution failed
- **`mismatch`**: SQL executed but results differ
- **`empty`**: No SQL generated (e.g., API error)

---

## Sample Workflow for Academic Paper

1. **Run Experiment**:
   ```bash
   python src/harness/run_experiment.py \
     --config experiments.yaml \
     --prompts dataset/current/nl_social_media_queries.json \
     --output results/full_run.jsonl
   ```

2. **Analyze Results**:
   ```bash
   python src/harness/core/analyze_results.py \
     results/full_run.jsonl \
     paper_outputs/
   ```

3. **Use in Paper**:
   - **Figures**: Import `figures/*.png` into paper
   - **Tables**: Copy LaTeX tables from `tables/*.tex`
   - **Statistics**: Reference numbers from `EXECUTIVE_SUMMARY.md`

### Example LaTeX Integration

```latex
\begin{figure}[h]
  \centering
  \includegraphics[width=0.8\textwidth]{figures/model_perturbation_heatmap.png}
  \caption{Model performance across perturbation types}
  \label{fig:heatmap}
\end{figure}

As shown in Table~\ref{tab:model_perf}, GPT-4o achieved 
61.06\% accuracy across all test cases...

\input{tables/table1_model_performance.tex}
```

---

## Customization

To modify the analysis, edit [analyze_results.py](file:///Users/obby/Documents/experiment/gemini-cli/sql-generator/src/harness/core/analyze_results.py):

### Add New Visualization
```python
def _plot_custom_analysis(self):
    fig, ax = plt.subplots(figsize=(10, 6))
    # Your custom plot code
    plt.savefig(self.figures_dir / "custom_plot.png", dpi=300)
```

### Add New Metric
```python
# In analyze_per_model_performance():
model_stats = self.df.groupby('model_name').agg({
    'your_metric': ['mean', 'std'],
    # ...
})
```

### Modify Color Schemes
```python
# At top of file:
sns.set_palette("Set2")  # Change to preferred palette
```

---

## Dependencies

Required packages (auto-installed from [requirements.txt](file:///Users/obby/Documents/experiment/gemini-cli/sql-generator/requirements.txt)):
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `matplotlib` - Plotting
- `seaborn` - Statistical visualizations
- `jinja2` - LaTeX table generation
- `tabulate` - Markdown table formatting

---

## Troubleshooting

### Issue: "No module named 'pandas'"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: Matplotlib warnings about seaborn style
**Solution**: These are cosmetic warnings and can be ignored. The style still applies correctly.

### Issue: Empty output directory
**Solution**: Check that input JSONL file exists and contains valid JSON records

### Issue: LaTeX tables not rendering
**Solution**: Ensure `jinja2` is installed (`pip install jinja2`)

---

## Performance

- **Small datasets** (< 1,000 records): < 5 seconds
- **Medium datasets** (1,000 - 10,000 records): 10-30 seconds
- **Large datasets** (> 10,000 records): 1-2 minutes

Memory usage scales linearly with dataset size.

---

## Testing

Test with synthetic data:
```bash
python test_analysis_script.py
```

This creates 300 sample records and validates all analysis features.
