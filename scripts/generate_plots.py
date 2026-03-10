#!/usr/bin/env python3
"""Generate visualization plots for the Hindi Honorifics Benchmark."""

import matplotlib.pyplot as plt
import numpy as np

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

RESULTS = {
    'gpt-5-mini': {'cloze': 81.4, 'gen': 40.0, 'refusal': 47.5, 'family': 'OpenAI'},
    'o4-mini': {'cloze': 79.9, 'gen': 49.0, 'refusal': 0.0, 'family': 'OpenAI'},
    'gpt-5-nano': {'cloze': 72.7, 'gen': 52.4, 'refusal': 0.0, 'family': 'OpenAI'},
    'gpt-5.2': {'cloze': 68.9, 'gen': 44.7, 'refusal': 2.0, 'family': 'OpenAI'},
    'gpt-4.1-mini': {'cloze': 75.9, 'gen': 55.5, 'refusal': 0.0, 'family': 'OpenAI'},
    'gpt-4o-mini': {'cloze': 78.8, 'gen': 57.5, 'refusal': 0.0, 'family': 'OpenAI'},
    'gpt-4o': {'cloze': 80.5, 'gen': 56.5, 'refusal': 0.0, 'family': 'OpenAI'},
    'Claude Sonnet': {'cloze': 75.8, 'gen': 41.2, 'refusal': 17.5, 'family': 'Anthropic'},
    'Gemini Flash': {'cloze': 55.0, 'gen': 39.0, 'refusal': 0.0, 'family': 'Google'},
    'Sarvam-M': {'cloze': 52.7, 'gen': 27.6, 'refusal': 0.0, 'family': 'Sarvam'},
}

TIER_DATA = {
    'gpt-5-mini': {'T': 25, 'TUM': 48, 'AAP': 52},
    'gpt-4o-mini': {'T': 42, 'TUM': 65, 'AAP': 66},
    'Claude Sonnet': {'T': 28, 'TUM': 49, 'AAP': 51},
    'Gemini Flash': {'T': 22, 'TUM': 45, 'AAP': 52},
}

def plot_cloze_vs_gen():
    fig, ax = plt.subplots(figsize=(10, 6))
    
    models = list(RESULTS.keys())
    cloze = [RESULTS[m]['cloze'] for m in models]
    gen = [RESULTS[m]['gen'] for m in models]
    
    x = np.arange(len(models))
    width = 0.35
    
    colors = {'OpenAI': '#74aa9c', 'Anthropic': '#d97757', 'Google': '#4285f4', 'Sarvam': '#ff9800'}
    bar_colors = [colors[RESULTS[m]['family']] for m in models]
    
    bars1 = ax.bar(x - width/2, cloze, width, label='Cloze (Comprehension)', color=bar_colors, alpha=0.9)
    bars2 = ax.bar(x + width/2, gen, width, label='Generation (Production)', color=bar_colors, alpha=0.5, hatch='//')
    
    ax.set_ylabel('Tier Accuracy (%)')
    ax.set_title('Comprehension vs Production: The Honorifics Gap', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=45, ha='right')
    ax.legend(loc='upper right')
    ax.set_ylim(0, 100)
    
    for bar, val in zip(bars1, cloze):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{val:.0f}', 
                ha='center', va='bottom', fontsize=8)
    for bar, val in zip(bars2, gen):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{val:.0f}', 
                ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('plots/cloze_vs_gen.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved cloze_vs_gen.png")

def plot_family_comparison():
    fig, ax = plt.subplots(figsize=(8, 5))
    
    families = ['OpenAI', 'Anthropic', 'Google', 'Sarvam']
    best_cloze = [81.4, 75.8, 55.0, 52.7]
    best_gen = [57.5, 41.2, 39.0, 27.6]
    
    x = np.arange(len(families))
    width = 0.35
    
    colors = ['#74aa9c', '#d97757', '#4285f4', '#ff9800']
    
    bars1 = ax.bar(x - width/2, best_cloze, width, label='Best Cloze', color=colors, edgecolor='black')
    bars2 = ax.bar(x + width/2, best_gen, width, label='Best Generation', color=colors, alpha=0.5, edgecolor='black', hatch='//')
    
    ax.set_ylabel('Tier Accuracy (%)')
    ax.set_title('Model Family Comparison', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(families)
    ax.legend()
    ax.set_ylim(0, 100)
    
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 1, f'{height:.0f}%',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('plots/family_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved family_comparison.png")

def plot_tier_breakdown():
    fig, ax = plt.subplots(figsize=(9, 5))
    
    models = list(TIER_DATA.keys())
    
    x = np.arange(len(models))
    width = 0.25
    
    t_vals = [TIER_DATA[m]['T'] for m in models]
    tum_vals = [TIER_DATA[m]['TUM'] for m in models]
    aap_vals = [TIER_DATA[m]['AAP'] for m in models]
    
    bars1 = ax.bar(x - width, t_vals, width, label='T (Intimate)', color='#e74c3c')
    bars2 = ax.bar(x, tum_vals, width, label='TUM (Familiar)', color='#f39c12')
    bars3 = ax.bar(x + width, aap_vals, width, label='AAP (Formal)', color='#27ae60')
    
    ax.set_ylabel('Generation Accuracy (%)')
    ax.set_title('Per-Tier Accuracy: Intimate Register is Hardest', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend()
    ax.set_ylim(0, 80)
    
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 1, f'{height:.0f}',
                    ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('plots/tier_breakdown.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved tier_breakdown.png")

def plot_refusal_rates():
    fig, ax = plt.subplots(figsize=(7, 4))
    
    models_with_refusals = ['gpt-5-mini', 'Claude Sonnet', 'gpt-5.2']
    refusals = [47.5, 17.5, 2.0]
    
    colors = ['#74aa9c', '#d97757', '#74aa9c']
    bars = ax.barh(models_with_refusals, refusals, color=colors, edgecolor='black')
    
    ax.set_xlabel('Refusal Rate (%)')
    ax.set_title('Model Refusal Rates on Hindi Film Dialogue', fontweight='bold')
    ax.set_xlim(0, 60)
    
    for bar, val in zip(bars, refusals):
        ax.text(val + 1, bar.get_y() + bar.get_height()/2, f'{val}%',
                ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('plots/refusal_rates.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved refusal_rates.png")

if __name__ == '__main__':
    import os
    os.chdir('/Users/adit/.cursor/worktrees/hindi-honorifics-benchmark/deq')
    
    plot_cloze_vs_gen()
    plot_family_comparison()
    plot_tier_breakdown()
    plot_refusal_rates()
    
    print("\nAll plots generated successfully!")
