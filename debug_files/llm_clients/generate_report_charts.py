
import matplotlib.pyplot as plt
import os

OUTPUT_DIR = '../../prog_report/2026-01-02/images'

def setup_dir():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, OUTPUT_DIR)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    return output_path

def generate_charts():
    output_dir = setup_dir()
    
    # Style settings
    plt.style.use('ggplot')
    
    # 1. Applicability Bar Chart
    # Use horizontal bar for better readability of labels
    labels = [
        'Typos (100%)', 'Synonyms (99.5%)', 'Column Vars (99%)', 
        'Under Spec (95.6%)', 'Ambiguos Pronouns (86.2%)', 
        'Implicit Logic (67.6%)', 'Missing WHERE (62.5%)', 
        'Relative Temp (23.8%)', 'Incomplete Joins (20.2%)', 
        'Vague Agg (14.3%)'
    ]
    values = [100, 99.5, 99.0, 95.6, 86.2, 67.6, 62.5, 23.8, 20.2, 14.3]
    
    # Sort for visual appeal
    zipped = sorted(zip(labels, values), key=lambda x: x[1])
    sorted_labels, sorted_values = zip(*zipped)

    plt.figure(figsize=(10, 8))
    bars = plt.barh(sorted_labels, sorted_values, color='skyblue')
    plt.xlabel('Applicability Rate (%)')
    plt.title('Perturbation Applicability by Type')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'applicability_chart.png'))
    plt.close()

    # 2. Top Compounds Bar Chart
    comp_labels = [
        'Synonyms+Typos+UnderSpec', 
        'RelTemp+Typos+UnderSpec', 
        'Typos+UnderSpec+VagueAgg', 
        'ColVars+Typos+UnderSpec',
        'ColVars+Synonyms+Typos+UnderSpec'
    ]
    comp_counts = [625, 193, 135, 128, 115]
    
    # Reverse for top-down view
    plt.figure(figsize=(10, 6))
    plt.barh(comp_labels[::-1], comp_counts[::-1], color='lightgreen')
    plt.xlabel('Count')
    plt.title('Top 5 Compound Perturbation Combinations')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'top_compounds_chart.png'))
    plt.close()

    print(f"Charts saved to {output_dir}")

if __name__ == "__main__":
    generate_charts()
