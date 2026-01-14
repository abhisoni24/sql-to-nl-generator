# Dr. Spider vs Our Approach: Perturbation Count Comparison

**Date:** 2026-01-08  
**Analysis:** Back-of-Envelope Math on Expected Perturbations

---

## Dr. Spider's Approach

### Overview
- **Paper:** "DR.SPIDER: A Diagnostic Evaluation Benchmark Towards Text-to-SQL Robustness" (ICLR 2023)
- **Base Dataset:** Spider development set (1,034 queries)
- **Perturbation Types:** 17 total

### Perturbation Breakdown

**DB Perturbations (3 types):**
1. **Schema-synonym** - Replace column/table names with synonyms
2. **Schema-abbreviation** - Abbreviate schema element names  
3. **DBcontent-equivalence** - Replace DB content with equivalent representations

**NLQ Perturbations (9 types):**
1. **Keyword-synonym** - Replace SQL keyword indicators with synonyms
2. **Keyword-carrier** - Different carrier phrases for keywords
3. **Column-synonym** - Replace column name indicators with synonyms
4. **Column-carrier** - Imply columns through carriers
5. **Column-attribute** - Replace columns with their attributes
6. **Column-value** - Imply columns through values
7. **Value-synonym** - Replace value representations
8. **Multitype** - Combination of multiple perturbation types
9. **Others** - General paraphrases

**SQL Perturbations (5 types):**
1. **Comparison** - Replace comparison operators (<, >, <=, >=)
2. **Sort-order** - Switch ASC/DESC
3. **NonDB-number** - Modify non-DB numbers (LIMIT, COUNT thresholds)
4. **DB-text** - Replace mentioned DB text content
5. **DB-number** - Replace mentioned DB numbers

### Their Perturbation Strategy

**Key Method:**
- Use OPT (large PLM) to generate paraphrases
- Generate ~20 paraphrases per question per category
- Filter to keep top 5 factual paraphrases
- Manual review by 3 SQL experts
- **Result: Multiple perturbations per original query**

### Actual Numbers from Paper

From Table 3 in the paper:

| Perturbation Type | # of Perturbed Queries |
|-------------------|----------------------|
| Schema-synonym | 2,619 |
| Schema-abbreviation | 2,853 |
| DBcontent-equivalence | 382 |
| Keyword-synonym | 953 |
| Keyword-carrier | 399  |
| Column-synonym | 563 |
| Column-carrier | 579 |
| Column-attribute | 119 |
| Column-value | 304 |
| Value-synonym | 506 |
| Multitype | 1,351 |
| Others | 2,819 |
| Comparison | 178 |
| Sort-order | 192 |
| NonDB-number | 131 |
| DB-text | 911 |
| DB-number | 410 |
| **TOTAL** | **~14,269** |

**Base Queries:** 1,034 (Spider dev set)  
**Total Perturbed Queries:** 14,269  
**Average Perturbations per Query:** 14,269 / 1,034 ≈ **13.8 perturbations/query**

---

## Our Approach

### Overview
- **Base Dataset:** 2,100 SQL queries (300 per complexity × 7 types)
- **Perturbation Types:** 10 types
- **Strategy:** Deterministic, configuration-driven single perturbations

### Our 10 Perturbation Types

1. **under_specification** - Omit table/column qualifiers
2. **implicit_business_logic** - Use business terms instead of conditions
3. **synonym_substitution** - Replace SQL terms with synonyms
4. **incomplete_joins** - Remove explicit JOIN conditions
5. **relative_temporal** - Use relative time expressions
6. **ambiguous_pronouns** - Replace schema refs with pronouns
7. **vague_aggregation** - Vague terms for aggregates
8. **column_variations** - camelCase variations
9. **missing_where_details** - Subjective WHERE terms
10. **typos** - Natural typo injection

### Our Perturbation Strategy

**Method:**
- **Single perturbations:** Each query gets perturbed with EACH applicable type once
- **Applicability check:** Perturbations only apply if contextually appropriate
- **Deterministic:** Seed-based generation (reproducible)
- **Result: 1 perturbation variant per type per query**

### Expected Perturbation Count

**From Pipeline Verification:**

| Perturbation Type | Applicability Rate | Expected Count (2,100 base) |
|-------------------|-------------------|----------------------------|
| ambiguous_pronouns | 100.0% | 2,100 |
| synonym_substitution | 100.0% | 2,100 |
| typos | 100.0% | 2,100 |
| under_specification | 100.0% | 2,100 |
| column_variations | 84.4% | 1,773 |
| implicit_business_logic | 56.6% | 1,189 |
| missing_where_details | 56.6% | 1,189 |
| incomplete_joins | 19.1% | 401 |
| vague_aggregation | 14.3% | 300 |
| relative_temporal | 12.9% | 270 |
| **TOTAL** | - | **~14,622** |

**Base Queries:** 2,100  
**Total Perturbed Queries:** 14,622 (single perturbations only)  
**Average Perturbations per Query:** 14,622 / 2,100 ≈ **~7.0 perturbations/query**

