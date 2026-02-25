#!/usr/bin/env python3
"""Generate evaluation plots for Hindi Honorifics Cloze Benchmark."""

import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
from pathlib import Path

matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']

RESULTS_DIR = Path(__file__).parent.parent / 'results'
PLOTS_DIR = Path(__file__).parent.parent / 'plots'
PLOTS_DIR.mkdir(exist_ok=True)

def load_metrics(name):
    p = RESULTS_DIR / f'{name}_metrics.json'
    if p.exists():
        return json.loads(p.read_text())
    return None

configs = {
    'Random': 'baseline_random_500',
    'Majority': 'baseline_majority_500',
    'GPT-4.1-nano\n$0.10': 'gpt41_nano_mc_500',
    'GPT-4o\n$2.50': 'gpt4o_mc_500',
    'GPT-4o-mini\n$0.15': 'gpt4o_mini_mc_500',
    'GPT-4.1-mini\n$0.40': 'gpt41_mini_mc_500',
    'GPT-5.2\n$1.75': 'gpt52_mc_500',
    'GPT-5-nano\n$0.05': 'gpt5_nano_mc_500',
    'o4-mini\n$1.10': 'o4_mini_mc_500',
    'GPT-5-mini\n$0.25': 'gpt5_mini_mc_500',
}

data = {k: load_metrics(v) for k, v in configs.items()}
data = {k: v for k, v in data.items() if v}

labels = list(data.keys())
exact_accs = [data[k]['exact_accuracy'] * 100 for k in labels]
tier_accs = [data[k]['tier_accuracy'] * 100 for k in labels]

# Romanized tier keys
TIER_ROMAN = {'तू': 'tu', 'तुम': 'tum', 'आप': 'aap'}
TIER_DISPLAY = {'तू': 'tuu (intimate)', 'तुम': 'tum (familiar)', 'आप': 'aap (formal)'}

# --- Plot 1: Overall accuracy comparison ---
fig, ax = plt.subplots(figsize=(14, 6))
x = np.arange(len(labels))
w = 0.35
bars1 = ax.bar(x - w/2, exact_accs, w, label='Exact Form Accuracy', color='#2196F3', edgecolor='white')
bars2 = ax.bar(x + w/2, tier_accs, w, label='Tier Accuracy (T/TUM/AAP)', color='#FF9800', edgecolor='white')

ax.set_ylabel('Accuracy (%)', fontsize=13)
ax.set_title('Hindi Honorifics Cloze Benchmark — Model Comparison (n=500)', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=25, ha='right', fontsize=9)
ax.legend(fontsize=11)
ax.set_ylim(0, 95)
ax.grid(axis='y', alpha=0.3)

for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=8)
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig(PLOTS_DIR / 'overall_accuracy.png', dpi=150)
print(f"Saved {PLOTS_DIR / 'overall_accuracy.png'}")

# --- Plot 2: Per-tier accuracy for LLM models ---
fig, ax = plt.subplots(figsize=(12, 6))
llm_models = [k for k in labels if 'GPT' in k or 'o4' in k.lower()]
tiers_deva = ['तू', 'तुम', 'आप']
tier_display = ['tuu (intimate)', 'tum (familiar)', 'aap (formal)']
colors = ['#E91E63', '#4CAF50', '#2196F3']

x = np.arange(len(llm_models))
w = 0.25
for i, (tier_d, tier_label) in enumerate(zip(tiers_deva, tier_display)):
    vals = []
    for m in llm_models:
        v = data[m].get(f'tier_accuracy_{tier_d}', 0)
        vals.append(v * 100)
    bars = ax.bar(x + i*w - w, vals, w, label=tier_label, color=colors[i], edgecolor='white')
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=8)

ax.set_ylabel('Tier Accuracy (%)', fontsize=13)
ax.set_title('Per-Tier Accuracy by Model', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(llm_models, rotation=15, ha='right', fontsize=9)
ax.legend(fontsize=11)
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'per_tier_accuracy.png', dpi=150)
print(f"Saved {PLOTS_DIR / 'per_tier_accuracy.png'}")

# --- Plot 3: Confusion matrix for best model (GPT-5-mini) ---
best = data.get('GPT-5-mini\n$0.25', {})
conf = best.get('tier_confusion', {})
tier_labels_conf = ['T', 'TUM', 'AAP']
matrix = np.zeros((3, 3))
for i, g in enumerate(tier_labels_conf):
    for j, p in enumerate(tier_labels_conf):
        matrix[i][j] = conf.get(f'{g}->{p}', 0)

row_sums = matrix.sum(axis=1, keepdims=True)
row_sums[row_sums == 0] = 1
matrix_norm = matrix / row_sums * 100

