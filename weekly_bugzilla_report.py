import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime, timedelta

# Setup
today = datetime.today()
last_week = today - timedelta(days=7)
os.makedirs("weekly_reports", exist_ok=True)

# Load CSV
df = pd.read_csv("bugzilla_data.csv")
datetime_format = "%m/%d/%Y %H:%M"
df['Opened'] = pd.to_datetime(df['Opened'], format=datetime_format, errors='coerce')
df['Changed'] = pd.to_datetime(df['Changed'], format=datetime_format, errors='coerce')

# Filter for last 7 days
weekly_df = df[df['Opened'] >= last_week]

# Plot
fig, ax = plt.subplots(figsize=(12, 6))
status_counts = weekly_df['Status'].value_counts()
sns.barplot(x=status_counts.index, y=status_counts.values, ax=ax, palette="pastel")
ax.set_title(f"Weekly Bugzilla Report ({last_week.date()} → {today.date()})")
ax.set_ylabel("Bug Count")
ax.set_xlabel("Status")
ax.grid(True)

# Save plot
report_path = f"weekly_reports/Bugzilla_Weekly_Report_{today.strftime('%Y%m%d')}.png"
plt.tight_layout()
plt.savefig(report_path)
print(f"✅ Report saved at {report_path}")