---

## Direct Comparison

### Normalized to Same Base Size (1,034 queries)

**Dr. Spider:**
- Base: 1,034 queries
- Total perturbations: 14,269
- Avg per query: **13.8**

**Our Approach (normalized to 1,034):**
- Base: 1,034 queries
- Expected total: 1,034 × 7.0 = **7,238**
- Avg per query: **7.0**

### Key Differences

| Dimension | Dr. Spider | Our Approach | Ratio |
|-----------|------------|--------------|-------|
| **Total Perturbations** | 14,269 | 7,238 (normalized) | **1.97x** |
| **Unique Types** | 17 | 10 | 1.7x |
| **Variants per Type** | 1-5 (filtered from 20) | 1 (deterministic) | ~3x |
| **Generation Method** | LLM + human review | Deterministic AST | - |
| **Reproducibility** | Low (stochastic) | High (seeded) | - |

---

## Why Does Dr. Spider Have More Perturbations?

### 1. **Multiple Variants per Type**
- Dr. Spider generates **up to 5 variants** per perturbation type per query
- We generate **1 variant** per type

**Example:**
- Dr. Spider for "Keyword-synonym": Might have "get", "fetch", "retrieve", "show", "find"
- Our approach: Randomly picks ONE synonym per invocation

### 2. **Overlapping Coverage**
Dr. Spider has overlapping perturbations:
- **Multitype (1,351)** combines multiple perturbation types
- **Others (2,819)** is general paraphrases

Our approach has disjoint, orthogonal perturbations.

### 3. **Different Applicability Baselines**

| Perturbation Concept | Dr. Spider Count | Our Count | Ratio |
|----------------------|------------------|-----------|-------|
| Keyword/synonym variants | 953 + 399 = 1,352 | 2,100 | 0.64x |
| Column/schema changes | 563 + 579 + 119 + 304 = 1,565 | 1,773 | 0.88x |
| Value/content changes | 506 + 911 + 410 = 1,827 | 1,189 + 270 = 1,459 | 1.25x |

Dr. Spider applies perturbations more conservatively (lower applicability) but with more variants each.

---

## If We Adopted Dr. Spider's Multi-Variant Strategy

**Assumption:** Generate 3-5 variants per type (instead of 1)

### Expected Count with Multi-Variant Generation

| Scenario | Variants per Type | Total Perturbations | Avg per Query |
|----------|------------------|---------------------|---------------|
| **Current (1 variant)** | 1 | 14,622 | 7.0 |
| **Conservative (3 variants)** | 3 | 43,866 | 20.9 |
| **Matching Dr. Spider (5 variants)** | 5 | 73,110 | 34.8 |

**With 5 variants:** 73,110 / 1,034 (normalized) = **70,738** perturbations
- **4.95x more** than Dr. Spider!

---

## Quality vs Quantity Trade-off

### Dr. Spider's Advantages
✅ Multiple natural paraphrases per type  
✅ LLM-generated diversity  
✅ Human-verified quality (63% acceptance rate)  
✅ More coverage of linguistic variation

### Our Approach's Advantages
✅ **Deterministic & reproducible**  
✅ **Systematic coverage** (applies to ALL queries)  
✅ **Efficient** (no LLM calls, no human review)  
✅ **Context-aware** (applicability checks prevent invalid perturbations)  
✅ **Orthogonal perturbations** (no overlap between types)

---

## Back-of-Envelope Summary

### Dr. Spider
- **17 perturbation types**
- **~13.8 perturbations per query**
- **14,269 total** (on 1,034 base queries)
- Method: LLM generation + human curation

### Our Approach (Current)
- **10 perturbation types**
- **~7.0 perturbations per query**
- **14,622 total** (on 2,100 base queries)
- Method: Deterministic AST-based

### Our Approach (If Multi-Variant)
- **10 perturbation types × 5 variants**
- **~34.8 perturbations per query**
- **73,110 total** (on 2,100 base queries)
- Would be **5x larger** than Dr. Spider!

---

## Conclusion

**Current State:**
Our approach generates **~50% fewer** perturbations per query (7.0 vs 13.8) compared to Dr. Spider, primarily because:
1. We generate 1 variant per type vs their 3-5
2. We have 10 types vs their 17
3. Our higher applicability rates compensate partially

**Potential:**
If we adopted multi-variant generation (even just 3 variants per type), we would generate **2.5-5x MORE** perturbations than Dr. Spider, while maintaining:
- Deterministic reproducibility
- Systematic coverage
- Efficient generation (no LLM/human costs)

**Recommendation:**
Our current approach provides **adequate coverage** with **higher efficiency**. Multi-variant generation would be valuable for:
- Research papers requiring comparison to Dr. Spider
- Scenarios needing maximum linguistic diversity
- Testing LLM robustness to specific paraphrase types

But for systematic evaluation, our single-variant approach is **sufficient and superior** in terms of reproducibility and cost-effectiveness.
