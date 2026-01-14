# Perturbation Logic Quality Evaluation Report
**Date:** 2026-01-08  
**Scope:** Analysis of 7 sample entries (one per complexity type) across 10 perturbation types

## Executive Summary

After analyzing representative samples from each SQL complexity type, I have identified **critical semantic preservation issues** in the current perturbation logic. The primary concern is that several perturbations sacrifice too much semantic information, making it impossible for LLMs to reconstruct the original SQL. This violates the stated goal: perturbations should represent realistic natural language variations that preserve enough intent for SQL reconstruction.

**Severity Classification:**
- 🔴 **CRITICAL**: Renders prompts unusable for LLM SQL generation
- 🟡 **MODERATE**: Causes ambiguity but may work with context
- 🟢 **MINOR**: Minor issues, mostly acceptable

---

## Detailed Analysis by Perturbation Type

### 1. Ambiguous Pronouns 🔴 **CRITICAL ISSUE**

**Current Behavior:**
Replaces ALL schema elements (tables, columns, aliases) with generic pronouns ("it", "that table", "that field").

**Example (Simple):**
```
Original: "Get u1.email, u1.is_verified from users (as u1) where u1.username not equals test..."
Perturbed: "Get it, that field from that table where that field not equals test..."
```

**Problem:**
- **Complete loss of semantic value**: No table names, no column names, no aliases
- An LLM cannot possibly know:
  - Which table to query
  - Which columns to select
  - Which column to filter on
- This is equivalent to asking: "Get something from somewhere where something equals something"

**Realistic User Behavior:**
Users might use pronouns for *previously mentioned* entities, but never for the first mention:
- ✅ "Get users and their comments. Show me all columns from *it*."
- ❌ "Get it from that table"

**Proposed Solution:**
1. **Selective Replacement**: Only replace entities after first mention
2. **Context Preservation**: Keep at least one concrete reference per entity type
3. **Example Fix**:
   ```
   "Get email and verification status from users where that username field is not 'test'"
   ```
   This preserves the table name but pronoun-izes some columns.

---

### 2. Under-Specification 🟡 **MODERATE ISSUE**

**Current Behavior:**
Removes table qualifiers and uses "the table" instead of table names.

**Example (Join):**
```
Original: "Get all columns from users (as u1) LEFT joined with comments (as c3)..."
Perturbed: "Get all columns from the table LEFT joined with the table..."
```

**Problem:**
- **Ambiguous in multi-table contexts**: "the table" repeated twice is confusing
- For simple single-table queries, this works reasonably well
- For joins, this creates severe ambiguity

**Realistic User Behavior:**
Users might omit aliases or qualifiers, but rarely use "the table" when multiple tables exist:
- ✅ "Get email from users where username is not test"
- ❌ "Get columns from the table joined with the table"

**Proposed Solution:**
1. **Preserve table names in multi-table contexts**
2. **Only remove qualifiers/aliases** in simple queries
3. **Example Fix (Join)**:
   ```
   "Get all columns from users left joined with comments"
   ```

---

### 3. INSERT/UPDATE/DELETE Rendering 🔴 **CRITICAL ISSUE**

**Current Behavior:**
Vanilla prompts for INSERT/UPDATE/DELETE are overly simplistic and lose all semantic detail.

**Examples:**
```
INSERT: "Insert into table." (loses: columns, values, including NOW())
UPDATE: "Update follows." (loses: SET clause, WHERE clause, NOW())
DELETE: "Delete from likes." (loses: WHERE clause)
```

**Problem:**
- **Catastrophic information loss** even in vanilla prompts
- Perturbations have nothing meaningful to perturb
- These prompts are essentially unusable

**Realistic User Behavior:**
Users would never describe these operations so minimally:
- ❌ "Insert into table"
- ✅ "Insert a new follow relationship with follower 362 and followee 303 timestamped now"

**Proposed Solution:**
1. **Fix base renderer** to properly handle INSERT/UPDATE/DELETE
2. **Include essential details**:
   - INSERT: columns and values
   - UPDATE: SET assignments and WHERE conditions
   - DELETE: WHERE conditions
3. **Example Fix (INSERT)**:
   ```
   Original: "Insert into follows with follower_id 362, followee_id 303, and timestamp now"
   Typos: "Inert into follows with follwer_id 362..."
   ```

---

### 4. Vague Aggregation 🟡 **MODERATE ISSUE**

**Current Behavior:**
Replaces "GROUP BY" with "for each" - which is actually good!

**Example (Aggregate):**
```
Original: "...grouped by l1.liked_at"
Perturbed: "...for each l1.liked_at"
```

**Problem:**
- Implementation seems limited to GROUP BY
- Doesn't handle aggregate function names (COUNT, SUM, AVG, etc.)
- "expression" appears in vanilla prompt for `COUNT(*)` which loses meaning

**Realistic User Behavior:**
Users do say "for each" for GROUP BY, and use vague terms for aggregates:
- ✅ "Show the count for each date" → "Show the number for each date"
- ✅ "Get the sum of likes" → "Get the total likes"

**Proposed Solution:**
1. **Extend to aggregate functions**:
   - COUNT(*) → "count" / "number" / "total"
   - SUM() → "total" / "sum up"
   - AVG() → "average"
   - MIN/MAX → "smallest" / "largest"
