import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

# --- Single Boxplot ---

scores = [65.6, 71.9, 90.6, 78.1, 82.8, 82.8, 78.1, 81.3, 82.8, 76.6]

fig, ax = plt.subplots()
box = ax.boxplot(scores, patch_artist=True, showmeans=True, showfliers=False,  meanprops={
        'marker': '^',
        'markerfacecolor': 'black',
        'markeredgecolor': 'black',
        'markersize': 4
    }
    )

# Colour styling
box['boxes'][0].set_facecolor('teal')
box['medians'][0].set_color('black')

# Labeling
ax.set_title('Chatbot Usability Questionnaire Scores (MInf2)', fontsize=14)
ax.set_ylabel('Score', fontsize=14)
ax.set_ylim(0, 100)
ax.set_xticks([])
ax.tick_params(axis='y', labelsize=13)
plt.grid(True, axis='y', linestyle='--', alpha=0.7)
plt.show()

# --- Side-by-side Boxplot ---

# Last year and this year CUQ scores
scores_minf1 = [71.9, 82.8, 53.1, 73.4, 46.9, 71.9, 71.9, 50.0, 25.0, 68.8]
scores_minf2 = [65.6, 71.9, 90.6, 78.1, 82.8, 82.8, 78.1, 81.3, 82.8, 76.6]

# Create side-by-side boxplot
fig, ax = plt.subplots()
box = ax.boxplot([scores_minf1, scores_minf2], patch_artist=True, showmeans=True, showfliers=False,  meanprops={
        'marker': '^',
        'markerfacecolor': 'black',
        'markeredgecolor': 'black',
        'markersize': 4
    }
    )

# Match the colour style to the original plot
colors = ['teal', 'teal']
for patch, color in zip(box['boxes'], colors):
    patch.set_facecolor(color)

for median in box['medians']:
    median.set_color('black')

# Set y-axis to start at 0
ax.set_ylim(0, 100)

# Styling
ax.set_title('Chatbot Usability Questionnaire Scores (MInf1 vs MInf2)', fontsize=14)
ax.set_ylabel('Score', fontsize=14)
ax.set_xticks([1, 2])
ax.set_xticklabels(['MInf1', 'MInf2'], fontsize=14)
ax.tick_params(axis='y', labelsize=13)
plt.grid(True, axis='y', linestyle='--', alpha=0.7)
plt.show()

# --- Statistical Analysis ---

# Perform two-sample t-test
t_stat, p_val = ttest_ind(scores_minf2, scores_minf1)

print(f"T-statistic: {t_stat:.3f}")
print(f"P-value: {p_val:.4f}")