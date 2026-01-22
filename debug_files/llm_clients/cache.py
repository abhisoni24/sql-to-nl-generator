perturbation_types = [
    {
      "id": 1,
      "name": "omit_obvious_clauses",
      "display_name": "Omit Obvious Clause Names",
      "description": "Remove explicit SQL clause keywords (SELECT, FROM, WHERE) when the intent is clear from context.",
      "instruction": "Omit SQL keywords like SELECT, FROM, WHERE when the query intent can be inferred.",
      "examples": [
        {
          "original": "SELECT all columns FROM users WHERE country_code equals 'US'.",
          "perturbed": "All columns, users, country_code equals 'US'."
        },
        {
          "original": "SELECT username, email FROM users WHERE is_verified equals true.",
          "perturbed": "username, email, users, is_verified equals true."
        }
      ],
      "application_rules": [
        "Remove SELECT keyword, use implied retrieval: 'Get' → implied",
        "Remove FROM keyword, just mention table name",
        "Remove WHERE keyword, use comma separation for conditions",
        "Keep the logical flow recognizable but strip SQL structure words"
      ],
      "systematic_generation": {
        "feasible": true,
        "method": "Pattern-based text replacement using regex to strip specific keywords (SELECT, FROM, WHERE) while preserving table names, column names, and conditions.",
        "complexity": "Low - simple string manipulation"
      }
    },
    {
      "id": 2,
      "name": "synonym_substitution",
      "display_name": "Synonym Substitution for Actions",
      "description": "Replace query action verbs with synonyms that convey the same intent.",
      "instruction": "Replace query verbs like 'get', 'select', 'retrieve' with natural synonyms.",
      "examples": [
        {
          "original": "Get all columns from posts where view_count > 100.",
          "perturbed": "Fetch all columns from posts where view_count > 100."
        },
        {
          "original": "Show all users where is_verified equals true.",
          "perturbed": "Display all users where is_verified equals true."
        }
      ],
      "application_rules": [
        "Replace action verbs: get→fetch/retrieve/pull/extract, show→display/present",
        "Replace filter verbs: where→having/with/for, equals→matches/is",
        "Maintain consistency within the same prompt",
        "Use domain-appropriate synonyms"
      ],
      "common_synonyms": {
        "get": ["fetch", "retrieve", "pull", "extract", "obtain"],
        "select": ["choose", "pick", "grab", "find"],
        "show": ["display", "present", "list", "give me"],
        "where": ["having", "with", "for which", "that have"],
        "equals": ["is", "matches", "is equal to", "="]
      },
      "systematic_generation": {
        "feasible": true,
        "method": "Dictionary-based replacement with predefined synonym mappings. Parse prompt, identify target words, randomly select from synonym list.",
        "complexity": "Low - dictionary lookup and replacement"
      }
    },
    {
      "id": 3,
      "name": "sentence_structure_variation",
      "display_name": "Sentence Structure Variation",
      "description": "Transform the sentence structure between active, passive, imperative, and interrogative forms.",
      "instruction": "Rewrite the prompt using different grammatical structures while preserving meaning.",
      "examples": [
        {
          "original": "Get all users where is_verified equals true.",
          "perturbed_active": "I need all users where is_verified equals true.",
          "perturbed_passive": "All users where is_verified equals true should be retrieved.",
          "perturbed_imperative": "Retrieve all users where is_verified equals true.",
          "perturbed_question": "Can you get all users where is_verified equals true?"
        },
        {
          "original": "Select posts with view_count greater than 500.",
          "perturbed_active": "We want posts with view_count greater than 500.",
          "perturbed_passive": "Posts with view_count greater than 500 need to be selected.",
          "perturbed_imperative": "Find posts with view_count greater than 500.",
          "perturbed_question": "Could you select posts with view_count greater than 500?"
        }
      ],
      "application_rules": [
        "Active: Add subject ('I need', 'We want', 'The system requires')",
        "Passive: Use passive voice ('should be retrieved', 'is needed')",
        "Imperative: Use command form ('Get', 'Retrieve', 'Find')",
        "Question: Convert to question form ('Can you', 'Would you', 'Could you')"
      ],
      "structure_patterns": {
        "active": ["I need", "We want", "I'm looking for", "We require"],
        "passive": ["should be retrieved", "needs to be fetched", "is required"],
        "imperative": ["Get", "Retrieve", "Find", "Extract", "Pull"],
        "question": ["Can you get", "Would you fetch", "Could you retrieve", "What are"]
      },
      "systematic_generation": {
        "feasible": false,
        "method": "Requires syntactic parsing and grammatical transformation rules. Would need NLP libraries or LLM for accurate restructuring.",
        "complexity": "High - requires deep linguistic knowledge"
      }
    },
    {
      "id": 4,
      "name": "verbosity_variation",
      "display_name": "Verbosity with Fillers and Informal Language",
      "description": "Add conversational fillers, hedging language, and informal expressions to make the prompt more verbose and casual.",
      "instruction": "Insert filler words, informal language, and conversational elements while maintaining query intent.",
      "examples": [
        {
          "original": "Get all posts where view_count > 100.",
          "perturbed": "So, I'd like to basically get, you know, all the posts where the view_count is, like, greater than 100 or something."
        },
        {
          "original": "Select users where country_code equals 'US'.",
          "perturbed": "Okay, so I kind of need to select, um, users where the country_code is basically 'US', I think."
        }
      ],
      "application_rules": [
        "Add filler words: 'basically', 'like', 'you know', 'kind of', 'sort of'",
        "Add hedging: 'I think', 'maybe', 'probably', 'or something'",
        "Add conversational starts: 'So', 'Well', 'Okay', 'Alright'",
        "Add informal phrasing: 'I'd like to', 'Can we', 'I want'",
        "Add redundancy: 'all the', 'any and all', 'each and every'"
      ],
      "filler_phrases": {
        "hedging": ["basically", "kind of", "sort of", "like", "you know", "I think", "probably"],
        "conversational": ["So", "Well", "Okay", "Alright", "Um", "Uh"],
        "informal": ["gonna", "wanna", "gotta", "a bunch of", "or something", "or whatever"],
        "redundant": ["all the", "any and all", "each and every", "the whole"]
      },
      "systematic_generation": {
        "feasible": true,
        "method": "Random insertion of filler phrases at strategic positions (start, before verbs, after nouns). Use position-based rules and filler banks.",
        "complexity": "Medium - requires position identification but uses template insertion"
      }
    },
    {
      "id": 5,
      "name": "operator_aggregate_variation",
      "display_name": "Operator Format and Aggregate Description Variation",
      "description": "Express comparison operators and aggregate functions using varied natural language descriptions and symbolic formats.",
      "instruction": "Replace standard operators and aggregate functions with alternative expressions, symbols, or verbose descriptions.",
      "examples": [
        {
          "original": "Get COUNT(*) from comments where view_count > 50.",
          "perturbed_operator": "Get COUNT(*) from comments where view_count is greater than 50.",
          "perturbed_aggregate": "Get the total number of comments where view_count > 50.",
          "perturbed_both": "Get how many comments have a view_count exceeding 50."
        },
        {
          "original": "Select AVG(view_count) from posts where posted_at >= '2024-01-01'.",
          "perturbed_operator": "Select AVG(view_count) from posts where posted_at is at least '2024-01-01'.",
          "perturbed_aggregate": "Select the average view_count from posts where posted_at >= '2024-01-01'.",
          "perturbed_both": "Select the mean view_count from posts posted no earlier than '2024-01-01'."
        }
      ],
      "application_rules": [
        "Replace operators: > → 'greater than'/'exceeds'/'above', = → 'equals'/'is'/'matches'",
        "Replace aggregates: COUNT → 'total number'/'how many', SUM → 'total'/'sum up', AVG → 'average'/'mean'",
        "Use symbolic variants: '>=' → 'at least', '<=' → 'at most', '!=' → 'not equal to'",
        "Mix symbolic and verbal: 'view_count > 50' → 'view_count exceeds 50'"
      ],
      "operator_variations": {
        ">": ["greater than", "exceeds", "more than", "above", "higher than"],
        "<": ["less than", "below", "under", "fewer than", "lower than"],
        ">=": ["at least", "greater than or equal to", "minimum of", "no less than"],
        "<=": ["at most", "less than or equal to", "maximum of", "no more than"],
        "=": ["equals", "is", "matches", "is equal to"],
        "!=": ["not equal to", "is not", "doesn't match", "different from"]
      },
      "aggregate_variations": {
        "COUNT": ["total number of", "how many", "count of", "number of", "quantity of"],
        "SUM": ["total", "sum of", "add up", "combined total"],
        "AVG": ["average", "mean", "average value of", "typical"],
        "MAX": ["maximum", "highest", "largest", "biggest"],
        "MIN": ["minimum", "lowest", "smallest", "least"]
      },
      "systematic_generation": {
        "feasible": true,
        "method": "Pattern matching for operators (>, <, =, etc.) and aggregate functions (COUNT, SUM, AVG). Dictionary-based replacement with predefined mappings.",
        "complexity": "Low - regex pattern matching and dictionary lookup"
      }
    },
    {
      "id": 6,
      "name": "typos",
      "display_name": "Typos and Misspellings",
      "description": "Introduce realistic keyboard typos in table names, column names, or query-related terms.",
      "instruction": "Add 1-2 realistic typos while keeping the prompt readable and intent clear.",
      "examples": [
        {
          "original": "Get all columns from users where email equals 'test@example.com'.",
          "perturbed": "Get all columns from users where emial equals 'test@example.com'."
        },
        {
          "original": "Select all posts where view_count exceeds 1000.",
          "perturbed": "Selct all posts where view_count exceeds 1000."
        }
      ],
      "application_rules": [
        "Introduce 1-2 typos per prompt maximum",
        "Use realistic typo patterns: adjacent key swap, missing letter, duplicate letter",
        "Target table names, column names, or common words",
        "Avoid typos that completely obscure meaning",
        "Common patterns: usres, psots, coments, whre, slect"
      ],
      "typo_patterns": {
        "character_swap": ["users → usres", "posts → psots", "email → emial"],
        "missing_character": ["comments → coments", "where → whre", "count → cont"],
        "duplicate_character": ["from → fromm", "likes → likkes", "follows → folllows"],
        "adjacent_key": ["select → sekect", "content → contnet", "user_id → user_ud"]
      },
      "common_typos": {
        "users": ["usres", "uesrs", "usrs"],
        "posts": ["psots", "psts", "posst"],
        "comments": ["coments", "commments", "commnets"],
        "email": ["emial", "emai", "emaill"],
        "where": ["whre", "wher", "hwere"]
      },
      "systematic_generation": {
        "feasible": true,
        "method": "Rule-based typo generation: (1) swap adjacent characters, (2) drop random character, (3) duplicate random character, (4) substitute with adjacent keyboard key. Target specific word positions.",
        "complexity": "Low - character-level string manipulation with position-based rules"
      }
    },
    {
      "id": 7,
      "name": "comment_annotations",
      "display_name": "Comment-Style Annotations",
      "description": "Add SQL-style comments or parenthetical notes within the natural language prompt.",
      "instruction": "Insert comments, annotations, or clarifications using SQL comment syntax or parenthetical expressions.",
      "examples": [
        {
          "original": "Get all users where country_code equals 'US'.",
          "perturbed": "Get all users -- need to filter by country -- where country_code equals 'US' (United States only)."
        },
        {
          "original": "Select posts with view_count greater than 500.",
          "perturbed": "Select posts (popular ones) with view_count greater than 500 -- for analytics."
        }
      ],
      "application_rules": [
        "Add SQL-style comments: '-- comment text'",
        "Add parenthetical notes: '(clarification here)'",
        "Add inline clarifications that don't change meaning",
        "Place comments mid-sentence or at end",
        "Keep annotations brief and relevant"
      ],
      "comment_patterns": {
        "sql_comment": ["-- this is important", "-- note:", "-- filtering here"],
        "parenthetical": ["(i.e., ...)", "(specifically ...)", "(note: ...)", "(only ...)"],
        "clarification": ["in other words", "that is", "meaning"]
      },
      "example_annotations": [
        "-- for reporting purposes",
        "(active users only)",
        "-- important: check this",
        "(excluding deleted records)"
      ],
      "systematic_generation": {
        "feasible": true,
        "method": "Template-based insertion at predetermined positions (after table names, after WHERE, at end). Use annotation bank with random selection.",
        "complexity": "Low - position-based template insertion"
      }
    },
    {
      "id": 8,
      "name": "temporal_expression_variation",
      "display_name": "Temporal Expression Variation",
      "description": "Express date/time conditions using varied temporal language, from specific dates to relative expressions.",
      "instruction": "Replace date/time conditions with alternative temporal expressions ranging from specific to vague.",
      "examples": [
        {
          "original": "Get all posts where posted_at > '2024-01-01'.",
          "perturbed_relative": "Get all posts from this year.",
          "perturbed_vague": "Get all recent posts.",
          "perturbed_natural": "Get all posts posted after January first, twenty twenty-four."
        },
        {
          "original": "Select comments where created_at >= '2024-06-15'.",
          "perturbed_relative": "Select comments from the last few months.",
          "perturbed_vague": "Select recent comments.",
          "perturbed_natural": "Select comments created after June fifteenth, two thousand twenty-four."
        }
      ],
      "application_rules": [
        "Replace ISO dates with natural language: '2024-01-01' → 'January 1st, 2024'",
        "Use relative time: 'last week', 'yesterday', 'this month', 'recent'",
        "Use vague periods: 'recently', 'lately', 'a while ago', 'not long ago'",
        "Mix formats: '2024' vs 'twenty twenty-four'",
        "Only apply if original prompt contains date/time conditions"
      ],
      "temporal_patterns": {
        "specific_date": ["January 1st, 2024", "the first of January", "Jan 1 2024", "01/01/2024"],
        "relative": ["last week", "yesterday", "this month", "last year", "two days ago"],
        "vague": ["recently", "lately", "a while ago", "not long ago", "some time ago"],
        "comparison": ["newer than", "older than", "after", "before", "since"]
      },
      "systematic_generation": {
        "feasible": true,
        "method": "Regex pattern matching for date formats (YYYY-MM-DD, timestamps). Dictionary-based replacement with context-aware rules (> date → 'after', < date → 'before').",
        "complexity": "Medium - requires date parsing and context-aware replacement"
      }
    },
    {
  "id": 9,
  "name": "punctuation_variation",
  "display_name": "Punctuation Variation",
  "description": "Introduce varied punctuation marks (commas, semicolons, dashes, ellipsis) at different positions in the prompt.",
  "instruction": "Insert or modify punctuation marks to create different sentence rhythms while preserving meaning.",
  "examples": [
    {
      "original": "Get all users where is_verified equals true and country_code equals 'US'.",
      "perturbed": "Get all users, where is_verified equals true, and country_code equals 'US'."
    },
    {
      "original": "Select posts with view_count greater than 1000 and posted_at after '2024-01-01'.",
      "perturbed": "Select posts with view_count greater than 1000; posted_at after '2024-01-01'."
    },
    {
      "original": "Retrieve comments from users where comment_text is not empty.",
      "perturbed": "Retrieve comments from users... where comment_text is not empty."
    }
  ],
  "application_rules": [
    "Insert commas before/after WHERE, AND, OR clauses",
    "Replace AND/OR with semicolons for clause separation",
    "Add ellipsis (...) for dramatic pauses",
    "Use em-dashes (--) or en-dashes (–) to separate conditions",
    "Insert 1-3 punctuation modifications per prompt",
    "Maintain sentence readability and meaning"
  ],
  "punctuation_types": {
    "comma_insertion": ["before WHERE", "after table names", "between conditions", "after SELECT"],
    "semicolon_replacement": ["replace AND with ;", "replace OR with ;", "separate major clauses"],
    "ellipsis": ["before WHERE", "between clauses", "after table reference"],
    "dash_insertion": ["before conditions", "around parenthetical info", "between clauses"]
  },
  "insertion_positions": [
    "After SELECT/GET keywords",
    "Before/after WHERE",
    "Between AND/OR conditions",
    "After table names",
    "Before comparison operators"
  ],
  "systematic_generation": {
    "feasible": true,
    "method": "Pattern matching for clause boundaries (WHERE, AND, OR, FROM). Randomly select 1-3 positions and insert punctuation from predefined types. Replace conjunctions with semicolons.",
    "complexity": "Low - position-based insertion with random selection"
  }
},
    {
      "id": 10,
      "name": "urgency_qualifiers",
      "display_name": "Urgency Qualifiers",
      "description": "Add urgency or priority indicators to the query request.",
      "instruction": "Prepend or append urgency markers, priority levels, or time-sensitive language.",
      "examples": [
        {
          "original": "Get all posts where view_count > 1000.",
          "perturbed_high": "URGENT: Get all posts where view_count > 1000.",
          "perturbed_low": "When you get a chance, get all posts where view_count > 1000.",
          "perturbed_priority": "High priority - get all posts where view_count > 1000."
        },
        {
          "original": "Select users where is_verified equals true.",
          "perturbed_high": "ASAP: Select users where is_verified equals true.",
          "perturbed_low": "No rush, but select users where is_verified equals true.",
          "perturbed_priority": "Critical - select users where is_verified equals true."
        }
      ],
      "application_rules": [
        "Add urgency markers: 'URGENT', 'ASAP', 'immediately', 'right away'",
        "Add low urgency: 'when you can', 'no rush', 'at your convenience'",
        "Add priority levels: 'High priority', 'Low priority', 'Critical'",
        "Add time pressure: 'need this now', 'quickly', 'as soon as possible'",
        "Place at beginning or end of prompt"
      ],
      "urgency_levels": {
        "high": ["URGENT:", "ASAP:", "Immediately:", "Right away:", "Critical:", "High priority:"],
        "medium": ["Soon:", "Please prioritize:", "Important:", "Need this:"],
        "low": ["When you can,", "No rush,", "At your convenience,", "Eventually,", "Low priority:"]
      },
      "systematic_generation": {
        "feasible": true,
        "method": "Prepend or append urgency markers from predefined lists. Random selection based on urgency level (high/medium/low).",
        "complexity": "Low - simple string prepend/append with random selection"
      }
    },
    {
      "id": 11,
      "name": "mixed_sql_nl",
      "display_name": "Mixed SQL and Natural Language",
      "description": "Blend SQL syntax elements directly into natural language prompts.",
      "instruction": "Intermix actual SQL keywords, operators, or syntax with natural language descriptions.",
      "examples": [
        {
          "original": "Get all users where country_code equals 'US' and is_verified equals true.",
          "perturbed": "SELECT all users WHERE country_code = 'US' and they are verified."
        },
        {
          "original": "Retrieve posts with view_count greater than 500.",
          "perturbed": "Retrieve posts WHERE view_count > 500."
        }
      ],
      "application_rules": [
        "Mix SQL keywords (SELECT, WHERE, AND, OR) with natural language",
        "Use SQL operators (=, >, <) alongside natural descriptions",
        "Combine table.column notation with informal references",
        "Create hybrid syntax that's neither pure SQL nor pure natural language",
        "Keep some structure recognizable to both SQL and natural language"
      ],
      "mixing_patterns": {
        "keyword_mix": ["SELECT from users where verified", "Get * FROM posts WHERE popular"],
        "operator_mix": ["users where email = 'test' and verified", "posts with view_count > 100"],
        "notation_mix": ["Get users.username where active", "SELECT posts.content from posts that are recent"]
      },
      "systematic_generation": {
        "feasible": true,
        "method": "Pattern matching for natural language components. Replace specific phrases with SQL equivalents (where→WHERE, equals→=, greater than→>). Maintain hybrid structure.",
        "complexity": "Low - dictionary-based replacement with SQL keyword injection"
      }
    },
    {
      "id": 12,
      "name": "table_column_synonyms",
      "display_name": "Synonyms of Tables and Column Names",
      "description": "Replace actual schema table/column names with plausible synonyms that humans might naturally use.",
      "instruction": "Substitute schema-specific names with domain-appropriate synonyms while maintaining query intent.",
      "examples": [
        {
          "original": "Get all columns from posts where view_count > 100.",
          "perturbed": "Get all columns from articles where views > 100."
        },
        {
          "original": "Select username and email from users where is_verified equals true.",
          "perturbed": "Select user_name and email_address from members where confirmed equals true."
        }
      ],
      "application_rules": [
        "Replace table names with synonyms maintaining semantic similarity",
        "Replace column names with natural alternatives",
        "Maintain consistency within the same prompt",
        "Use domain-appropriate alternatives",
        "Preserve the essential meaning of the schema element"
      ],
      "schema_synonyms": {
        "users": ["members", "accounts", "profiles", "customers"],
        "posts": ["articles", "entries", "content", "publications", "messages"],
        "comments": ["replies", "responses", "feedback", "remarks"],
        "likes": ["reactions", "favorites", "appreciations", "endorsements"],
        "follows": ["subscriptions", "connections", "friendships"],
        "user_id": ["member_id", "account_id", "profile_id", "uid"],
        "post_id": ["article_id", "content_id", "entry_id", "pid"],
        "view_count": ["views", "visit_count", "page_views", "impressions"],
        "email": ["email_address", "contact", "mail"],
        "username": ["user_name", "login", "handle", "screen_name"],
        "content": ["body", "text", "message", "post_text"],
        "comment_text": ["reply_text", "comment_body", "response"],
        "is_verified": ["verified", "is_confirmed", "confirmed", "validation_status"],
        "signup_date": ["registration_date", "joined_date", "created_at", "member_since"],
        "posted_at": ["published_at", "created_at", "timestamp", "post_date"],
        "liked_at": ["reaction_time", "favorited_at", "timestamp"],
        "followed_at": ["connection_date", "subscribed_at", "friend_since"]
      },
      "systematic_generation": {
        "feasible": true,
        "method": "Dictionary-based replacement. Parse prompt for schema elements (table/column names), look up in synonym dictionary, replace with random selection.",
        "complexity": "Low - dictionary lookup and string replacement"
      }
    },
    {
      "id": 13,
      "name": "incomplete_join_spec",
      "display_name": "Incomplete JOIN Specification",
      "description": "When querying multiple related tables, omit explicit join conditions, join types, or relationship details.",
      "instruction": "Remove explicit JOIN syntax and foreign key references, using only natural language to imply relationships.",
      "examples": [
        {
          "original": "Get all columns from users JOIN posts ON users.id = posts.user_id where posts.view_count > 100.",
          "perturbed": "Get all columns from users and their posts where view_count > 100."
        },
        {
          "original": "Select username from users LEFT JOIN comments ON users.id = comments.user_id.",
          "perturbed": "Select username from users along with their comments."
        }
      ],
      "application_rules": [
        "Remove JOIN keywords (JOIN, INNER JOIN, LEFT JOIN)",
        "Remove ON clauses and explicit foreign key relationships",
        "Use natural language: 'and their', 'with', 'along with', 'including'",
        "Omit join type specification",
        "Let relationships be implied by context",
        "Only apply when original prompt involves multiple tables"
      ],
      "relationship_phrases": {
        "possessive": ["users and their posts", "posts and their comments", "users with their likes"],
        "inclusive": ["users along with posts", "posts including comments", "users together with follows"],
        "connective": ["users connected to posts", "posts related to comments", "users associated with likes"]
      },
      "join_scenarios": {
        "user_posts": "users and their posts",
        "post_comments": "posts with comments",
        "user_likes": "users and the posts they liked",
        "user_followers": "users and their followers"
      },
      "systematic_generation": {
        "feasible": true,
        "method": "Pattern matching for JOIN keywords and ON clauses. Remove JOIN...ON blocks, replace with relationship phrases from predefined templates based on table pairs.",
        "complexity": "Medium - requires JOIN clause parsing and relationship inference"
      }
    },
    {
      "id": 14,
      "name": "ambiguous_pronouns",
      "display_name": "Ambiguous Pronoun References",
      "description": "Replace ONE explicit table, column, or value reference with a pronoun lacking clear antecedent. Maximum one ambiguous pronoun per prompt to preserve semantic meaning.",
      "instruction": "Substitute a SINGLE specific name with a pronoun (it, that, this) to create mild referential ambiguity while keeping the query understandable.",
      "examples": [
        {
          "original": "Get all columns from users where users.country_code equals 'US'.",
          "perturbed": "Get all columns from users where that field equals 'US'."
        },
        {
          "original": "Select posts where posts.view_count exceeds 1000 and posts.posted_at is recent.",
          "perturbed": "Select posts where it exceeds 1000 and posts.posted_at is recent."
        }
      ],
      "application_rules": [
        "Replace ONLY ONE specific reference per prompt",
        "Target a table name, column name, or value - not multiple",
        "Use pronouns: 'it', 'that', 'this', 'the field', 'the column'",
        "Ensure surrounding context still makes the query understandable",
        "Avoid replacing critical identifiers that would make query unsolvable",
        "Prefer replacing second occurrence of repeated elements"
      ],
      "pronoun_substitutions": {
        "table_reference": ["it", "that table", "this table"],
        "column_reference": ["that field", "it", "the column", "this field"],
        "value_reference": ["that", "it", "this value"]
      },
      "safe_replacement_strategy": [
        "If column name appears twice, replace the second occurrence",
        "Replace non-critical columns (not primary keys or join keys)",
        "Replace table reference only if table name is mentioned multiple times",
        "Avoid replacing the main table in FROM clause"
      ],
      "systematic_generation": {
        "feasible": true,
        "method": "Parse prompt for repeated elements (table names, column names). Identify safe replacement candidates (non-critical, repeated). Replace second occurrence with pronoun from predefined list.",
        "complexity": "Medium - requires parsing and safe candidate identification"
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