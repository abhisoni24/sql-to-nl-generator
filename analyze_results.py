import json
import matplotlib.pyplot as plt
import os
from collections import Counter

def analyze_and_visualize():
    if not os.path.exists('social_media_queries.json'):
        print("Error: social_media_queries.json not found. Run main.py first.")
        return

    with open('social_media_queries.json', 'r') as f:
        data = json.load(f)
        
    # 1. Complexity Distribution
    complexities = [d['complexity'] for d in data]
    comp_counts = Counter(complexities)
    
    plt.figure(figsize=(10, 6))
    plt.pie(comp_counts.values(), labels=comp_counts.keys(), autopct='%1.1f%%', startangle=140)
    plt.title('Query Complexity Distribution')
    plt.axis('equal')
    plt.savefig('visualizations/complexity_distribution.png')
    plt.close()
    
    # 2. Table Usage Frequency
    all_tables = []
    for d in data:
        # Simple extraction, might need more robust parsing if table names are complex
        # But our generator stores them in "tables" key (though main.py logic for that was simple)
        # Let's re-extract from SQL string to be safe or rely on metadata if robust
        # The main.py logic `[t.name for t in query_ast.find_all(lambda x: x.key == "table")]` is decent but might miss aliases or be empty
        # Let's trust the metadata for now, but clean it up
        tables = d.get('tables', [])
        # Filter out empty or None
        tables = [t for t in tables if t]
        all_tables.extend(tables)
        
    table_counts = Counter(all_tables)
    
    plt.figure(figsize=(10, 6))
    plt.bar(table_counts.keys(), table_counts.values())
    plt.title('Table Usage Frequency')
    plt.xlabel('Table Name')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('visualizations/table_usage.png')
    plt.close()
    
    print("Visualizations saved to visualizations/ directory.")

    # 3. Keyword Coverage Metrics
    keywords = ['WHERE', 'GROUP BY', 'HAVING', 'ORDER BY', 'LIMIT', 'JOIN', 'LEFT JOIN', 'DATE_SUB', 'INTERVAL', 'LIKE', 'IN', 'SELECT']
    keyword_counts = {k: 0 for k in keywords}
    
    # Add 'Subquery' as a special category
    keyword_counts['Subquery'] = 0
    
    for d in data:
        sql = d['sql'].upper()
        for k in keywords:
            if k in sql:
                keyword_counts[k] += 1
        
        # Naive subquery check (presence of nested SELECT)
        # A better check would be looking at complexity or parsing, but string check is a good proxy for now
        if "SELECT" in sql[7:]: # Skip the first SELECT
             keyword_counts['Subquery'] += 1

    # Print metrics to console
    print("\nKeyword Coverage Metrics:")
    print("-" * 30)
    for k, v in keyword_counts.items():
        print(f"{k}: {v} ({v/len(data)*100:.1f}%)")
        
    # Visualize Metrics
    plt.figure(figsize=(12, 6))
    plt.bar(keyword_counts.keys(), keyword_counts.values(), color='skyblue')
    plt.title('SQL Feature Coverage')
    plt.xlabel('Feature')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('visualizations/feature_coverage.png')
    plt.close()

    # 4. Query Type Distribution
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
            
    # Print metrics
    print("\nQuery Type Distribution:")
    print("-" * 30)
    for k, v in query_types.items():
        print(f"{k}: {v} ({v/len(data)*100:.1f}%)")

    # Visualize Query Types
    plt.figure(figsize=(8, 8))
    plt.pie(query_types.values(), labels=query_types.keys(), autopct='%1.1f%%', startangle=140, colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
    plt.title('Query Type Distribution')
    plt.axis('equal')
    plt.savefig('visualizations/query_type_distribution.png')
    plt.close()

if __name__ == "__main__":
    analyze_and_visualize()
