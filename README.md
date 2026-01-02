# Text-to-SQL Synthetic Data Generator

This project is a comprehensive pipeline designed to generate, validate, and verify synthetic training data for Large Language Models (LLMs) tasked with converting Natural Language (English) into SQL queries.

It simulates a realistic data environment by defining a complex social media schema, programmatically generating thousands of valid SQL queries, verifying their structural correctness, and then testing LLM performance against this ground truth.

---

## 🛠 Technologies Used

This project leverages a modern Python stack to ensure robustness, scalability, and ease of use:

*   **[Python 3.10+](https://www.python.org/)**: The core programming language, chosen for its rich ecosystem in data processing and AI.
*   **[SQLGlot](https://github.com/tobymao/sqlglot)**: A powerful SQL parser and transpiler. It is used extensively here for:
    *   **Parsing**: Converting raw SQL strings into Abstract Syntax Trees (ASTs) for analysis.
    *   **Validation**: Ensuring generated SQL is syntactically valid for specific dialects (e.g., MySQL, SQLite).
    *   **Verification**: comparing the *semantic* equivalence of two queries (e.g., `SELECT * FROM table` vs `select * from table`).
*   **[Google GenAI SDK](https://ai.google.dev/)**: The interface for interacting with Gemini models. This is used to test how well state-of-the-art LLMs can interpret our generated prompts.
*   **[Matplotlib](https://matplotlib.org/)**: Used for visualizing dataset statistics, such as the distribution of query complexity and table usage.
*   **[Python-dotenv](https://pypi.org/project/python-dotenv/)**: Manages configuration and API keys securely via `.env` files.

---

## 🚀 The Data Pipeline: A Deep Dive

The project operates as a linear pipeline, transforming abstract rules into verified experimental results.

### 1. The Blueprint (Schema Definition)
**File:** `src/core/schema.py`

Before any code is written, the "world" must be defined. This file exports a detailed schema dictionary representing a social media platform.
*   **Tables & Columns**: Defines entities like `User`, `Post`, `Comment` and their attributes (types, constraints).
*   **Relationships**: Explicitly maps foreign keys (e.g., `Comment.user_id` -> `User.id`) to ensure valid JOIN operations can be generated.

### 2. The Builder (Procedural SQL Generation)
**File:** `src/core/generator.py`
**Executed via:** `src/main.py`

This compoenent acts as a "random walker" through the schema to build valid SQL queries from scratch without using an LLM.
*   **Mechanism**: It starts by selecting a primary table, then probabilistically decides to:
    *   Add **JOINs** based on the schema's foreign key map.
    *   Apply **WHERE** clauses using type-aware data generators (e.g., generating a wrapper date for a DATE column).
    *   Apply **AGGREGATIONS** (COUNT, AVG) and **GROUP BY** clauses.
*   **Validation**: Every generated query is passed through `sqlglot` to valid syntax before checking.
*   **Output**: A large JSON dataset (`social_media_queries.json`) serving as the "Ground Truth."

### 3. The Translator (NL Prompt Generation)
**File:** `src/scripts/generate_nl_prompts.py`
**Helper:** `src/core/nl_renderer.py`

To train or test an LLM, we need English questions that match the SQL. This step converts the rigid SQL logic into natural human language.
*   **Template-Based Rendering**: It breaks down the SQL AST (Abstract Syntax Tree) and maps components to English phrases (e.g., `WHERE age > 21` -> "older than 21").
*   **Variation Engine**: It doesn't just create one prompt. It generates multiple variations for *every* query:
    *   *Formal*: "Retrieve the list of users..."
    *   *Casual*: "Show me the users who..."
    *   *Ambiguous*: "Who are the users..." (Testing LLM resilience).

### 4. The Analyst (Statistical Analysis)
**File:** `src/scripts/analyze_results.py`

Quality assurance for the dataset. This script parses the generated JSON to ensure the data is balanced and diverse.
*   **Metrics**: Calculates distribution of query types (SELECT vs JOINs), complexity depth, and coverage of schema tables.
*   **Visualization**: Generates charts (`visualizations/`) to prove the dataset isn't biased towards simple queries.

### 5. The Exam (LLM Inference Loop)
**File:** `src/tests/test_llm_sql_generation.py`

The "Production" test. We feed the generated English prompts to an actual LLM (e.g., Gemini 1.5 Pro) and capture its response.
*   **Input**: The Natural Language prompt + The Database Schema context.
*   **Output**: The LLM's predicted SQL query.

### 6. The Grader (Functional Verification)
**File:** `src/tests/verify_functional_accuracy.py`

The critical final step. How do we know if the LLM is right? String matching (`predicted == actual`) fails because `SELECT a, b` is functionally identical to `SELECT b, a`.
*   **AST Comparison**: This module uses `sqlglot` to parse both the *Ground Truth* SQL and the *LLM Predicted* SQL into trees.
*   **Canonicalization**: It normalizes both trees (sorting columns, standardizing quotes) to check for **functional equivalence**. If the trees match, the LLM is correct, regardless of formatting differences.

---

## 📂 Project Structure Map

| Directory | Component | Description |
| :--- | :--- | :--- |
| **`src/core/`** | **Foundations** | The immutable logic of the system. Contains the `schema` definitions and the core `generator` logic that builds the query trees. |
| **`src/scripts/`** | **Workflows** | Executable scripts that run specific stages of the pipeline: generation, translation, and analysis. |
| **`src/tests/`** | **Verification** | logic for testing the output. `test_llm_...` runs the AI, while `verify_...` scores the results. |
| **`src/llm/`** | **Adapters** | Abstraction layer for AI models, allowing easy switching between providers (Gemini, OpenAI, etc.). |

---

## 🛠 How to Run

1.  **Setup Environment**:
    ```bash
    source .venv/bin/activate
    export PYTHONPATH=$PYTHONPATH:.
    ```

2.  **Step 1: Generate Ground Truth Data**
    ```bash
    python src/main.py
    ```
    *Creates `social_media_queries_verify.json`*

3.  **Step 2: Translate to Natural Language**
    ```bash
    python -m src.scripts.generate_nl_prompts
    ```

4.  **Step 3: Analyze Dataset Quality**
    ```bash
    python -m src.scripts.analyze_results
    ```

5.  **Step 4: Run LLM Experiments**
    ```bash
    python -m src.tests.test_llm_sql_generation
    ```

*Note: Always verify you are running from the project root directory.*
