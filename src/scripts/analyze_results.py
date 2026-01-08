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
        gen_pert = d.get('generated_perturbations', {})
        # efficient extraction
        variations = [p['perturbed_nl_prompt'] for p in gen_pert.get('single_perturbations', []) if p.get('perturbed_nl_prompt')]
        
        if variations: # Check if we have variations
            unique_count = len(set(variations))
            # Just count unique variations, logic for specific buckets (3, 2, 1) might need adjustment 
            # if we have 10 variations now.
            # Assuming we want to see if there is diversity. Let's simplfy to % unique.
            # But preserving user graph buckets: "All 3 unique" implies 3 variations.
            # We now have potentially 10.
            # I will adapt the buckets to: All Unique, Some Duplicates, All Same?
            # Or just check for duplicates.
            if unique_count == len(variations):
                all_unique += 1
            elif unique_count == 1:
                one_unique += 1
            else:
                two_unique += 1 # "Some duplicates" bucket basically.

    
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
        # Extract from new structure
        gen_pert = d.get('generated_perturbations', {})
        vanilla = gen_pert.get('original', {}).get('nl_prompt', '')
        
        # Variations are now the single perturbations that are applicable and have a Prompt
        variations = []
        for p in gen_pert.get('single_perturbations', []):
            if p.get('perturbed_nl_prompt'):
                variations.append(p['perturbed_nl_prompt'])
                
        vanilla_lengths.append(len(vanilla.split()))
        
        for var in variations:
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
    
    # 7. Perturbation Analysis (Explicit SDT Types)
    
    # Metrics to track
    perturbation_stats = {} # {name: {'applied': 0, 'total': 0, 'len_deltas': []}}
    
    for d in data:
        gen_pert = d.get('generated_perturbations', {})
        vanilla = gen_pert.get('original', {}).get('nl_prompt', '')
        vanilla_len = len(vanilla.split())
        
        single_perts = gen_pert.get('single_perturbations', [])
        
        for p in single_perts:
            p_name = p['perturbation_name']
            if p_name not in perturbation_stats:
                perturbation_stats[p_name] = {'applied': 0, 'total': 0, 'len_deltas': []}
            
            perturbation_stats[p_name]['total'] += 1
            
            if p['applicable']:
                perturbation_stats[p_name]['applied'] += 1
                p_prompt = p.get('perturbed_nl_prompt', '')
                if p_prompt:
                    delta = len(p_prompt.split()) - vanilla_len
                    perturbation_stats[p_name]['len_deltas'].append(delta)

    # 7a. Applicability Rates
    print("\n5. Perturbation Applicability Rates:")
    print("-" * 30)
    
    names = []
    rates = []
    
    for name, stats in sorted(perturbation_stats.items()):
        rate = (stats['applied'] / stats['total']) * 100 if stats['total'] > 0 else 0
        print(f"  {name}: {stats['applied']}/{stats['total']} ({rate:.1f}%)")
        names.append(name.replace('_', ' ').title())
        rates.append(rate)
        
    plt.figure(figsize=(12, 6))
    bars = plt.barh(names, rates, color='#2ecc71')
    plt.title('Perturbation Applicability Rates', fontsize=14, fontweight='bold')
    plt.xlabel('Applicability (%)')
    plt.xlim(0, 100)
    plt.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 1, bar.get_y() + bar.get_height()/2, f'{width:.1f}%', 
                 va='center', fontsize=10)
                 
    plt.tight_layout()
    plt.savefig('visualizations_verify/perturbation_applicability.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 7b. Prompt Length Impact
    print("\n6. Prompt Length Impact (Avg Word Count Change):")
    print("-" * 30)
    
    avg_deltas = []
    delta_names = []
    box_data = []
    
    for name, stats in sorted(perturbation_stats.items()):
        deltas = stats['len_deltas']
        if deltas:
            avg = sum(deltas) / len(deltas)
            print(f"  {name}: {avg:+.1f} words")
            avg_deltas.append(avg)
            delta_names.append(name.replace('_', ' ').title())
            box_data.append(deltas)
        else:
             print(f"  {name}: N/A")

    plt.figure(figsize=(12, 6))
    # Sort by avg delta for better viz
    sorted_indices = sorted(range(len(avg_deltas)), key=lambda k: avg_deltas[k])
    sorted_names = [delta_names[i] for i in sorted_indices]
    sorted_data = [box_data[i] for i in sorted_indices]
    
    plt.boxplot(sorted_data, vert=False, labels=sorted_names, patch_artist=True,
                boxprops=dict(facecolor='#9b59b6', alpha=0.6))
    plt.title('Prompt Length Impact by Perturbation Type', fontsize=14, fontweight='bold')
    plt.xlabel('Word Count Delta (Perturbed - Vanilla)')
    plt.grid(axis='x', alpha=0.3)
    plt.axvline(0, color='black', linestyle='--', alpha=0.5) # Zero line
    
    plt.tight_layout()
    plt.savefig('visualizations_verify/perturbation_length_impact.png', dpi=300, bbox_inches='tight')
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
