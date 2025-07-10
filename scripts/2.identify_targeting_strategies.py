# Re-run after environment reset
import pandas as pd
import matplotlib.pyplot as plt
import os

# Load cleaned call data
df = pd.read_csv("source_files/cleaned_call_data_intermediate.csv")
df.columns = df.columns.str.lower().str.strip()

# Group Age Into Brackets
df['age'] = pd.to_numeric(df['age'], errors='coerce')
df['age_group'] = pd.cut(
    df['age'],
    bins=[0, 18, 30, 45, 60, 75, 90, 120],
    labels=['<18', '18–30', '31–45', '46–60', '61–75', '76–90', '90+']
)

# Ensure 'pass__' is numeric
df['pass__'] = pd.to_numeric(df['pass__'], errors='coerce')

# Compute Success Metrics by Demographics
group_metrics = {
    'ethnicity': df.groupby('ethnicity')['pass__'].mean().sort_values(ascending=False),
    'gender': df.groupby('gender')['pass__'].mean().sort_values(ascending=False),
    'party': df.groupby('party')['pass__'].mean().sort_values(ascending=False),
    'county': df.groupby('county')['pass__'].mean().sort_values(ascending=False),
    'age_group': df.groupby('age_group')['pass__'].mean().sort_values(ascending=False)
}

# Create dashboard directory
dashboard_path = "dashboard"
os.makedirs(dashboard_path, exist_ok=True)

# Save CSV summaries
group_metrics['ethnicity'].to_csv(f"{dashboard_path}/ethnicity_pass_rates.csv")
group_metrics['gender'].to_csv(f"{dashboard_path}/gender_pass_rates.csv")
group_metrics['party'].to_csv(f"{dashboard_path}/party_pass_rates.csv")
group_metrics['county'].to_csv(f"{dashboard_path}/county_pass_rates.csv")
group_metrics['age_group'].to_csv(f"{dashboard_path}/agegroup_pass_rates.csv")

# Save plots
for key, data in group_metrics.items():
    plt.figure(figsize=(8, 4))
    data.plot(kind='bar', color='teal', edgecolor='black')
    plt.title(f"Call Success Rate by {key.capitalize()}", fontsize=12)
    plt.ylabel("Success Rate")
    plt.xlabel(key.capitalize())
    #plt.ylim(0, 1.1)
    plt.ylim(data.min() - 0.05, data.max() + 0.05)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"{dashboard_path}/{key}_success_rate_chart.png")
    plt.close()

