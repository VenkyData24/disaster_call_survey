import pandas as pd
import matplotlib.pyplot as plt
import os

# Load and preprocess
df = pd.read_csv("source_files/final_merged_call_disaster_stats.csv")
df.columns = df.columns.str.lower().str.strip()
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['incident_begin_date'] = pd.to_datetime(df['incident_begin_date'], errors='coerce', utc=True).dt.tz_localize(None)
df['incident_end_date'] = pd.to_datetime(df['incident_end_date'], errors='coerce', utc=True).dt.tz_localize(None)

# Feature engineering
df['age_group'] = pd.cut(df['age'], bins=[17, 30, 45, 60, 75, 100],
                         labels=['18-30', '31-45', '46-60', '61-75', '76+'])
df['post_disaster_outreach'] = df['date'] > df['incident_begin_date']
df['call_month'] = df['date'].dt.to_period('M').astype(str)
df['disaster_month'] = df['incident_begin_date'].dt.to_period('M').astype(str)

# Grouped summaries
def summarize(df, group_col):
    return df.groupby(group_col).agg(
        total_calls=('client_id', 'count'),
        unique_households=('household_id', 'nunique'),
        avg_call_duration=('call_duration', 'mean'),
        post_disaster_ratio=('post_disaster_outreach', 'mean')
    ).reset_index()

ethnicity_summary = summarize(df, 'ethnicity')
party_summary = summarize(df, 'party')
gender_summary = summarize(df, 'gender')

# Monthly trend
monthly_calls = df.groupby('call_month').size().reset_index(name='total_calls')
monthly_disasters = df.groupby('disaster_month').size().reset_index(name='disaster_events')
monthly = pd.merge(monthly_calls.rename(columns={'call_month': 'month'}),
                   monthly_disasters.rename(columns={'disaster_month': 'month'}),
                   on='month', how='outer').fillna(0)
monthly['month'] = pd.to_datetime(monthly['month'])
monthly = monthly.sort_values('month')

# Save plots to dashboard
os.makedirs("dashboard", exist_ok=True)

def save_bar_plot(data, x, y, title, filename):
    plt.figure(figsize=(8, 4))
    plt.bar(data[x], data[y], color='teal', edgecolor='black')
    plt.title(title)
    plt.xlabel(x.capitalize())
    plt.ylabel(y.replace('_', ' ').capitalize())
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"dashboard/{filename}")
    plt.close()

save_bar_plot(ethnicity_summary, 'ethnicity', 'total_calls', 'Total Calls by Ethnicity', 'ethnicity_total_calls.png')
save_bar_plot(party_summary, 'party', 'total_calls', 'Total Calls by Party', 'party_total_calls.png')
save_bar_plot(gender_summary, 'gender', 'total_calls', 'Total Calls by Gender', 'gender_total_calls.png')

# Monthly line chart
plt.figure(figsize=(10, 5))
plt.plot(monthly['month'], monthly['total_calls'], label='Outreach Calls', marker='o')
plt.plot(monthly['month'], monthly['disaster_events'], label='Disaster Events', marker='x')
plt.title('Monthly Trend: Outreach vs Disaster Events')
plt.xlabel('Month')
plt.ylabel('Volume')
plt.legend()
plt.tight_layout()
plt.savefig("dashboard/monthly_trend_calls_vs_disasters.png")
plt.close()
