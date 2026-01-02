perturbation_types = [
    {
      "id": 1,
      "name": "under_specification",
      "display_name": "Under-specification of Table/Column Names",
      "description": "Omit explicit table or column names that would normally be specified, forcing the model to infer schema references from context.",
      "instruction": "Remove explicit table names, aliases, and column references. Make the prompt more ambiguous about which specific tables or columns to use.",
      "example": {
        "original": "Get all columns from likes (as l1) where l1.post_id equals 827.",
        "perturbed": "Get everything where the post ID equals 827."
      },
      "application_rules": [
        "Remove table name if it appears explicitly",
        "Remove aliases like 'as l1'",
        "Replace qualified column references (table.column) with just column names",
        "Use generic terms like 'everything', 'all data', 'records' instead of specific table names"
      ]
    },
    {
      "id": 2,
      "name": "implicit_business_logic",
      "display_name": "Implicit Business Logic",
      "description": "Remove explicit condition definitions and assume domain knowledge about what constitutes valid, active, or relevant records.",
      "instruction": "Replace specific filter conditions with vague business terms that assume domain knowledge.",
      "example": {
        "original": "Get all columns from likes (as l1) where l1.post_id equals 827.",
        "perturbed": "Get all likes for that specific post."
      },
      "application_rules": [
        "Replace specific conditions with domain assumptions like 'relevant', 'active', 'valid'",
        "Use demonstrative pronouns ('that post', 'this user') without explicit IDs",
        "Imply filters without stating exact criteria",
        "Assume knowledge of what 'current', 'recent', or 'important' means"
      ]
    },
    {
      "id": 3,
      "name": "synonym_substitution",
      "display_name": "Synonym Substitution",
      "description": "Replace schema-related terms (table names, column names) with synonyms or related terms that humans naturally use.",
      "instruction": "Replace table and column names with plausible synonyms while maintaining the query intent.",
      "example": {
        "original": "Get all columns from likes (as l1) where l1.post_id equals 827.",
        "perturbed": "Get all columns from reactions (as l1) where l1.content_id equals 827."
      },
      "application_rules": [
        "Replace table names with synonyms: likes→reactions/favorites, users→members/accounts, orders→purchases",
        "Replace column names with synonyms: post_id→content_id/article_id, user_id→member_id/account_id",
        "Maintain consistency within the same prompt",
        "Use domain-appropriate synonyms"
      ],
      "common_synonyms": {
        "likes": ["reactions", "favorites", "appreciations"],
        "users": ["members", "accounts", "customers", "clients"],
        "posts": ["articles", "content", "messages", "entries"],
        "orders": ["purchases", "transactions", "sales"],
        "products": ["items", "goods", "merchandise"],
        "post_id": ["content_id", "article_id", "message_id"],
        "user_id": ["member_id", "account_id", "customer_id"]
      }
    },
    {
      "id": 4,
      "name": "incomplete_joins",
      "display_name": "Incomplete Join Specifications",
      "description": "When the query implies relationships between tables, omit join conditions, join types, or relationship details.",
      "instruction": "If the nl_prompt mentions multiple tables or relationships, remove specific join conditions and foreign key references.",
      "example": {
        "original": "Get all columns from users u JOIN posts p ON u.user_id = p.author_id where p.post_id equals 827.",
        "perturbed": "Get all columns from users with their posts where the post ID equals 827."
      },
      "application_rules": [
        "Remove explicit JOIN keywords and ON clauses",
        "Replace with natural language like 'with', 'and their', 'along with'",
        "Omit join type specification (INNER, LEFT, RIGHT)",
        "Remove explicit foreign key references",
        "Only apply if the original prompt mentions multiple tables or relationships"
      ]
    },
    {
      "id": 5,
      "name": "relative_temporal",
      "display_name": "Relative Temporal References",
      "description": "Replace explicit dates, timestamps, or time-based conditions with relative time expressions.",
      "instruction": "Convert absolute date/time values to relative expressions like 'recent', 'last month', 'yesterday'.",
      "example": {
        "original": "Get all columns from likes (as l1) where l1.created_date > '2024-01-01'.",
        "perturbed": "Get all columns from likes (as l1) where created recently."
      },
      "application_rules": [
        "Replace specific dates with relative terms: 'recent', 'last month', 'yesterday', 'this week'",
        "Replace date ranges with vague periods: 'in the past year', 'older records'",
        "Remove exact timestamps in favor of 'recently', 'a while ago'",
        "Only apply if the original prompt contains date/time conditions"
      ],
      "temporal_mappings": {
        "specific_date": ["yesterday", "last week", "recently", "a few days ago"],
        "date_comparison": ["recent", "old", "newer", "latest"],
        "date_range": ["last month", "this quarter", "past year", "in recent months"]
      }
    },
    {
      "id": 6,
      "name": "ambiguous_pronouns",
      "display_name": "Ambiguous Pronoun References",
      "description": "Replace explicit table or column references with pronouns (it, that, they) without clear antecedents.",
      "instruction": "Substitute table names, column names, or values with pronouns, making references ambiguous.",
      "example": {
        "original": "Get all columns from likes (as l1) where l1.post_id equals 827.",
        "perturbed": "Get all columns from it where that ID equals 827."
      },
      "application_rules": [
        "Replace table names with 'it', 'that table', 'them'",
        "Replace column names with 'that field', 'it', 'the value'",
        "Replace specific IDs/values with 'that one', 'it', 'the specified one'",
        "Create ambiguity about which entity is being referenced"
      ],
      "pronoun_substitutions": {
        "table_reference": ["it", "that table", "them", "those"],
        "column_reference": ["that field", "it", "the column", "that value"],
        "id_reference": ["that one", "it", "that ID", "the specified one"]
      }
    },
    {
      "id": 7,
      "name": "vague_aggregation",
      "display_name": "Vague Aggregation Requests",
      "description": "When aggregations are present, use imprecise language without specifying exact aggregate functions or grouping columns.",
      "instruction": "Replace specific aggregation functions (COUNT, SUM, AVG) and GROUP BY specifications with vague requests.",
      "example": {
        "original": "Get COUNT(*) from likes grouped by post_id where post_id equals 827.",
        "perturbed": "Show me likes by post where post_id equals 827."
      },
      "application_rules": [
        "Replace COUNT/SUM/AVG with 'total', 'number of', 'summarize'",
        "Replace GROUP BY with 'by', 'for each', 'per'",
        "Remove explicit aggregate function names",
        "Use vague terms like 'breakdown', 'summary', 'totals'",
        "Only apply if the original prompt contains aggregation functions"
      ],
      "vague_mappings": {
        "COUNT": ["how many", "number of", "total"],
        "SUM": ["total", "sum up", "add up"],
        "AVG": ["average", "typical", "mean"],
        "GROUP BY": ["by", "per", "for each", "breakdown by"]
      }
    },
    {
      "id": 8,
      "name": "column_variations",
      "display_name": "Column Name Variations",
      "description": "Modify column names using different naming conventions, abbreviations, or case styles.",
      "instruction": "Change column naming conventions (snake_case, camelCase), use abbreviations, or alter plural/singular forms.",
      "example": {
        "original": "Get all columns from likes (as l1) where l1.post_id equals 827.",
        "perturbed": "Get all columns from likes (as l1) where l1.postId equals 827."
      },
      "application_rules": [
        "Convert snake_case to camelCase: post_id → postId, user_name → userName",
        "Use abbreviations: identifier → id, number → num, customer → cust",
        "Change plural/singular: posts → post, users → user",
        "Swap prefix/suffix: id_post → post_id, date_created → created_date"
      ],
      "variation_patterns": {
        "case_conversion": ["post_id → postId", "user_name → userName", "created_date → createdDate"],
        "abbreviations": ["post_id → post_identifier", "user_id → uid", "customer → cust"],
        "plural_singular": ["likes → like", "posts → post", "users → user"]
      }
    },
    {
      "id": 9,
      "name": "missing_where_details",
      "display_name": "Missing WHERE Clause Details",
      "description": "Replace specific filter conditions with vague, subjective criteria.",
      "instruction": "Convert explicit WHERE conditions into imprecise, subjective filtering language.",
      "example": {
        "original": "Get all columns from likes (as l1) where l1.post_id equals 827.",
        "perturbed": "Get all columns from likes (as l1) where the post is the relevant one."
      },
      "application_rules": [
        "Replace specific numeric conditions with 'high', 'low', 'significant'",
        "Replace equality checks with 'relevant', 'appropriate', 'correct one'",
        "Use subjective terms: 'important', 'key', 'major', 'primary'",
        "Remove exact values in favor of qualitative descriptions"
      ],
      "vague_terms": {
        "numeric_comparison": ["high value", "low amount", "significant number"],
        "equality": ["the relevant one", "the right one", "appropriate", "matching"],
        "quality": ["important", "key", "significant", "major", "primary"]
      }
    },
    {
      "id": 10,
      "name": "typos",
      "display_name": "Typos and Misspellings",
      "description": "Introduce realistic keyboard typos in table names, column names, or SQL-related terms.",
      "instruction": "Add 1-2 realistic typos to table names, column names, or keywords while keeping the prompt readable.",
      "example": {
        "original": "Get all columns from likes (as l1) where l1.post_id equals 827.",
        "perturbed": "Get all columns from liks (as l1) where l1.post_id equls 827."
      },
      "application_rules": [
        "Introduce 1-2 typos per prompt",
        "Use realistic typo patterns: character swap, missing character, duplicate character",
        "Target table names, column names, or SQL keywords",
        "Keep typos subtle enough that intent remains clear",
        "Common patterns: custmoer, prodcut, oder, equls, slect"
      ],
      "typo_patterns": {
        "character_swap": ["likes → lkies", "post_id → post_di"],
        "missing_character": ["equals → equls", "where → whre", "likes → liks"],
        "duplicate_character": ["from → fromm", "post → posst"],
        "adjacent_key": ["select → sekect", "where → whete"]
      }
    }
  ]