2. **Fix "expression" rendering**: Should be "count of all rows" or similar

---

### 5. Implicit Business Logic 🟡 **MODERATE ISSUE**

**Current Behavior:**
Replaces specific values with business logic terms like "is valid".

**Example (Advanced):**
```
Original: "...on f1.followee_id equals f2.follower_id..."
Perturbed: "...on f1.followee_id is valid..."
```

**Problem:**
- "is valid" replacement breaks JOIN conditions
- Only makes sense for WHERE clause filtering
- Current applicability check looks for WHERE but logic applies more broadly

**Realistic User Behavior:**
Users do use business terms, but appropriately:
- ✅ "where user status is active" (instead of "status = 1")
- ❌ "on followee_id is valid" (breaks join semantics)

**Proposed Solution:**
1. **Restrict to WHERE clauses only**
2. **Use contextual business terms**:
   - Numeric comparisons → "high", "low", "valid range"
   - String patterns → "valid", "matches format"
3. **Never apply to JOIN conditions**

---

### 6. Column Variations 🟢 **MINOR ISSUE**

**Current Behavior:**
Changes snake_case to camelCase (e.g., `user_id` → `userId`).

**Example:**
```
Original: "...c3.user_id..."
Perturbed: "...c3.userId..."
```

**Problem:**
- Generally acceptable and realistic
- Minor issue: sometimes introduces spacing errors ("liked at" instead of "liked_at")

**Proposed Solution:**
- Fix spacing handling in camelCase conversion
- Consider adding other variations: PascalCase, kebab-case

---

### 7. Missing WHERE Details 🟡 **MODERATE ISSUE**

**Current Behavior:**
Replaces specific values/conditions with subjective terms.

**Example:**
```
Original: "...where username not equals test..."
Perturbed: "...where username not equals test..." (NO CHANGE!)
```

**Problem:**
- Implementation appears incomplete or not working
- Should replace "test" with something like "the invalid value" or "certain username"

**Proposed Solution:**
1. **Actually implement the transformation**
2. **Replace literal values** with subjective descriptors:
   - "where id = 42" → "where id is the target one"
   - "where username like '%test%'" → "where username matches the pattern"

---

### 8. Synonym Substitution 🟢 **ACCEPTABLE**

**Current Behavior:**
Replaces keywords: "Get" → "Find", "joined" → "combined", "grouped" → "categorized".

**Example:**
```
Original: "Get...from users..."
Perturbed: "Find...from users..."
```

**Assessment:**
- Works well and is realistic
- Could be expanded with more synonym options

---

### 9. Incomplete Joins 🟢 **ACCEPTABLE**

**Current Behavior:**
Removes explicit JOIN conditions, using "with" instead of "joined on".

**Example:**
```
Original: "...LEFT joined with comments (as c3) on u1.id equals c3.user_id"
Perturbed: "...with comments (as c3)"
```

**Assessment:**
- Realistic: users do say "get users with their comments"
- Applicability is correct (only applies to JOIN queries)

---

### 10. Typos 🔴 **CRITICAL ISSUE**

**Current Behavior:**
Injects random character-level typos.

**Examples:**
```
"users" → "urss" / "usrs"
"LEFT" → "FF"
"equals" → "eqals" / "equu"
"grouped by" → "groupupuped by"
"Insert into table" → "Insert tt tabb"
```

**Problem:**
- **Overly aggressive**: Multiple typos per prompt
- **Unnatural patterns**: "groupupuped", "FF joined"
- **Loss of meaning**: "Insert tt tabb" is unintelligible
- **Too clustered**: Typos should be sparse, not dense

**Realistic User Behavior:**
Real users make typos, but:
- Usually 1-2 typos per sentence, not everywhere
- Typos preserve word structure: "commnts" not "cmmts"
- Critical keywords often autocorrected

**Proposed Solution:**
1. **Reduce typo density**: Maximum 1-2 typos per prompt
2. **Improve typo patterns**:
   - Adjacent key swaps: "usres" → "usres"
   - Missing letters: "comments" → "coments"
   - Double letters: "user" → "useer"
3. **Protect critical keywords**: Avoid typos on SQL keywords like SELECT, FROM
4. **Spacing preservation**: "Insert into table" → "Insert into tabel", not "Insert tt tabb"

---

## Priority Recommendations

### High Priority (Fix Immediately)
1. **Ambiguous Pronouns**: Implement selective replacement
2. **INSERT/UPDATE/DELETE**: Fix base rendering to include essential details
3. **Typos**: Reduce density and improve realism

### Medium Priority
4. **Under-Specification**: Preserve table names in joins
5. **Implicit Business Logic**: Restrict to WHERE clauses
6. **Missing WHERE Details**: Actually implement the logic
7. **Vague Aggregation**: Extend to aggregate functions

### Low Priority (Polish)
8. **Column Variations**: Fix spacing issues
9. **Synonym Substitution**: Expand synonym dictionary
10. **Incomplete Joins**: (Already working well)

---

## Conclusion

The current SDT engine framework is solid, but the perturbation logic needs refinement to balance **variation** with **semantic preservation**. The key principle should be:

> **A perturbed prompt should be ambiguous or vague, but never impossible to interpret.**

This will ensure the dataset remains valuable for evaluating LLM robustness to natural language variations while maintaining solvability.
