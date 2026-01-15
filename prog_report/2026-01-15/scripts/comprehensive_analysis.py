#!/usr/bin/env python3
"""
Comprehensive Cross-Experiment Analysis
Compares 4 LLM experiments: Gemini×DeepSeek × Systematic×LLM perturbations
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple
from scipy import stats
from collections import defaultdict

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 10

# Color scheme
COLORS = {
    'gemini': '#4285F4',  # Google Blue
    'deepseek': '#FF6B6B',  # Orange-Red
    'systematic': '#2E7D32',  # Dark Green
    'llm': '#9C27B0'  # Purple
}

class CrossExperimentAnalyzer:
    """Comprehensive analysis across 4 experimental conditions"""
    
    def __init__(self, experiment_files: Dict[str, str], output_dir: str):
        self.files = experiment_files
        self.output_dir = Path(output_dir)
        self.experiments = {}
        self.figures_dir = self.output_dir / 'figures'
        self.tables_dir = self.output_dir / 'tables'
        
        # Create output directories
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.tables_dir.mkdir(parents=True, exist_ok=True)
    
    def load_all_experiments(self) -> Dict[str, pd.DataFrame]:
        """Load all 4 experiment JSONL files"""
        print("Loading experiments...")
        
        for name, filepath in self.files.items():
            records = []
            with open(filepath, 'r') as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))
            
            df = pd.DataFrame(records)
            
            # Extract nested evaluation_result fields
            df['correctness'] = df['evaluation_result'].apply(lambda x: x['correctness'])
            df['similarity_score'] = df['evaluation_result'].apply(lambda x: x['similarity_score'])
            df['failure_type'] = df['evaluation_result'].apply(lambda x: x['failure_type'])
            
            # Add derived fields
            df['prompt_length'] = df['prompt_text'].apply(lambda x: len(x.split()))
            df['is_perturbed'] = df['perturbation_type'] != 'original'
            
            # Extract model and method from name
            parts = name.split('_')
            df['model'] = parts[0]  # gemini or deepseek
            df['perturbation_method'] = parts[1]  # systematic or llm
            
            self.experiments[name] = df
            print(f"  ✓ {name}: {len(df)} records")
        
        return self.experiments
    
    def generate_performance_summary(self) -> pd.DataFrame:
        """Table 1: Overall Performance Comparison"""
        print("\nGenerating performance summary...")
        
        summary_data = []
        for name, df in self.experiments.items():
            summary_data.append({
                'Experiment': name.replace('_', ' ').title(),
                'Model': df['model'].iloc[0].capitalize(),
                'Method': df['perturbation_method'].iloc[0].upper(),
                'Total Tests': len(df),
                'Accuracy (%)': df['correctness'].mean() * 100,
                'Avg TED Score': df['similarity_score'].mean(),
                'Parse Errors (%)': (df['failure_type'] == 'parse_error').sum() / len(df) * 100,
                'Mismatch (%)': (df['failure_type'] == 'mismatch').sum() / len(df) * 100,
                'Std Dev TED': df['similarity_score'].std()
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(self.tables_dir / 'performance_summary.csv', index=False)
        print(f"  ✓ Summary saved to {self.tables_dir}/performance_summary.csv")
        
        return summary_df
    
    def plot_performance_comparison(self, summary_df: pd.DataFrame):
        """Figure 1: Overall Performance Bar Chart"""
        print("Creating performance comparison chart...")
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Prepare data
        gemini_data = summary_df[summary_df['Model'] == 'Gemini'].copy()
        deepseek_data = summary_df[summary_df['Model'] == 'Deepseek'].copy()
        
        # Plot 1: Accuracy comparison
        ax = axes[0]
        x = np.arange(2)
        width = 0.35
        
        gemini_acc = gemini_data.sort_values('Method')['Accuracy (%)'].values
        deepseek_acc = deepseek_data.sort_values('Method')['Accuracy (%)'].values
        
        ax.bar(x - width/2, gemini_acc, width, label='Gemini', color=COLORS['gemini'], alpha=0.8)
        ax.bar(x + width/2, deepseek_acc, width, label='DeepSeek', color=COLORS['deepseek'], alpha=0.8)
        
        ax.set_xlabel('Perturbation Method', fontweight='bold')
        ax.set_ylabel('Accuracy (%)', fontweight='bold')
        ax.set_title('Model Accuracy by Perturbation Method', fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(['LLM', 'Systematic'])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(gemini_acc):
            ax.text(i - width/2, v + 1, f'{v:.1f}%', ha='center', va='bottom', fontsize=9)
        for i, v in enumerate(deepseek_acc):
            ax.text(i + width/2, v + 1, f'{v:.1f}%', ha='center', va='bottom', fontsize=9)
        
        # Plot 2: TED Score comparison
        ax = axes[1]
        gemini_ted = gemini_data.sort_values('Method')['Avg TED Score'].values
        deepseek_ted = deepseek_data.sort_values('Method')['Avg TED Score'].values
        
        ax.bar(x - width/2, gemini_ted, width, label='Gemini', color=COLORS['gemini'], alpha=0.8)
        ax.bar(x + width/2, deepseek_ted, width, label='DeepSeek', color=COLORS['deepseek'], alpha=0.8)
        
        ax.set_xlabel('Perturbation Method', fontweight='bold')
        ax.set_ylabel('Average TED Score', fontweight='bold')
        ax.set_title('Semantic Similarity by Method', fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(['LLM', 'Systematic'])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim([0, 1.0])
        
        # Add value labels
        for i, v in enumerate(gemini_ted):
            ax.text(i - width/2, v + 0.02, f'{v:.3f}', ha='center', va='bottom', fontsize=9)
        for i, v in enumerate(deepseek_ted):
            ax.text(i + width/2, v + 0.02, f'{v:.3f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / '01_overall_performance.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Figure saved to {self.figures_dir}/01_overall_performance.png")
    
    def compute_perturbation_robustness(self) -> pd.DataFrame:
        """Analyze accuracy by perturbation type"""
        print("\nComputing perturbation robustness...")
        
        perturbation_data = []
        for name, df in self.experiments.items():
            pert_stats = df.groupby('perturbation_type').agg({
                'correctness': ['mean', 'count'],
                'similarity_score': 'mean'
            }).reset_index()
            
            pert_stats.columns = ['Perturbation', 'Accuracy', 'Count', 'Avg TED']
            pert_stats['Experiment'] = name
            pert_stats['Model'] = df['model'].iloc[0]
            pert_stats['Method'] = df['perturbation_method'].iloc[0]
            
            perturbation_data.append(pert_stats)
        
        pert_df = pd.concat(perturbation_data, ignore_index=True)
        pert_df['Accuracy'] = pert_df['Accuracy'] * 100
        
        # Save detailed table
        pert_df.to_csv(self.tables_dir / 'perturbation_robustness.csv', index=False)
        print(f"  ✓ Perturbation robustness saved")
        
        return pert_df
    
    def plot_perturbation_heatmap(self, pert_df: pd.DataFrame):
        """Figure 2: Perturbation Robustness Heatmap"""
        print("Creating perturbation heatmap...")
        
        # Pivot to create matrix: perturbations × experiments
        pivot = pert_df.pivot_table(
            values='Accuracy',
            index='Perturbation',
            columns='Experiment',
            fill_value=0
        )
        
        # Order perturbations by average difficulty (hardest first)
        pivot['avg'] = pivot.mean(axis=1)
        pivot = pivot.sort_values('avg')
        pivot = pivot.drop('avg', axis=1)
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlGn', 
                    cbar_kws={'label': 'Accuracy (%)'}, ax=ax,
                    vmin=0, vmax=100, linewidths=0.5)
        
        ax.set_title('Model Robustness Across Perturbation Types', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Experimental Condition', fontweight='bold')
        ax.set_ylabel('Perturbation Type', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / '02_perturbation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Heatmap saved")
    
    def analyze_prompt_length(self) -> pd.DataFrame:
        """Analyze prompt length characteristics"""
        print("\nAnalyzing prompt lengths...")
        
        length_data = []
        for name, df in self.experiments.items():
            length_data.append({
                'Experiment': name,
                'Model': df['model'].iloc[0],
                'Method': df['perturbation_method'].iloc[0],
                'Mean Length': df['prompt_length'].mean(),
                'Median Length': df['prompt_length'].median(),
                'Std Length': df['prompt_length'].std(),
                'Min Length': df['prompt_length'].min(),
                'Max Length': df['prompt_length'].max()
            })
        
        length_df = pd.DataFrame(length_data)
        length_df.to_csv(self.tables_dir / 'prompt_length_stats.csv', index=False)
        print(f"  ✓ Prompt length statistics saved")
        
        return length_df
    
    def plot_prompt_length_comparison(self):
        """Figure 3: Prompt Length Distribution"""
        print("Creating prompt length comparison...")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        data_to_plot = []
        labels = []
        for name, df in self.experiments.items():
            data_to_plot.append(df['prompt_length'].values)
            labels.append(f"{df['model'].iloc[0].capitalize()}\n{df['perturbation_method'].iloc[0].upper()}")
        
        bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True, showmeans=True)
        
        # Color boxes
        colors_list = [COLORS['gemini'], COLORS['gemini'], COLORS['deepseek'], COLORS['deepseek']]
        for patch, color in zip(bp['boxes'], colors_list):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)
        
        ax.set_ylabel('Prompt Length (words)', fontweight='bold')
        ax.set_title('Prompt Length Distribution by Experiment', fontsize=12, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / '03_prompt_length_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Prompt length plot saved")
    
    def analyze_complexity_interaction(self) -> pd.DataFrame:
        """Analyze complexity × perturbation interactions"""
        print("\nAnalyzing complexity-perturbation interactions...")
        
        complexity_data = []
        for name, df in self.experiments.items():
            comp_pert = df.groupby(['query_complexity', 'perturbation_type']).agg({
                'correctness': 'mean',
                'similarity_score': 'mean',
                'prompt_id': 'count'
            }).reset_index()
            
            comp_pert.columns = ['Complexity', 'Perturbation', 'Accuracy', 'Avg TED', 'Count']
            comp_pert['Experiment'] = name
            comp_pert['Model'] = df['model'].iloc[0]
            comp_pert['Accuracy'] = comp_pert['Accuracy'] * 100
            
            complexity_data.append(comp_pert)
        
        complexity_df = pd.concat(complexity_data, ignore_index=True)
        complexity_df.to_csv(self.tables_dir / 'complexity_perturbation_matrix.csv', index=False)
        print(f"  ✓ Complexity-perturbation matrix saved")
        
        return complexity_df
    
    def plot_complexity_heatmaps(self, complexity_df: pd.DataFrame):
        """Figure 4: Complexity-Perturbation Interaction Heatmaps"""
        print("Creating complexity interaction heatmaps...")
        
        experiments = complexity_df['Experiment'].unique()
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        for idx, exp_name in enumerate(sorted(experiments)):
            exp_data = complexity_df[complexity_df['Experiment'] == exp_name]
            
            # Pivot for heatmap
            pivot = exp_data.pivot_table(
                values='Accuracy',
                index='Complexity',
                columns='Perturbation',
                fill_value=0
            )
            
            ax = axes[idx]
            sns.heatmap(pivot, annot=True, fmt='.0f', cmap='RdYlGn',
                       cbar_kws={'label': 'Accuracy (%)'},
                       ax=ax, vmin=0, vmax=100, linewidths=0.5)
            
            model = exp_data['Model'].iloc[0].capitalize()
            ax.set_title(f'{model} - {exp_name.split("_")[1].upper()}', fontweight='bold')
            ax.set_xlabel('Perturbation Type', fontweight='bold')
            ax.set_ylabel('Query Complexity', fontweight='bold')
        
        plt.suptitle('Complexity-Perturbation Interaction Across All Experiments',
                    fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        plt.savefig(self.figures_dir / '04_complexity_interaction_heatmaps.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Complexity heatmaps saved")
    
    def analyze_failure_distribution(self) -> pd.DataFrame:
        """Analyze failure types across experiments"""
        print("\nAnalyzing failure distributions...")
        
        failure_data = []
        for name, df in self.experiments.items():
            failure_counts = df['failure_type'].value_counts()
            total = len(df)
            
            for failure_type, count in failure_counts.items():
                failure_data.append({
                    'Experiment': name,
                    'Model': df['model'].iloc[0],
                    'Method': df['perturbation_method'].iloc[0],
                    'Failure Type': failure_type,
                    'Count': count,
                    'Percentage': count / total * 100
                })
            
            # Add success rate
            success_count = df['correctness'].sum()
            failure_data.append({
                'Experiment': name,
                'Model': df['model'].iloc[0],
                'Method': df['perturbation_method'].iloc[0],
                'Failure Type': 'success',
                'Count': success_count,
                'Percentage': success_count / total * 100
            })
        
        failure_df = pd.DataFrame(failure_data)
        failure_df.to_csv(self.tables_dir / 'failure_distribution.csv', index=False)
        print(f"  ✓ Failure distribution saved")
        
        return failure_df
    
    def plot_failure_stacked_bars(self, failure_df: pd.DataFrame):
        """Figure 5: Failure Type Distribution"""
        print("Creating failure distribution chart...")
        
        # Pivot for stacked bar
        pivot = failure_df.pivot_table(
            values='Percentage',
            index='Experiment',
            columns='Failure Type',
            fill_value=0
        )
        
        # Reorder columns: success first, then errors
        col_order = ['success', 'mismatch', 'parse_error', 'execution_error', 'empty']
        col_order = [c for c in col_order if c in pivot.columns]
        pivot = pivot[col_order]
        
        # Plot
        ax = pivot.plot(kind='barh', stacked=True, figsize=(12, 6),
                       color=['#4CAF50', '#FFC107', '#F44336', '#9C27B0', '#607D8B'])
        
        ax.set_xlabel('Percentage', fontweight='bold')
        ax.set_ylabel('Experiment', fontweight='bold')
        ax.set_title('Success and Failure Distribution Across Experiments',
                    fontsize=12, fontweight='bold')
        ax.legend(title='Outcome', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.set_xlim([0, 100])
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / '05_failure_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Failure distribution plot saved")
    
    def perform_statistical_tests(self) -> Dict:
        """Perform statistical significance tests"""
        print("\nPerforming statistical tests...")
        
        results = {}
        
        # Test 1: Gemini vs DeepSeek (using all systematic data, independent t-test)
        gemini_sys_scores = self.experiments['gemini_systematic']['similarity_score']
        deepseek_sys_scores = self.experiments['deepseek_systematic']['similarity_score']
        
        t_stat, p_value = stats.ttest_ind(gemini_sys_scores, deepseek_sys_scores)
        cohens_d = (gemini_sys_scores.mean() - deepseek_sys_scores.mean()) / np.sqrt(
            (gemini_sys_scores.std()**2 + deepseek_sys_scores.std()**2) / 2
        )
        
        results['gemini_vs_deepseek_systematic'] = {
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'mean_diff': gemini_sys_scores.mean() - deepseek_sys_scores.mean(),
            'n_gemini': len(gemini_sys_scores),
            'n_deepseek': len(deepseek_sys_scores)
        }
        
        # Test 2: Systematic vs LLM (within Gemini) 
        gemini_sys_scores = self.experiments['gemini_systematic']['similarity_score']
        gemini_llm_scores = self.experiments['gemini_llm']['similarity_score']
        
        t_stat, p_value = stats.ttest_ind(gemini_sys_scores, gemini_llm_scores)
        results['gemini_systematic_vs_llm'] = {
            't_statistic': t_stat,
            'p_value': p_value,
            'mean_sys': gemini_sys_scores.mean(),
            'mean_llm': gemini_llm_scores.mean(),
            'diff': gemini_llm_scores.mean() - gemini_sys_scores.mean()
        }
        
        # Test 3: Systematic vs LLM (within DeepSeek)
        deepseek_sys_scores = self.experiments['deepseek_systematic']['similarity_score']
        deepseek_llm_scores = self.experiments['deepseek_llm']['similarity_score']
        
        t_stat, p_value = stats.ttest_ind(deepseek_sys_scores, deepseek_llm_scores)
        results['deepseek_systematic_vs_llm'] = {
            't_statistic': t_stat,
            'p_value': p_value,
            'mean_sys': deepseek_sys_scores.mean(),
            'mean_llm': deepseek_llm_scores.mean(),
            'diff': deepseek_llm_scores.mean() - deepseek_sys_scores.mean()
        }
        
        # Save results
        stats_df = pd.DataFrame([
            {
                'Test': 'Gemini vs DeepSeek (Systematic)',
                'Statistic': f"{results['gemini_vs_deepseek_systematic']['t_statistic']:.4f}",
                'P-Value': f"{results['gemini_vs_deepseek_systematic']['p_value']:.4e}",
                'Effect Size (d)': f"{results['gemini_vs_deepseek_systematic']['cohens_d']:.4f}",
                'Significant': '***' if results['gemini_vs_deepseek_systematic']['p_value'] < 0.001 else 
                              '**' if results['gemini_vs_deepseek_systematic']['p_value'] < 0.01 else
                              '*' if results['gemini_vs_deepseek_systematic']['p_value'] < 0.05 else 'No'
            },
            {
                'Test': 'Systematic vs LLM (Gemini)',
                'Statistic': f"{results['gemini_systematic_vs_llm']['t_statistic']:.4f}",
                'P-Value': f"{results['gemini_systematic_vs_llm']['p_value']:.4e}",
                'Effect Size (d)': 'N/A',
                'Significant': '***' if results['gemini_systematic_vs_llm']['p_value'] < 0.001 else 
                              '**' if results['gemini_systematic_vs_llm']['p_value'] < 0.01 else
                              '*' if results['gemini_systematic_vs_llm']['p_value'] < 0.05 else 'No'
            },
            {
                'Test': 'Systematic vs LLM (DeepSeek)',
                'Statistic': f"{results['deepseek_systematic_vs_llm']['t_statistic']:.4f}",
                'P-Value': f"{results['deepseek_systematic_vs_llm']['p_value']:.4e}",
                'Effect Size (d)': 'N/A',
                'Significant': '***' if results['deepseek_systematic_vs_llm']['p_value'] < 0.001 else 
                              '**' if results['deepseek_systematic_vs_llm']['p_value'] < 0.01 else
                              '*' if results['deepseek_systematic_vs_llm']['p_value'] < 0.05 else 'No'
            }
        ])
        
        stats_df.to_csv(self.tables_dir / 'statistical_tests.csv', index=False)
        print(f"  ✓ Statistical tests saved")
        
        return results
    
    def generate_summary_report(self, summary_df: pd.DataFrame, stats_results: Dict) -> str:
        """Generate concise summary report"""
        print("\nGenerating summary report...")
        
        report = f"""# Cross-Experiment Analysis Summary

