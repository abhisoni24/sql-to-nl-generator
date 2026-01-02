import json
import matplotlib.pyplot as plt
import os
from collections import Counter

def analyze_and_visualize():
    if not os.path.exists('./dataset/current/nl_social_media_queries.json'):
        print("Error: ./dataset/current/nl_social_media_queries.json not found. Run main.py first.")
        return

    with open('./dataset/current/nl_social_media_queries.json', 'r') as f:
        data = json.load(f)
    
    # Ensure visualizations directory exists
    os.makedirs('visualizations_verify', exist_ok=True)
    
    print(f"Analyzing {len(data)} SQL queries...")
    print("="*60)
    
    # ========== PART 1: SQL Query Analysis ==========
    
    # 1. Query Type Distribution
    query_types = {'SELECT': 0, 'INSERT': 0, 'UPDATE': 0, 'DELETE': 0}
    for d in data:
        sql = d['sql'].strip().upper()
        if sql.startswith('SELECT'):
            query_types['SELECT'] += 1
        elif sql.startswith('INSERT'):
            query_types['INSERT'] += 1
        elif sql.startswith('UPDATE'):
            query_types['UPDATE'] += 1
        elif sql.startswith('DELETE'):
            query_types['DELETE'] += 1
            
    print("\n1. Query Type Distribution:")
    print("-" * 30)
    for k, v in query_types.items():
        print(f"  {k}: {v} ({v/len(data)*100:.1f}%)")

    # Visualize Query Types
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    ax1.pie(query_types.values(), labels=query_types.keys(), autopct='%1.1f%%', 
            startangle=140, colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
    ax1.set_title('Query Type Distribution')
    
    # 2. Complexity Distribution
    complexities = [d['complexity'] for d in data]
    comp_counts = Counter(complexities)
    
    ax2.pie(comp_counts.values(), labels=comp_counts.keys(), autopct='%1.1f%%', 
            startangle=140)
    ax2.set_title('Query Complexity Distribution')
    
    plt.tight_layout()
    plt.savefig('visualizations_verify/sql_query_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Table Usage Frequency
    all_tables = []
    for d in data:
        tables = d.get('tables', [])
        tables = [t for t in tables if t]
        all_tables.extend(tables)
        
    table_counts = Counter(all_tables)
    
    plt.figure(figsize=(10, 6))
    plt.bar(table_counts.keys(), table_counts.values(), color='skyblue')
    plt.title('Table Usage Frequency', fontsize=14, fontweight='bold')
    plt.xlabel('Table Name')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('visualizations_verify/table_usage.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. SQL Feature Coverage
    keywords = ['WHERE', 'GROUP BY', 'HAVING', 'ORDER BY', 'LIMIT', 'JOIN', 
                'LEFT JOIN', 'DATE_SUB', 'INTERVAL', 'LIKE', 'IN']
    keyword_counts = {k: 0 for k in keywords}
    keyword_counts['Subquery'] = 0
    
    for d in data:
        sql = d['sql'].upper()
        for k in keywords:
            if k in sql:
                keyword_counts[k] += 1
        
        if "SELECT" in sql[7:]:  # Nested SELECT (subquery)
             keyword_counts['Subquery'] += 1

    print("\n2. SQL Feature Coverage:")
    print("-" * 30)
    for k, v in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {k}: {v} ({v/len(data)*100:.1f}%)")
        
    plt.figure(figsize=(12, 6))
    plt.bar(keyword_counts.keys(), keyword_counts.values(), color='#66b3ff')
    plt.title('SQL Feature Coverage', fontsize=14, fontweight='bold')
    plt.xlabel('Feature')
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('visualizations_verify/feature_coverage.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ========== PART 2: NL Prompt Analysis ==========
    
    # 5. Variation Uniqueness Analysis
    all_unique = 0
    two_unique = 0
    one_unique = 0
    
    for d in data:
        variations = d.get('nl_prompt_variations', [])
        if len(variations) == 3:
            unique_count = len(set(variations))
            if unique_count == 3:
                all_unique += 1
            elif unique_count == 2:
                two_unique += 1
            elif unique_count == 1:
                one_unique += 1
    
    print("\n3. NL Variation Uniqueness:")
    print("-" * 30)
    print(f"  All 3 unique: {all_unique} ({all_unique/len(data)*100:.1f}%)")
    print(f"  2 unique: {two_unique} ({two_unique/len(data)*100:.1f}%)")
    print(f"  1 unique (all same): {one_unique} ({one_unique/len(data)*100:.1f}%)")
    
    # Visualize Uniqueness
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    uniqueness_data = [all_unique, two_unique, one_unique]
    uniqueness_labels = ['All 3 Unique', '2 Unique', '1 Unique']
    colors = ['#2ecc71', '#f39c12', '#e74c3c']
    
    ax1.pie(uniqueness_data, labels=uniqueness_labels, autopct='%1.1f%%', 
            startangle=90, colors=colors)
    ax1.set_title('Variation Uniqueness Distribution', fontweight='bold')
    
    # 6. NL Prompt Length Statistics
    vanilla_lengths = []
    variation_lengths = []
    
    for d in data:
        vanilla = d.get('nl_prompt', '')
        vanilla_lengths.append(len(vanilla.split()))
        
        for var in d.get('nl_prompt_variations', []):
            variation_lengths.append(len(var.split()))
    
    print("\n4. NL Prompt Length (words):")
    print("-" * 30)
    print(f"  Vanilla - Avg: {sum(vanilla_lengths)/len(vanilla_lengths):.1f}, "
          f"Min: {min(vanilla_lengths)}, Max: {max(vanilla_lengths)}")
    print(f"  Variations - Avg: {sum(variation_lengths)/len(variation_lengths):.1f}, "
          f"Min: {min(variation_lengths)}, Max: {max(variation_lengths)}")
    
    # Box plot for length comparison
    ax2.boxplot([vanilla_lengths, variation_lengths], labels=['Vanilla', 'Variations'])
    ax2.set_title('NL Prompt Length Distribution', fontweight='bold')
    ax2.set_ylabel('Word Count')
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('visualizations_verify/nl_prompt_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 7. Perturbation Technique Detection (heuristic)
    technique_counts = {
        'Code-Switching (SQL keywords)': 0,
        'Verbose': 0,
        'Fluff (conversational)': 0,
        'Symbols (>, =, <)': 0,
        'Lexical Variation': 0
    }
    
    fluff_markers = ['I need to', 'Please', 'Can you', "Let's", 'Help me', 
                     'thanks', 'please', 'for me', 'if possible']
    verbose_markers = ['I need to retrieve the following', 'from the table named', 
                       'specifically filtering']
    lexical_markers = ['Retrieve', 'Fetch', 'Find', 'Pull', 'Show']
    
    for d in data:
        for var in d.get('nl_prompt_variations', []):
            # Code-switching: uppercase SQL keywords
            if any(kw in var for kw in ['SELECT', 'FROM', 'WHERE', 'GROUP BY']):
                technique_counts['Code-Switching (SQL keywords)'] += 1
            
            # Verbose
            if any(marker in var for marker in verbose_markers):
                technique_counts['Verbose'] += 1
            
            # Fluff
            if any(marker in var for marker in fluff_markers):
                technique_counts['Fluff (conversational)'] += 1
            
            # Symbols
            if any(sym in var for sym in [' > ', ' < ', ' = ', ' >= ', ' <= ']):
                technique_counts['Symbols (>, =, <)'] += 1
            
            # Lexical variation
            if any(marker in var for marker in lexical_markers):
                technique_counts['Lexical Variation'] += 1
    
    print("\n5. Perturbation Technique Usage (in variations):")
    print("-" * 30)
    for k, v in sorted(technique_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {k}: {v} ({v/(len(data)*3)*100:.1f}%)")
    
    plt.figure(figsize=(12, 6))
    plt.barh(list(technique_counts.keys()), list(technique_counts.values()), 
             color='#9b59b6')
    plt.title('Perturbation Technique Usage Across All Variations', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Count')
    plt.tight_layout()
    plt.savefig('visualizations_verify/perturbation_techniques.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 8. Summary Statistics
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    print(f"Total SQL Queries: {len(data)}")
    print(f"Total NL Prompts Generated: {len(data) * 4} (1 vanilla + 3 variations)")
    print(f"Uniqueness Rate: {all_unique/len(data)*100:.1f}% (all 3 variations unique)")
    print(f"Average Vanilla Prompt Length: {sum(vanilla_lengths)/len(vanilla_lengths):.1f} words")
    print(f"Average Variation Prompt Length: {sum(variation_lengths)/len(variation_lengths):.1f} words")
    print("="*60)
    
    print(f"\n✓ All visualizations saved to visualizations_verify/ directory")

if __name__ == "__main__":
    analyze_and_visualize()
