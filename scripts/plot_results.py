#!/usr/bin/env python3
"""Generate evaluation plots for Hindi Honorifics Cloze Benchmark."""

import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from matplotlib.font_manager import FontProperties
import numpy as np
from pathlib import Path

# Devanagari-capable font
DEVA_FONT = FontProperties(fname=str(Path.home() / '.fonts' / 'NotoSansDevanagari.ttf'))
# Use it as default fallback
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Noto Sans Devanagari', 'DejaVu Sans']

RESULTS_DIR = Path(__file__).parent.parent / 'results'
PLOTS_DIR = Path(__file__).parent.parent / 'plots'
PLOTS_DIR.mkdir(exist_ok=True)

# Load all 500-probe metrics
def load_metrics(name):
    p = RESULTS_DIR / f'{name}_metrics.json'
    if p.exists():
        return json.loads(p.read_text())
    return None

configs = {
    'Random': 'baseline_random_500',
    'Majority (तुम)': 'baseline_majority_500',
    'Tier-Majority (आप)': 'baseline_tier_majority_500',
    'GPT-4o-mini': 'gpt4o_mini_mc_500',
    'GPT-4o': 'gpt4o_mc_500',
    'GPT-4.1-mini': 'gpt41_mini_mc_500',
    'GPT-5.2': 'gpt52_mc_500',
}

data = {k: load_metrics(v) for k, v in configs.items()}
data = {k: v for k, v in data.items() if v}

labels = list(data.keys())
exact_accs = [data[k]['exact_accuracy'] * 100 for k in labels]
tier_accs = [data[k]['tier_accuracy'] * 100 for k in labels]

# --- Plot 1: Overall accuracy comparison ---
fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(labels))
w = 0.35
bars1 = ax.bar(x - w/2, exact_accs, w, label='Exact Form Accuracy', color='#2196F3', edgecolor='white')
bars2 = ax.bar(x + w/2, tier_accs, w, label='Tier Accuracy (T/TUM/AAP)', color='#FF9800', edgecolor='white')

ax.set_ylabel('Accuracy (%)', fontsize=13)
ax.set_title('Hindi Honorifics Cloze Benchmark — Model Comparison (n=500)', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=25, ha='right', fontsize=10)
ax.legend(fontsize=11)
ax.set_ylim(0, 80)
ax.grid(axis='y', alpha=0.3)

for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=9)
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig(PLOTS_DIR / 'overall_accuracy.png', dpi=150)
print(f"Saved {PLOTS_DIR / 'overall_accuracy.png'}")

# --- Plot 2: Per-tier accuracy for LLM models ---
fig, ax = plt.subplots(figsize=(10, 6))
llm_models = [k for k in labels if 'GPT' in k or 'gpt' in k.lower()]
tiers = ['तू', 'तुम', 'आप']
tier_keys = ['तू', 'तुम', 'आप']
colors = ['#E91E63', '#4CAF50', '#2196F3']

x = np.arange(len(llm_models))
w = 0.25
for i, tier in enumerate(tiers):
    vals = []
    for m in llm_models:
        v = data[m].get(f'tier_accuracy_{tier}', 0)
        vals.append(v * 100)
    bars = ax.bar(x + i*w - w, vals, w, label=f'{tier} tier', color=colors[i], edgecolor='white')
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=9)

ax.set_ylabel('Tier Accuracy (%)', fontsize=13)
ax.set_title('Per-Tier Accuracy by Model', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(llm_models, rotation=15, ha='right', fontsize=10)
ax.legend(fontsize=11)
ax.set_ylim(0, 85)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'per_tier_accuracy.png', dpi=150)
print(f"Saved {PLOTS_DIR / 'per_tier_accuracy.png'}")

# --- Plot 3: Confusion matrix for best model (GPT-5.2) ---
best = data.get('GPT-5.2', {})
conf = best.get('tier_confusion', {})
tier_labels = ['T', 'TUM', 'AAP']
matrix = np.zeros((3, 3))
for i, g in enumerate(tier_labels):
    for j, p in enumerate(tier_labels):
        matrix[i][j] = conf.get(f'{g}->{p}', 0)

# Normalize by row
row_sums = matrix.sum(axis=1, keepdims=True)
row_sums[row_sums == 0] = 1
matrix_norm = matrix / row_sums * 100

fig, ax = plt.subplots(figsize=(7, 6))
im = ax.imshow(matrix_norm, cmap='Blues', vmin=0, vmax=100)
ax.set_xticks(range(3))
ax.set_yticks(range(3))
display_labels = ['तू (T)', 'तुम (TUM)', 'आप (AAP)']
ax.set_xticklabels(display_labels, fontsize=11)
ax.set_yticklabels(display_labels, fontsize=11)
ax.set_xlabel('Predicted Tier', fontsize=13)
ax.set_ylabel('Gold Tier', fontsize=13)
ax.set_title('Tier Confusion Matrix — GPT-5.2 (Hindi)\n(row-normalized %)', fontsize=13, fontweight='bold')

for i in range(3):
    for j in range(3):
        color = 'white' if matrix_norm[i][j] > 50 else 'black'
        ax.text(j, i, f'{matrix_norm[i][j]:.1f}%\n({int(matrix[i][j])})', ha='center', va='center', fontsize=11, color=color)

plt.colorbar(im, ax=ax, label='%')
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'confusion_matrix_gpt52.png', dpi=150)
print(f"Saved {PLOTS_DIR / 'confusion_matrix_gpt52.png'}")

# --- Plot 4: Valid form rate ---
fig, ax = plt.subplots(figsize=(10, 5))
valid_rates = [data[k].get('valid_form_rate', 0) * 100 for k in labels]
colors_bar = ['#9E9E9E' if 'baseline' in configs.get(k, '').lower() or 'Random' in k or 'Majority' in k else '#2196F3' for k in labels]
colors_bar = []
for k in labels:
    if 'GPT' not in k:
        colors_bar.append('#9E9E9E')
    else:
        colors_bar.append('#2196F3')

bars = ax.bar(labels, valid_rates, color=colors_bar, edgecolor='white')
ax.set_ylabel('Valid Form Rate (%)', fontsize=13)
ax.set_title('Rate of Valid Hindi Pronoun Forms in Model Output', fontsize=14, fontweight='bold')
ax.set_ylim(0, 110)
ax.set_xticklabels(labels, rotation=25, ha='right', fontsize=10)
ax.grid(axis='y', alpha=0.3)
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{bar.get_height():.1f}%', ha='center', va='bottom', fontsize=9)
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'valid_form_rate.png', dpi=150)
print(f"Saved {PLOTS_DIR / 'valid_form_rate.png'}")

print("\nAll plots saved to", PLOTS_DIR)