schema = {
    "users": {
        "id": "int",
        "username": "varchar",
        "email": "varchar",
        "signup_date": "datetime",
        "is_verified": "boolean",
        "country_code": "varchar"
    },
    "posts": {
        "id": "int",
        "user_id": "int",
        "content": "text",
        "posted_at": "datetime",
        "view_count": "int"
    },
    "comments": {
        "id": "int",
        "user_id": "int",
        "post_id": "int",
        "comment_text": "text",
        "created_at": "datetime"
    },
    "likes": {
        "user_id": "int",
        "post_id": "int",
        "liked_at": "datetime"
    },
    "follows": {
        "follower_id": "int",
        "followee_id": "int",
        "followed_at": "datetime"
    }
}

# Define valid join paths (left_table, right_table): (left_key, right_key)
foreign_keys = {
    ("users", "posts"): ("id", "user_id"),
    ("posts", "users"): ("user_id", "id"),  # Reverse join
    ("users", "comments"): ("id", "user_id"),
    ("comments", "users"): ("user_id", "id"),
    ("posts", "comments"): ("id", "post_id"),
    ("comments", "posts"): ("post_id", "id"),
    ("users", "likes"): ("id", "user_id"),
    ("likes", "users"): ("user_id", "id"),
    ("posts", "likes"): ("id", "post_id"),
    ("likes", "posts"): ("post_id", "id"),
    ("users", "follows"): ("id", "follower_id"),  # Who is following
    ("follows", "users"): ("follower_id", "id"),
}

