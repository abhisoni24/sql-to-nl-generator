import json
import sys

def extract_samples():
    """Extract one complete entry per complexity type for evaluation."""
    
    with open('dataset/current/nl_social_media_queries.json', 'r') as f:
        data = json.load(f)
    
    complexity_types = ['simple', 'join', 'aggregate', 'advanced', 'insert', 'update', 'delete']
    samples = {}
    
    for complexity in complexity_types:
        for entry in data:
            if entry['complexity'] == complexity:
                samples[complexity] = entry
                break
    
    # Save to file for inspection
    with open('prog_report/sample_entries.json', 'w') as f:
        json.dump(samples, f, indent=2)
    
    print(f"Extracted {len(samples)} sample entries")
    for c, entry in samples.items():
        print(f"\n{c.upper()}:")
        print(f"  SQL: {entry['sql'][:80]}...")
        print(f"  ID: {entry['id']}")

if __name__ == "__main__":
    extract_samples()