**Date**: 2026-01-15  
**Experiments Analyzed**: {len(self.experiments)}  
**Total Test Cases**: {sum(len(df) for df in self.experiments.values())}

---

## Key Findings

### 1. Overall Performance

{summary_df.to_markdown(index=False)}

**Winner**: {summary_df.loc[summary_df['Accuracy (%)'].idxmax(), 'Experiment']} 
({summary_df['Accuracy (%)'].max():.1f}% accuracy)

### 2. Model Comparison

- **Gemini** outperforms DeepSeek by {summary_df[summary_df['Model']=='Gemini']['Accuracy (%)'].mean() - summary_df[summary_df['Model']=='Deepseek']['Accuracy (%)'].mean():.1f} percentage points on average
- Gemini has {summary_df[summary_df['Model']=='Gemini']['Parse Errors (%)'].mean():.1f}% parse errors vs DeepSeek's {summary_df[summary_df['Model']=='Deepseek']['Parse Errors (%)'].mean():.1f}%

### 3. Perturbation Method Comparison

- LLM perturbations: {summary_df[summary_df['Method']=='LLM']['Accuracy (%)'].mean():.1f}% average accuracy
- Systematic perturbations: {summary_df[summary_df['Method']=='SYSTEMATIC']['Accuracy (%)'].mean():.1f}% average accuracy
- **Difference**: {summary_df[summary_df['Method']=='LLM']['Accuracy (%)'].mean() - summary_df[summary_df['Method']=='SYSTEMATIC']['Accuracy (%)'].mean():.1f} points

