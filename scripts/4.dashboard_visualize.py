import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------
# Streamlit Dashboard Setup
# -------------------------------
st.set_page_config(page_title="Outreach Campaign Dashboard", layout="wide")
sns.set(style="whitegrid")

# -------------------------------
# Load and Preprocess Dataset
# -------------------------------
df = pd.read_csv("source_files/final_merged_call_disaster_stats.csv")
df.columns = df.columns.str.lower().str.strip()

# Convert to datetime
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['incident_begin_date'] = pd.to_datetime(df['incident_begin_date'], errors='coerce', utc=True).dt.tz_localize(None)

# -------------------------------
# De-duplicate rows
# -------------------------------
df = df.drop_duplicates(subset=['client_id', 'household_id', 'date'])

# -------------------------------
# Feature Engineering
# -------------------------------
df['age_group'] = pd.cut(df['age'], bins=[17, 30, 45, 60, 75, 100],
                         labels=['18–30', '31–45', '46–60', '61–75', '76+'])

# Safely calculate post-disaster flag
df['disaster_valid'] = df['incident_begin_date'].notna()
df['post_disaster_outreach'] = df['disaster_valid'] & (df['date'] > df['incident_begin_date'])

df['call_month'] = df['date'].dt.to_period('M').astype(str)
df['disaster_month'] = df['incident_begin_date'].dt.to_period('M').astype(str)

# -------------------------------
# Dashboard Header + KPIs
# -------------------------------
st.title("📞 Emergency Alert Outreach Campaign Dashboard")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Calls", f"{len(df):,}")
col2.metric("Unique Households", f"{df['household_id'].nunique():,}")
col3.metric("% Post-Disaster Calls", f"{df['post_disaster_outreach'].mean() * 100:.2f}%")
col4.metric("Counties Targeted", df['countyclean'].nunique())

st.markdown("---")

# -------------------------------
# Bar Chart Helper
# -------------------------------
def demographic_barplot(data, column, title):
    summary = data.groupby(column).agg(total_calls=('client_id', 'count')).reset_index()
    fig, ax = plt.subplots()
    sns.barplot(data=summary.sort_values('total_calls', ascending=False),
                x=column, y='total_calls', ax=ax)
    ax.set_title(title)
    ax.set_xlabel(column.capitalize())
    ax.set_ylabel("Total Calls")
    plt.xticks(rotation=45)
    st.pyplot(fig)

# -------------------------------
# Demographic Distribution
# -------------------------------
col1, col2 = st.columns(2)
with col1:
    demographic_barplot(df, 'ethnicity', 'Outreach by Ethnicity')
    demographic_barplot(df, 'party', 'Outreach by Party')
with col2:
    demographic_barplot(df, 'gender', 'Outreach by Gender')
    demographic_barplot(df, 'age_group', 'Outreach by Age Group')

st.markdown("---")

# -------------------------------
# Monthly Trends
# -------------------------------
monthly_calls = df.groupby('call_month').size().reset_index(name='total_calls')
monthly_disasters = df.groupby('disaster_month').size().reset_index(name='disaster_events')

monthly_calls.rename(columns={'call_month': 'month'}, inplace=True)
monthly_disasters.rename(columns={'disaster_month': 'month'}, inplace=True)

trend = pd.merge(monthly_calls, monthly_disasters, on='month', how='outer').fillna(0)
trend['month'] = pd.to_datetime(trend['month'])
trend = trend.sort_values('month')

fig, ax = plt.subplots()
sns.lineplot(data=trend, x='month', y='total_calls', label='Calls', ax=ax)
sns.lineplot(data=trend, x='month', y='disaster_events', label='Disasters', ax=ax)
ax.set_title("📈 Monthly Trend: Outreach vs. Disasters")
ax.set_xlabel("Month")
ax.set_ylabel("Volume")
st.pyplot(fig)

st.markdown("---")

# -------------------------------
# Top ZIP Codes
# -------------------------------
top_zips = df.groupby('zipcodeclean').agg(total_calls=('client_id', 'count')).reset_index()
top_zips = top_zips.sort_values('total_calls', ascending=False).head(10)

fig, ax = plt.subplots()
sns.barplot(data=top_zips, x='zipcodeclean', y='total_calls', ax=ax)
ax.set_title("Top 10 ZIP Codes by Call Volume")
ax.set_xlabel("ZIP Code")
ax.set_ylabel("Total Calls")
plt.xticks(rotation=45)
st.pyplot(fig)

st.markdown("---")

# -------------------------------
# Footer
# -------------------------------
st.caption(
    "This dashboard summarizes a county-wide phone outreach campaign for emergency alert enrollment. "
    "It integrates disaster data to analyze community targeting patterns and post-disaster response timing."
)
