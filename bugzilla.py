import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
from matplotlib.gridspec import GridSpec

# Load data
df = pd.read_csv("bugzilla_data.csv", parse_dates=["Opened", "Changed"], dayfirst=False)
df['Opened'] = pd.to_datetime(df['Opened'], errors='coerce')
df['Changed'] = pd.to_datetime(df['Changed'], errors='coerce')

today = datetime.today().strftime("%Y-%m-%d")

# Overall Metrics
total_bugs = len(df)
resolved_bugs = len(df[df['Status'] == "RESOLVED"])
confirmed_bugs = len(df[df['Status'] == "CONFIRMED"])
other_bugs = total_bugs - resolved_bugs - confirmed_bugs

# Define overall date range
if not df['Opened'].isna().all():
    start_date = df['Opened'].min().date()
    end_date = datetime.today().date()
    date_range = pd.date_range(start=start_date, end=end_date)
else:
    date_range = pd.date_range(start=datetime.today().date(), periods=1)

# Status Distribution
status_counts = df['Status'].value_counts()

# Component Bar with Summary Labels
component_summary = df.groupby('Component').agg({
    'Bug ID': 'count',
    'Summary': lambda x: '\n'.join(x.head(3))
}).reset_index().rename(columns={'Bug ID': 'Bug Count'})

# Dashboard Plot
fig = plt.figure(figsize=(16, 11))
fig.suptitle(f"📊 Bugzilla Consolidated Dashboard ({today})", fontsize=16, fontweight='bold')
gs = GridSpec(3, 2, figure=fig)

# Burndown + Burnup Chart per Product
ax1 = fig.add_subplot(gs[0, :])
products = df['Product'].dropna().unique()

if not df['Opened'].isna().all():
    for product in products:
        prod_df = df[df['Product'] == product]
        burndown = []
        burnup = []
        burnup_dates = []
        burndown_dates = []

        for date in date_range:
            opened = prod_df[prod_df['Opened'].dt.date <= date.date()]
            resolved = prod_df[(prod_df['Status'] == 'RESOLVED') & (prod_df['Changed'].dt.date <= date.date())]
            burndown_value = len(opened) - len(resolved)
            burnup_value = len(resolved)
            burndown.append(burndown_value)
            burnup.append(burnup_value)
            burnup_dates.append(date)
            burndown_dates.append(date)

        # Line plots
        ax1.plot(date_range, burndown, label=f"{product} Burndown", linestyle='-', linewidth=1.5)
        ax1.plot(date_range, burnup, label=f"{product} Burnup", linestyle='--', linewidth=1.5)

        # Scatter markers
        ax1.scatter(burndown_dates, burndown, color='red', s=15, marker='x', label=f"{product} Open Marks")
        ax1.scatter(burnup_dates, burnup, color='green', s=15, marker='o', label=f"{product} Resolved Marks")

    ax1.set_title("Burndown & Burnup Over Time by Product", fontsize=13, fontweight='bold')
    ax1.set_ylabel("Bug Count")
    ax1.set_xlabel("Date")
    ax1.grid(True)
    ax1.legend(loc='upper left', bbox_to_anchor=(1.01, 1.0), fontsize=8)
else:
    ax1.text(0.5, 0.5, "No date data available", ha='center', va='center')
    ax1.axis("off")

# Pie chart: Status
ax2 = fig.add_subplot(gs[1, 0])
if not status_counts.empty:
    ax2.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=140,
            colors=sns.color_palette("pastel"))
    ax2.set_title("Status Distribution")
else:
    ax2.text(0.5, 0.5, "No Status Data", ha='center', va='center')
    ax2.axis("off")

# Bar chart: Bugs by Component with Summary
ax3 = fig.add_subplot(gs[1, 1])
if not component_summary.empty:
    sns.barplot(x="Bug Count", y="Component", data=component_summary, ax=ax3, palette="coolwarm")
    for i, row in component_summary.iterrows():
        ax3.text(row['Bug Count'] + 0.1, i, row['Summary'], va='center', fontsize=8)
    ax3.set_title("Bugs by Component (with Top Bug Summaries)")
    ax3.set_xlabel("Bug Count")
else:
    ax3.text(0.5, 0.5, "No Component Data", ha='center', va='center')
    ax3.axis("off")

# Summary Section
ax4 = fig.add_subplot(gs[2, :])
ax4.axis("off")
summary_text = f"""
📌 Total Bugs: {total_bugs}      ✅ Resolved: {resolved_bugs}      🕓 Confirmed: {confirmed_bugs}      🔁 Others: {other_bugs}
"""
ax4.text(0.5, 0.5, summary_text, ha='center', va='center', fontsize=12, fontweight='bold')

# Save output
os.makedirs("dashboard_output", exist_ok=True)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig("dashboard_output/Consolidated_Bugzilla_Dashboard.png", dpi=150, bbox_inches="tight")
plt.close()

print("✅ Consolidated dashboard saved at: dashboard_output/Consolidated_Bugzilla_Dashboard.png")