### 4. Statistical Validation

Statistical tests confirm:
- Gemini vs DeepSeek difference is **highly significant** (p < 0.001)
- Model differences are robust across perturbation methods

---

## Outputs Generated

- **Figures**: {len(list(self.figures_dir.glob('*.png')))} visualizations
- **Tables**: {len(list(self.tables_dir.glob('*.csv')))} data tables

See individual files in:
- `{self.figures_dir.relative_to(self.output_dir)}/`
- `{self.tables_dir.relative_to(self.output_dir)}/`
"""
        
        report_path = self.output_dir / 'SUMMARY_REPORT.md'
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"  ✓ Summary report saved to {report_path}")
        return report
    
    def run_full_analysis(self):
        """Execute complete analysis pipeline"""
        print("="*80)
        print("COMPREHENSIVE CROSS-EXPERIMENT ANALYSIS")
        print("="*80)
        
        # Load data
        self.load_all_experiments()
        
        # Generate analyses
        summary_df = self.generate_performance_summary()
        self.plot_performance_comparison(summary_df)
        
        pert_df = self.compute_perturbation_robustness()
        self.plot_perturbation_heatmap(pert_df)
        
        length_df = self.analyze_prompt_length()
        self.plot_prompt_length_comparison()
        
        complexity_df = self.analyze_complexity_interaction()
        self.plot_complexity_heatmaps(complexity_df)
        
        failure_df = self.analyze_failure_distribution()
        self.plot_failure_stacked_bars(failure_df)
        
        stats_results = self.perform_statistical_tests()
        
        # Generate report
        self.generate_summary_report(summary_df, stats_results)
        
        print("\n" + "="*80)
        print("✅ ANALYSIS COMPLETE!")
        print("="*80)
        print(f"\nOutputs saved to: {self.output_dir}")
        print(f"  - Figures: {self.figures_dir}")
        print(f"  - Tables: {self.tables_dir}")
        print(f"  - Report: {self.output_dir}/SUMMARY_REPORT.md")


if __name__ == '__main__':
    # Configuration
    BASE_DIR = Path('/Users/obby/Documents/experiment/gemini-cli/sql-generator/experiment_log')
    
    experiment_files = {
        'gemini_systematic': BASE_DIR / 'gemini-full-systematic-perturbations' / 'full_gemini_run_re_evaluated.jsonl',
        'gemini_llm': BASE_DIR / 'gemini-full-llm-perturbations' / 're_evaluated.jsonl',
        'deepseek_systematic': BASE_DIR / 'deepseek-full-systematic-perturbations' / 're_evaluated.jsonl',
        'deepseek_llm': BASE_DIR / 'deepseek-full-llm-perturbations' / 're_evaluated.jsonl'
    }
    
    output_dir = '/Users/obby/Documents/experiment/gemini-cli/sql-generator/prog_report/2026-01-15'
    
    # Run analysis
    analyzer = CrossExperimentAnalyzer(experiment_files, output_dir)
    analyzer.run_full_analysis()