fig, ax = plt.subplots(figsize=(7, 6))
im = ax.imshow(matrix_norm, cmap='Blues', vmin=0, vmax=100)
ax.set_xticks(range(3))
ax.set_yticks(range(3))
display_labels = ['tuu (T)', 'tum (TUM)', 'aap (AAP)']
ax.set_xticklabels(display_labels, fontsize=11)
ax.set_yticklabels(display_labels, fontsize=11)
ax.set_xlabel('Predicted Tier', fontsize=13)
ax.set_ylabel('Gold Tier', fontsize=13)
ax.set_title('Tier Confusion Matrix — GPT-5-mini\n(row-normalized %)', fontsize=13, fontweight='bold')

for i in range(3):
    for j in range(3):
        color = 'white' if matrix_norm[i][j] > 50 else 'black'
        ax.text(j, i, f'{matrix_norm[i][j]:.1f}%\n({int(matrix[i][j])})', ha='center', va='center', fontsize=11, color=color)

plt.colorbar(im, ax=ax, label='%')
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'confusion_matrix_gpt5_mini.png', dpi=150)
print(f"Saved {PLOTS_DIR / 'confusion_matrix_gpt5_mini.png'}")

# --- Plot 4: Valid form rate ---
fig, ax = plt.subplots(figsize=(12, 5))
valid_rates = [data[k].get('valid_form_rate', 0) * 100 for k in labels]
colors_bar = []
for k in labels:
    if 'GPT' not in k and 'o4' not in k:
        colors_bar.append('#9E9E9E')
    elif any(r in k for r in ['5-nano', '5-mini', 'o4']):
        colors_bar.append('#4CAF50')
    else:
        colors_bar.append('#2196F3')

bars = ax.bar(labels, valid_rates, color=colors_bar, edgecolor='white')
ax.set_ylabel('Valid Form Rate (%)', fontsize=13)
ax.set_title('Rate of Valid Hindi Pronoun Forms in Model Output\n(green = reasoning models, blue = standard, gray = baselines)', fontsize=13, fontweight='bold')
ax.set_ylim(0, 110)
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=25, ha='right', fontsize=9)
ax.grid(axis='y', alpha=0.3)
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{bar.get_height():.1f}%', ha='center', va='bottom', fontsize=8)
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'valid_form_rate.png', dpi=150)
print(f"Saved {PLOTS_DIR / 'valid_form_rate.png'}")

# --- Plot 5: Cost vs Accuracy scatter ---
cost_data = {
    'GPT-4.1-nano': (0.10, 'gpt41_nano_mc_500'),
    'GPT-4o': (2.50, 'gpt4o_mc_500'),
    'GPT-4o-mini': (0.15, 'gpt4o_mini_mc_500'),
    'GPT-4.1-mini': (0.40, 'gpt41_mini_mc_500'),
    'GPT-5.2': (1.75, 'gpt52_mc_500'),
    'GPT-5-nano': (0.05, 'gpt5_nano_mc_500'),
    'o4-mini': (1.10, 'o4_mini_mc_500'),
    'GPT-5-mini': (0.25, 'gpt5_mini_mc_500'),
}

fig, ax = plt.subplots(figsize=(12, 7))
for name, (cost, key) in cost_data.items():
    m = load_metrics(key)
    if m and m['tier_accuracy'] > 0:
        # Color: green for reasoning, pink for standard small, blue for standard large
        if any(k in name for k in ['o4', '5-nano', '5-mini']):
            color = '#4CAF50'  # reasoning
            marker = 's'
        else:
            color = '#2196F3'  # standard
            marker = 'o'
        ax.scatter(cost, m['tier_accuracy'] * 100, s=200, color=color, marker=marker,
                  edgecolors='white', linewidths=2, zorder=5)
        ax.annotate(name, (cost, m['tier_accuracy'] * 100), textcoords="offset points",
                   xytext=(10, 5), fontsize=10, fontweight='bold')

# Add legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='s', color='w', markerfacecolor='#4CAF50', markersize=12, label='Reasoning models'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#2196F3', markersize=12, label='Standard models'),
]
ax.legend(handles=legend_elements, fontsize=11, loc='lower right')

ax.set_xlabel('Input Cost ($/1M tokens)', fontsize=13)
ax.set_ylabel('Tier Accuracy (%)', fontsize=13)
ax.set_title('Cost vs Accuracy — Hindi Honorifics Benchmark', fontsize=14, fontweight='bold')
ax.set_xscale('log')
ax.grid(True, alpha=0.3)
ax.set_ylim(30, 90)
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'cost_vs_accuracy.png', dpi=150)
print(f"Saved {PLOTS_DIR / 'cost_vs_accuracy.png'}")

print("\nAll plots saved to", PLOTS_DIR)
