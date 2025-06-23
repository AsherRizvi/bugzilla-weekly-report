import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import datetime

st.set_page_config(layout="wide")

# Load CSV without date parsing first
df = pd.read_csv("bugzilla_data.csv")

# Correct datetime format used in your data
datetime_format = "%m/%d/%Y %H:%M"

# Parse the 'Opened' and 'Changed' columns
df['Opened'] = pd.to_datetime(df['Opened'], format=datetime_format, errors='coerce')
df['Changed'] = pd.to_datetime(df['Changed'], format=datetime_format, errors='coerce')

# UI Elements
st.title("📊 Bugzilla Interactive Dashboard")
product_list = sorted(df['Product'].dropna().unique())
selected_product = st.selectbox("Select Product", product_list)

# Filter by Product
product_df = df[df['Product'] == selected_product]

# Ensure there are valid Opened dates
valid_opened_dates = product_df['Opened'].dropna()
st.write(product_df['Opened'].isna().value_counts())

if product_df['Opened'].dropna().empty:
    st.warning(f"No valid 'Opened' dates for product: {selected_product}")
    st.stop()

if not valid_opened_dates.empty:
    # Date Range Slider
    min_date = valid_opened_dates.min().date()
    max_date = datetime.today().date()

    start_date, end_date = st.slider("Select Date Range (Opened)",
                                     min_value=min_date,
                                     max_value=max_date,
                                     value=(min_date, max_date),
                                     format="YYYY-MM-DD")

    # Filter data based on selected range
    filtered_df = product_df[
        (product_df['Opened'].dt.date >= start_date) &
        (product_df['Opened'].dt.date <= end_date)
    ]
else:
    st.warning("No valid 'Opened' dates found for this product.")
    filtered_df = product_df.iloc[0:0]  # Empty DataFrame

# Today's date for display
today = datetime.today().strftime("%Y-%m-%d")

# Metrics
total_bugs = len(filtered_df)
resolved_bugs = len(filtered_df[filtered_df['Status'] == "RESOLVED"])
confirmed_bugs = len(filtered_df[filtered_df['Status'] == "CONFIRMED"])
other_bugs = total_bugs - resolved_bugs - confirmed_bugs
status_counts = filtered_df['Status'].value_counts()

# Burndown / Burnup Data
burndown, burnup, dates = [], [], []

if not filtered_df['Opened'].isna().all():
    date_range = pd.date_range(start=start_date, end=end_date)
    for date in date_range:
        opened = filtered_df[filtered_df['Opened'].dt.date <= date.date()]
        resolved = filtered_df[
            (filtered_df['Status'] == 'RESOLVED') &
            (filtered_df['Changed'].dt.date <= date.date())
        ]
        burndown.append(len(opened) - len(resolved))
        burnup.append(len(resolved))
        dates.append(date)
else:
    date_range = pd.date_range(start=datetime.today().date(), periods=1)
    burndown = [0]
    burnup = [0]
    dates = list(date_range)

# Component Summary Table
component_summary = filtered_df.groupby('Component').agg({
    'Bug ID': 'count',
    'Summary': lambda x: '\n'.join(x.head(3))
}).reset_index().rename(columns={'Bug ID': 'Bug Count'})

# Plot Setup
fig, axs = plt.subplots(4, 1, figsize=(18, 20), constrained_layout=True)
fig.suptitle(f"{selected_product} Bugzilla Dashboard ({today})", fontsize=18, fontweight='bold')

# 1. Burndown / Burnup
axs[0].plot(dates, burndown, label="Burndown (Open Bugs)", color='red')
axs[0].plot(dates, burnup, label="Burnup (Resolved Bugs)", color='green')
axs[0].scatter(dates, burndown, color='red', s=10)
axs[0].scatter(dates, burnup, color='green', s=10)
axs[0].set_title("Burndown & Burnup Over Time")
axs[0].set_ylabel("Bug Count")
axs[0].set_xlabel("Date")
axs[0].legend()
axs[0].grid(True)
axs[0].set_xticks(dates[::max(len(dates)//10, 1)])
axs[0].tick_params(axis='x', rotation=45)

# 2. Status Pie Chart
if not status_counts.empty:
    axs[1].pie(status_counts, labels=status_counts.index, autopct='%1.1f%%',
               startangle=140, colors=sns.color_palette("pastel"))
    axs[1].set_title("Status Distribution")
    axs[1].axis('equal')
else:
    axs[1].text(0.5, 0.5, "No status data", ha='center', va='center')
    axs[1].axis("off")

# 3. Bugs by Component
if not component_summary.empty:
    sns.barplot(x="Bug Count", y="Component", data=component_summary, ax=axs[2], palette="coolwarm")
    for i, row in component_summary.iterrows():
        axs[2].text(row['Bug Count'] + 0.1, i, row['Summary'], va='center', fontsize=8, wrap=True)
    axs[2].set_title("Bugs by Component (Top Summaries)")
    axs[2].set_xlabel("Bug Count")
else:
    axs[2].text(0.5, 0.5, "No component data", ha='center', va='center')
    axs[2].axis("off")

# 4. Summary Box
axs[3].axis("off")
summary_text = f"""
📌 Total Bugs: {total_bugs}  
✅ Resolved: {resolved_bugs}  
🕓 Confirmed: {confirmed_bugs}  
🔁 Others: {other_bugs}
"""
axs[3].text(0.5, 0.5, summary_text, ha='center', va='center', fontsize=16, fontweight='bold')

# Show Plot in Streamlit
st.pyplot(fig)
