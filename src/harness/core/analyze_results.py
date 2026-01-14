#!/usr/bin/env python3
"""
Comprehensive Results Analysis Script for SQL Generation Experiments

Analyzes JSONL log files from experiment runs and generates:
- Statistical summaries
- Per-model performance comparisons
- Perturbation robustness analysis
- Query complexity analysis
- Failure mode analysis
- Academic-quality visualizations and tables

Usage:
    python analyze_results.py <input_jsonl> <output_dir>
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict, Counter
from datetime import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle

# Set style for academic papers
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'


class ExperimentAnalyzer:
    """Comprehensive analyzer for experiment results."""
    
    def __init__(self, jsonl_path: str, output_dir: str):
        """
        Initialize analyzer.
        
        Args:
            jsonl_path: Path to JSONL results file
            output_dir: Directory to save analysis outputs
        """
        self.jsonl_path = jsonl_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.figures_dir = self.output_dir / "figures"
        self.tables_dir = self.output_dir / "tables"
        self.figures_dir.mkdir(exist_ok=True)
        self.tables_dir.mkdir(exist_ok=True)
        
        self.records = []
        self.df = None
        
    def load_data(self):
        """Load and parse JSONL file into pandas DataFrame."""
        print(f"Loading data from {self.jsonl_path}...")
        
        with open(self.jsonl_path, 'r') as f:
            for line in f:
                if line.strip():
                    self.records.append(json.loads(line))
        
        # Convert to DataFrame
        self.df = pd.DataFrame(self.records)
        
        # Extract nested fields
        self.df['correctness'] = self.df['evaluation_result'].apply(lambda x: x['correctness'])
        self.df['similarity_score'] = self.df['evaluation_result'].apply(lambda x: x['similarity_score'])
        self.df['failure_type'] = self.df['evaluation_result'].apply(lambda x: x['failure_type'])
        
        # Add derived fields
        self.df['is_perturbed'] = self.df['perturbation_type'] != 'original'
        
        print(f"✓ Loaded {len(self.df)} records")
        print(f"  - Models: {self.df['model_name'].nunique()}")
        print(f"  - Perturbation types: {self.df['perturbation_type'].nunique()}")
        print(f"  - Complexity levels: {self.df['query_complexity'].nunique()}")
        
    def generate_summary_statistics(self):
        """Generate overall summary statistics."""
        print("\n" + "="*60)
        print("SUMMARY STATISTICS")
        print("="*60)
        
        summary = {
            'Total Records': len(self.df),
            'Total Queries': self.df['prompt_id'].apply(lambda x: x.split('_')[0]).nunique(),
            'Models Tested': self.df['model_name'].nunique(),
            'Unique Model Names': ', '.join(self.df['model_name'].unique()),
            'Overall Accuracy': f"{self.df['correctness'].mean()*100:.2f}%",
            'Mean Similarity Score': f"{self.df['similarity_score'].mean():.4f}",
            'Total Failures': (~self.df['correctness']).sum(),
            'Failure Rate': f"{(~self.df['correctness']).mean()*100:.2f}%",
        }
        
        # Save to file
        summary_file = self.tables_dir / "summary_statistics.txt"
        with open(summary_file, 'w') as f:
            for key, value in summary.items():
                f.write(f"{key:25s}: {value}\n")
                print(f"{key:25s}: {value}")
        
        print(f"\n✓ Summary saved to {summary_file}")
        
    def analyze_per_model_performance(self):
        """Analyze and visualize per-model performance."""
        print("\n" + "="*60)
        print("PER-MODEL PERFORMANCE ANALYSIS")
        print("="*60)
        
        # Calculate metrics per model
        model_stats = self.df.groupby('model_name').agg({
            'correctness': ['count', 'sum', 'mean'],
            'similarity_score': ['mean', 'std'],
            'failure_type': lambda x: (x != 'none').sum()
        }).round(4)
        
        model_stats.columns = ['Total Tests', 'Correct', 'Accuracy', 'Avg Similarity', 'Std Similarity', 'Total Failures']
        model_stats['Accuracy'] = (model_stats['Accuracy'] * 100).round(2)
        
        # Save table
        table_file = self.tables_dir / "model_performance.csv"
        model_stats.to_csv(table_file)
        print(f"\n✓ Model performance table saved to {table_file}")
        print("\nModel Performance:")
        print(model_stats.to_string())
        
        # Visualizations
        self._plot_model_accuracy_comparison()
        self._plot_model_similarity_comparison()
        
    def _plot_model_accuracy_comparison(self):
        """Bar chart comparing model accuracy."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        model_acc = self.df.groupby('model_name')['correctness'].mean() * 100
        model_acc = model_acc.sort_values(ascending=False)
        
        bars = ax.bar(range(len(model_acc)), model_acc.values, color=sns.color_palette("viridis", len(model_acc)))
        ax.set_xticks(range(len(model_acc)))
        ax.set_xticklabels(model_acc.index, rotation=45, ha='right')
        ax.set_ylabel('Accuracy (%)')
        ax.set_title('Model Accuracy Comparison')
        ax.set_ylim(0, 100)
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for i, (bar, val) in enumerate(zip(bars, model_acc.values)):
            ax.text(bar.get_x() + bar.get_width()/2, val + 1, f'{val:.1f}%', 
                   ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        fig_file = self.figures_dir / "model_accuracy_comparison.png"
        plt.savefig(fig_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Figure saved: {fig_file}")
        
    def _plot_model_similarity_comparison(self):
        """Box plot comparing similarity scores across models."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        models = self.df['model_name'].unique()
        data = [self.df[self.df['model_name'] == model]['similarity_score'].values for model in models]
        
        bp = ax.boxplot(data, labels=models, patch_artist=True, showmeans=True)
        
        # Color the boxes
        for patch, color in zip(bp['boxes'], sns.color_palette("Set2", len(models))):
            patch.set_facecolor(color)
        
        ax.set_ylabel('Similarity Score (TED)')
        ax.set_title('SQL Similarity Score Distribution by Model')
        ax.set_xticklabels(models, rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        fig_file = self.figures_dir / "model_similarity_boxplot.png"
        plt.savefig(fig_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Figure saved: {fig_file}")
    
    def analyze_perturbation_robustness(self):
        """Analyze model robustness to different perturbation types."""
        print("\n" + "="*60)
        print("PERTURBATION ROBUSTNESS ANALYSIS")
        print("="*60)
        
        # Calculate accuracy per perturbation type
        pert_stats = self.df.groupby('perturbation_type').agg({
            'correctness': ['count', 'sum', 'mean'],
            'similarity_score': 'mean'
        }).round(4)
        
        pert_stats.columns = ['Total', 'Correct', 'Accuracy', 'Avg Similarity']
        pert_stats['Accuracy'] = (pert_stats['Accuracy'] * 100).round(2)
        pert_stats = pert_stats.sort_values('Accuracy', ascending=False)
        
        # Save table
        table_file = self.tables_dir / "perturbation_performance.csv"
        pert_stats.to_csv(table_file)
        print(f"\n✓ Perturbation analysis saved to {table_file}")
        print("\nPerturbation Performance:")
        print(pert_stats.to_string())
        
        # Visualizations
        self._plot_perturbation_accuracy()
        self._plot_perturbation_heatmap()
        
    def _plot_perturbation_accuracy(self):
        """Bar chart of accuracy per perturbation type."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        pert_acc = self.df.groupby('perturbation_type')['correctness'].mean() * 100
        pert_acc = pert_acc.sort_values(ascending=True)
        
        # Color: green for original, gradient for perturbations
        colors = ['green' if idx == 'original' else 'coral' for idx in pert_acc.index]
        
        bars = ax.barh(range(len(pert_acc)), pert_acc.values, color=colors)
        ax.set_yticks(range(len(pert_acc)))
        ax.set_yticklabels(pert_acc.index)
        ax.set_xlabel('Accuracy (%)')
        ax.set_title('Accuracy by Perturbation Type')
        ax.set_xlim(0, 100)
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, pert_acc.values)):
            ax.text(val + 1, bar.get_y() + bar.get_height()/2, f'{val:.1f}%', 
                   va='center', fontsize=8)
        
        plt.tight_layout()
        fig_file = self.figures_dir / "perturbation_accuracy.png"
        plt.savefig(fig_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Figure saved: {fig_file}")
    
    def _plot_perturbation_heatmap(self):
        """Heatmap of model vs perturbation type performance."""
        # Create pivot table
        pivot = self.df.pivot_table(
            values='correctness',
            index='perturbation_type',
            columns='model_name',
            aggfunc='mean'
        ) * 100
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlGn', vmin=0, vmax=100,
                   cbar_kws={'label': 'Accuracy (%)'}, ax=ax)
        ax.set_title('Model Performance Heatmap: Perturbation Type vs Model')
        ax.set_xlabel('Model')
        ax.set_ylabel('Perturbation Type')
        
        plt.tight_layout()
        fig_file = self.figures_dir / "model_perturbation_heatmap.png"
        plt.savefig(fig_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Figure saved: {fig_file}")
    
    def analyze_complexity_performance(self):
        """Analyze performance across query complexity levels."""
        print("\n" + "="*60)
        print("QUERY COMPLEXITY ANALYSIS")
        print("="*60)
        
        # Calculate metrics per complexity level
        complexity_stats = self.df.groupby('query_complexity').agg({
            'correctness': ['count', 'sum', 'mean'],
            'similarity_score': 'mean'
        }).round(4)
        
        complexity_stats.columns = ['Total', 'Correct', 'Accuracy', 'Avg Similarity']
        complexity_stats['Accuracy'] = (complexity_stats['Accuracy'] * 100).round(2)
        
        # Order by complexity (if possible)
        complexity_order = ['simple', 'moderate', 'complex', 'advanced', 'join', 'aggregation', 'subquery']
        existing_levels = [c for c in complexity_order if c in complexity_stats.index]
        complexity_stats = complexity_stats.reindex(existing_levels)
        
        # Save table
        table_file = self.tables_dir / "complexity_performance.csv"
        complexity_stats.to_csv(table_file)
        print(f"\n✓ Complexity analysis saved to {table_file}")
        print("\nComplexity Performance:")
        print(complexity_stats.to_string())
        
        # Visualization
        self._plot_complexity_accuracy()
    
    def _plot_complexity_accuracy(self):
        """Line plot showing accuracy degradation with complexity."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Order complexities logically
        complexity_order = ['simple', 'moderate', 'complex', 'advanced', 'join', 'aggregation', 'subquery']
        complexity_data = self.df.groupby('query_complexity')['correctness'].mean() * 100
        
        existing_levels = [c for c in complexity_order if c in complexity_data.index]
        ordered_data = [complexity_data[c] for c in existing_levels]
        
        ax.plot(existing_levels, ordered_data, marker='o', linewidth=2, markersize=8)
        ax.set_xlabel('Query Complexity')
        ax.set_ylabel('Accuracy (%)')
        ax.set_title('Accuracy vs Query Complexity')
        ax.set_ylim(0, 100)
        ax.grid(alpha=0.3)
        ax.set_xticklabels(existing_levels, rotation=45, ha='right')
        
        # Add value labels
        for x, y in zip(existing_levels, ordered_data):
            ax.text(x, y + 2, f'{y:.1f}%', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        fig_file = self.figures_dir / "complexity_accuracy_trend.png"
        plt.savefig(fig_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Figure saved: {fig_file}")
    
    def analyze_failure_modes(self):
        """Detailed analysis of failure types."""
        print("\n" + "="*60)
        print("FAILURE MODE ANALYSIS")
        print("="*60)
        
        # Count failures by type
        failure_counts = self.df[self.df['failure_type'] != 'none']['failure_type'].value_counts()
        
        print("\nFailure Type Distribution:")
        for ftype, count in failure_counts.items():
            pct = count / len(self.df) * 100
            print(f"  {ftype:20s}: {count:5d} ({pct:5.2f}%)")
        
        # Save table
        failure_df = pd.DataFrame({
            'Failure Type': failure_counts.index,
            'Count': failure_counts.values,
            'Percentage': (failure_counts.values / len(self.df) * 100).round(2)
        })
        table_file = self.tables_dir / "failure_modes.csv"
        failure_df.to_csv(table_file, index=False)
        print(f"\n✓ Failure analysis saved to {table_file}")
        
        # Visualization
        self._plot_failure_distribution()
        
    def _plot_failure_distribution(self):
        """Pie chart of failure type distribution."""
        fig, ax = plt.subplots(figsize=(8, 8))
        
        failure_counts = self.df['failure_type'].value_counts()
        
        colors = sns.color_palette("Set3", len(failure_counts))
        explode = [0.1 if ft != 'none' else 0 for ft in failure_counts.index]
        
        wedges, texts, autotexts = ax.pie(
            failure_counts.values,
            labels=failure_counts.index,
            autopct='%1.1f%%',
            colors=colors,
            explode=explode,
            startangle=90
        )
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_weight('bold')
        
        ax.set_title('Distribution of Result Types')
        
        plt.tight_layout()
        fig_file = self.figures_dir / "failure_distribution.png"
        plt.savefig(fig_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Figure saved: {fig_file}")
    
    def generate_academic_tables(self):
        """Generate LaTeX-formatted tables for academic papers."""
        print("\n" + "="*60)
        print("GENERATING ACADEMIC TABLES")
        print("="*60)
        
        # Table 1: Overall Model Performance
        model_table = self.df.groupby('model_name').agg({
            'correctness': ['count', lambda x: (x.sum()/len(x)*100)],
            'similarity_score': ['mean', 'std']
        }).round(2)
        model_table.columns = ['N', 'Acc (%)', 'TED μ', 'TED σ']
        
        latex_file = self.tables_dir / "table1_model_performance.tex"
        with open(latex_file, 'w') as f:
            f.write(model_table.to_latex(caption="Model Performance Summary", label="tab:model_perf"))
        print(f"✓ LaTeX table saved: {latex_file}")
        
        # Table 2: Perturbation Robustness
        pert_table = self.df.groupby('perturbation_type').agg({
            'correctness': ['count', lambda x: (x.sum()/len(x)*100)],
            'similarity_score': 'mean'
        }).round(2)
        pert_table.columns = ['N', 'Acc (%)', 'TED μ']
        pert_table = pert_table.sort_values('Acc (%)', ascending=False)
        
        latex_file = self.tables_dir / "table2_perturbation_robustness.tex"
        with open(latex_file, 'w') as f:
            f.write(pert_table.to_latex(caption="Perturbation Robustness Analysis", label="tab:pert_robust"))
        print(f"✓ LaTeX table saved: {latex_file}")
        
        # Table 3: Complexity Analysis
        complexity_table = self.df.groupby('query_complexity').agg({
            'correctness': ['count', lambda x: (x.sum()/len(x)*100)],
            'similarity_score': 'mean'
        }).round(2)
        complexity_table.columns = ['N', 'Acc (%)', 'TED μ']
        
        latex_file = self.tables_dir / "table3_complexity_analysis.tex"
        with open(latex_file, 'w') as f:
            f.write(complexity_table.to_latex(caption="Query Complexity Analysis", label="tab:complexity"))
        print(f"✓ LaTeX table saved: {latex_file}")
    
    def generate_correlation_analysis(self):
        """Analyze correlations between different metrics."""
        print("\n" + "="*60)
        print("CORRELATION ANALYSIS")
        print("="*60)
        
        # Create correlation matrix
        numeric_cols = ['correctness', 'similarity_score', 'perturbation_id']
        corr_matrix = self.df[numeric_cols].corr()
        
        print("\nCorrelation Matrix:")
        print(corr_matrix.to_string())
        
        # Save
        table_file = self.tables_dir / "correlation_matrix.csv"
        corr_matrix.to_csv(table_file)
        
        # Visualize
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, linewidths=1, ax=ax)
        ax.set_title('Metric Correlation Matrix')
        
        plt.tight_layout()
        fig_file = self.figures_dir / "correlation_heatmap.png"
        plt.savefig(fig_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Correlation heatmap saved: {fig_file}")
    
    def generate_executive_summary(self):
        """Generate a comprehensive executive summary report."""
        print("\n" + "="*60)
        print("GENERATING EXECUTIVE SUMMARY")
        print("="*60)
        
        summary_file = self.output_dir / "EXECUTIVE_SUMMARY.md"
        
        with open(summary_file, 'w') as f:
            f.write("# Experiment Results - Executive Summary\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Data Source**: {self.jsonl_path}\n\n")
            
            f.write("---\n\n")
            f.write("## 📊 Overall Statistics\n\n")
            f.write(f"- **Total Test Cases**: {len(self.df):,}\n")
            f.write(f"- **Models Tested**: {self.df['model_name'].nunique()}\n")
            f.write(f"- **Overall Accuracy**: {self.df['correctness'].mean()*100:.2f}%\n")
            f.write(f"- **Average Similarity Score**: {self.df['similarity_score'].mean():.4f}\n\n")
            
            f.write("## 🤖 Model Performance\n\n")
            model_perf = self.df.groupby('model_name').agg({
                'correctness': lambda x: f"{x.mean()*100:.2f}%",
                'similarity_score': lambda x: f"{x.mean():.4f}"
            })
            model_perf.columns = ['Accuracy', 'Avg TED Score']
            f.write(model_perf.to_markdown())
            f.write("\n\n")
            
            f.write("## 🔄 Perturbation Robustness\n\n")
            pert_perf = self.df.groupby('perturbation_type')['correctness'].mean() * 100
            pert_perf = pert_perf.sort_values(ascending=False).head(10)
            f.write("Top 10 Perturbation Types by Accuracy:\n\n")
            for pert, acc in pert_perf.items():
                f.write(f"- **{pert}**: {acc:.2f}%\n")
            f.write("\n")
            
            f.write("## 📈 Query Complexity Impact\n\n")
            complexity_perf = self.df.groupby('query_complexity')['correctness'].mean() * 100
            for comp, acc in complexity_perf.items():
                f.write(f"- **{comp}**: {acc:.2f}%\n")
            f.write("\n")
            
            f.write("## ⚠️ Failure Analysis\n\n")
            failures = self.df[self.df['failure_type'] != 'none']['failure_type'].value_counts()
            for ftype, count in failures.items():
                pct = count / len(self.df) * 100
                f.write(f"- **{ftype}**: {count} ({pct:.2f}%)\n")
            f.write("\n")
            
            f.write("## 📁 Generated Outputs\n\n")
            f.write("### Figures\n\n")
            for fig in sorted(self.figures_dir.glob("*.png")):
                f.write(f"- `{fig.name}`\n")
            f.write("\n### Tables\n\n")
            for table in sorted(self.tables_dir.glob("*")):
                f.write(f"- `{table.name}`\n")
        
        print(f"✓ Executive summary saved: {summary_file}")
    
    def run_full_analysis(self):
        """Run all analysis steps."""
        print("\n" + "="*60)
        print("STARTING COMPREHENSIVE ANALYSIS")
        print("="*60)
        
        self.load_data()
        self.generate_summary_statistics()
        self.analyze_per_model_performance()
        self.analyze_perturbation_robustness()
        self.analyze_complexity_performance()
        self.analyze_failure_modes()
        self.generate_correlation_analysis()
        self.generate_academic_tables()
        self.generate_executive_summary()
        
        print("\n" + "="*60)
        print("✅ ANALYSIS COMPLETE!")
        print("="*60)
        print(f"\nAll outputs saved to: {self.output_dir}")
        print(f"  - Figures: {self.figures_dir}")
        print(f"  - Tables: {self.tables_dir}")
        print(f"  - Summary: {self.output_dir / 'EXECUTIVE_SUMMARY.md'}")


def main():
    """Main entry point."""
    if len(sys.argv) != 3:
        print("Usage: python analyze_results.py <input_jsonl> <output_dir>")
        print("\nExample:")
        print("  python analyze_results.py results/experiment_run1.jsonl analysis_output/")
        sys.exit(1)
    
    jsonl_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    if not os.path.exists(jsonl_path):
        print(f"Error: Input file not found: {jsonl_path}")
        sys.exit(1)
    
    analyzer = ExperimentAnalyzer(jsonl_path, output_dir)
    analyzer.run_full_analysis()


if __name__ == "__main__":
    main()
