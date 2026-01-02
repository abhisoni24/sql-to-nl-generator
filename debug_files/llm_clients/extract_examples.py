
import json
import os

INPUT_FILE = '../../dataset/current/nl_social_media_queries_perturbed.json'

def extract_examples():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, INPUT_FILE)

    with open(input_path, 'r') as f:
        data = json.load(f)

    complexities = ['simple', 'join', 'aggregate', 'advanced', 'insert', 'update', 'delete']
    found = {}

    for item in data:
        comp = item.get('complexity')
        if comp in complexities and comp not in found:
            found[comp] = item
        if len(found) == len(complexities):
            break

    print("\n## 6. Dataset Examples by Complexity")
    print("\nBelow are representative examples for each complexity type, showing the original prompt, SQL, and the generated perturbations.")

    for comp in complexities:
        item = found.get(comp)
        if not item:
            continue
            
        print(f"\n### {comp.capitalize()}")
        print(f"- **ID:** `{item['id']}`")
        print(f"- **Original Prompt:** \"{item['nl_prompt']}\"")
        print(f"- **SQL:** `{item['sql']}`")
        
        gen = item.get('generated_perturbations', {})
        singles = gen.get('single_perturbations', [])
        compound = gen.get('compound_perturbation', {})

        # Show all single perturbations
        print("\n**Single Perturbations (10):**")
        for p in singles:
            # Always show all 10 as requested, even if applicable is false? 
            # The user said "include the whole thing". 
            # Usually only applicable ones are interesting, but let's stick to what is "returned".
            # The previous code filtered `if p['applicable']`. 
            # I'll keep the filter if that's what constitutes "results", but usually 10 are generated.
            # Let's show all and mark applicable status if needed, or just show the applicable ones if that's the "result".
            # "results after perturbed prompts generation" implies the valid ones.
            # But the user said "each 10 simple prompts".
            # Let's double check if I have 10 applicable ones. 
            # In the report, I said "Typos" is 100% applicable. So most will be applicable.
            # I will show all and indicate if not applicable.
            
            status_icon = "✅" if p['applicable'] else "❌"
            applicability_str = "" if p['applicable'] else f" _(Not Applicable: {p.get('reason_not_applicable')})_"
            print(f"- {status_icon} **{p['perturbation_name']}:** \"{p['perturbed_nl_prompt']}\"{applicability_str}")
        
        # Show compound
        print(f"\n**Compound Perturbation:**")
        print(f"- \"{compound.get('perturbed_nl_prompt', 'N/A')}\"")
        applied = [x['perturbation_name'] for x in compound.get('perturbations_applied', [])]
        print(f"  - _Applied: {', '.join(applied)}_")
        print("\n---")

if __name__ == "__main__":
    extract_examples()
