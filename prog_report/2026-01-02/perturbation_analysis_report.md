# Perturbation Analysis Report

## 1. Executive Summary

- **Total Attempted:** 2,100
- **Total Processed Queries:** 2,100
- **Failed Queries:** 0 (0.00% failure rate)

The project to generate realistic prompt perturbations using Gemini 2.5 Flash Lite is **100% complete**. All 2,100 SQL queries across 7 complexity categories have been successfully processed, with 10 single perturbations and 1 compound perturbation generated for each.

## 2. Applicability of Perturbations

The model evaluated 10 distinct perturbation types for each query. The rates below reflect how often each type was deemed "applicable" to a given natural language prompt.

| Perturbation Type | Applicable Count | Not Applicable | Rate (%) |
| :--- | :--- | :--- | :--- |
| **Typos** | 2,100 | 0 | 100.0% |
| **Synonym Substitution** | 2,089 | 11 | 99.5% |
| **Column Variations** | 2,078 | 22 | 99.0% |
| **Under Specification** | 2,008 | 92 | 95.6% |
| **Ambiguous Pronouns** | 1,811 | 289 | 86.2% |
| **Implicit Business Logic** | 1,420 | 680 | 67.6% |
| **Missing WHERE Details** | 1,312 | 788 | 62.5% |
| **Relative Temporal** | 500 | 1,600 | 23.8% |
| **Incomplete Joins** | 424 | 1,676 | 20.2% |
| **Vague Aggregation** | 300 | 1,800 | 14.3% |

### Key Observations
1.  **Universal Noise:** "Typos", "Synonyms", and "Column Variations" are universal perturbation vectors, applicable to virtually any query.
2.  **Structural Dependencies:** "Incomplete Joins" (20.2%) and "Vague Aggregation" (14.3%) strongly correlate with the specific `JOIN` and `AGGREGATE` complexity classes in the dataset.
3.  **High Ambiguity:** Over 95% of queries allowed for "Under Specification", confirming that real-world prompts often lack explicit schema details.

## 3. Complexity Distribution

The final dataset is perfectly balanced.

| Complexity | Count | Status |
| :--- | :--- | :--- |
| **Simple** | 300 | ✅ Complete |
| **Join** | 300 | ✅ Complete |
| **Aggregate** | 300 | ✅ Complete |
| **Advanced** | 300 | ✅ Complete |
| **Insert** | 300 | ✅ Complete |
| **Update** | 300 | ✅ Complete |
| **Delete** | 300 | ✅ Complete |

## 4. Compound Perturbations

The model created one "compound" version per query, applying 2 to 5 perturbations simultaneously.

*   **Average Perturbations per Compound:** 3.26

### Most Frequent Combinations

| Count | Combination |
| :--- | :--- |
| 625 | synonym_substitution, typos, under_specification |
| 193 | relative_temporal, typos, under_specification |
| 135 | typos, under_specification, vague_aggregation |
| 128 | column_variations, typos, under_specification |
| 115 | column_variations, synonym_substitution, typos, under_specification |

**Insight:** The dominant pattern (occurring in ~30% of cases) is **Synonyms + Typos + Under-specification**. This suggests the most "natural" form of messy input is a user who types quickly, uses loose terminology, and assumes the AI knows the schema.

## 5. Visualizations

![Perturbation Applicability Chart](images/applicability_chart.png)

![Top Compound Combinations](images/top_compounds_chart.png)

### Processing Flow
**Total Queries: 2100** &rarr; **Processing Status** &rarr; **Success: 2100 (100%)** &rarr; **Data Ready for Training/Testing**