# Column type categories for smart filtering
NUMERIC_TYPES = {"int"}
TEXT_TYPES = {"varchar", "text"}
DATE_TYPES = {"datetime"}
BOOLEAN_TYPES = {"boolean"}


instructions = ''' Instructions

## Part 1: Single Perturbations (10 versions)
For each of the 10 perturbation types:
1. Carefully read the perturbation description and application rules
2. Evaluate if the perturbation is applicable to this specific nl_prompt
3. If applicable: Generate a perturbed version following the rules and examples
4. If NOT applicable: Mark as "not_applicable" and provide a brief reason why

**Applicability Guidelines:**
- under_specification: Applicable if prompt has explicit table/column names
- implicit_business_logic: Applicable if prompt has specific conditions/filters
- synonym_substitution: Applicable if prompt contains table or column names
- incomplete_joins: Applicable ONLY if prompt mentions multiple tables or relationships
- relative_temporal: Applicable ONLY if prompt has date/time conditions
- ambiguous_pronouns: Applicable if prompt has explicit entity references
- vague_aggregation: Applicable ONLY if prompt contains aggregation (COUNT, SUM, AVG, GROUP BY)
- column_variations: Applicable if prompt has explicit column names
- missing_where_details: Applicable if prompt has WHERE conditions with specific values
- typos: Always applicable

## Part 2: Compound Perturbation (1 version)
1. Select 2-5 perturbations that are applicable to this prompt
2. Apply them simultaneously to create a realistic compound perturbation
3. Prioritize perturbations that commonly co-occur in real developer behavior
4. List all perturbations applied

# Output Format
Return your response as a valid JSON object with this exact structure:
```json
{
  "original": {
    "nl_prompt": "<original prompt>",
    "sql": "<original SQL>",
    "tables": ["<table names>"],
    "complexity": "<complexity level>"
  },
  "single_perturbations": [
    {
      "perturbation_id": 1,
      "perturbation_name": "under_specification",
      "applicable": true,
      "perturbed_nl_prompt": "<perturbed version>",
      "changes_made": "<brief description of what was changed>",
      "reason_not_applicable": null
    },
    {
      "perturbation_id": 2,
      "perturbation_name": "implicit_business_logic",
      "applicable": false,
      "perturbed_nl_prompt": null,
      "changes_made": null,
      "reason_not_applicable": "<explanation why this perturbation doesn't apply>"
    },
    // ... continue for all 10 perturbations
  ],
  "compound_perturbation": {
    "perturbations_applied": [
      {
        "perturbation_id": 1,
        "perturbation_name": "under_specification"
      },
      {
        "perturbation_id": 3,
        "perturbation_name": "synonym_substitution"
      },
      {
        "perturbation_id": 10,
        "perturbation_name": "typos"
      }
    ],
    "perturbed_nl_prompt": "<compound perturbed version>",
    "changes_made": "<description of all changes made>"
  },
  "metadata": {
    "total_applicable_perturbations": 8,
    "total_not_applicable": 2,
    "applicability_rate": 0.8
  }
}
```

# Important Notes
1. Ensure the JSON is valid and properly formatted
2. For not_applicable cases, set perturbed_nl_prompt to null and provide reason_not_applicable
3. For compound perturbation, only use applicable perturbations
4. Maintain the original query intent in all perturbations
5. Make perturbations realistic - simulate actual developer behavior
6. Do not add explanations outside the JSON structure
7. Return ONLY the JSON object, no additional text

Generate the perturbed versions now.
'''