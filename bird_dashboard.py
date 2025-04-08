import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector

# Page config
st.set_page_config(page_title="🐦 Bird Monitoring Dashboard", layout="wide")
st.title("🐦 Bird Monitoring Dashboard")

# MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Padmavathi@09",
    database="bird_monitoring_db"
)

# Load data
@st.cache_data
def load_data():
    query = "SELECT * FROM bird_table"
    df = pd.read_sql(query, conn)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filter Data")

years = sorted(df['Year'].dropna().unique())
if len(years) > 1:
    year_range = st.sidebar.slider("📆 Select Year Range", int(min(years)), int(max(years)), (int(min(years)), int(max(years))))
    df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]

site = st.sidebar.multiselect("📍 Select Site Name", sorted(df['Site_Name'].dropna().unique()))
if site:
    df = df[df['Site_Name'].isin(site)]

observer = st.sidebar.multiselect("🧍 Select Observer", sorted(df['Observer'].dropna().unique()))
if observer:
    df = df[df['Observer'].isin(observer)]

sex = st.sidebar.multiselect("⚧ Select Sex", sorted(df['Sex'].dropna().unique()))
if sex:
    df = df[df['Sex'].isin(sex)]

common_name = st.sidebar.multiselect("🪶 Select Species", sorted(df['Common_Name'].dropna().unique()))
if common_name:
    df = df[df['Common_Name'].isin(common_name)]

if not df['Temperature'].dropna().empty:
    temp_min = float(df['Temperature'].min())
    temp_max = float(df['Temperature'].max())
    if temp_min < temp_max:
        temperature = st.sidebar.slider("🌡 Temperature Range (°C)", temp_min, temp_max, (temp_min, temp_max))
        df = df[(df['Temperature'] >= temperature[0]) & (df['Temperature'] <= temperature[1])]

# Summary cards
st.markdown("### 📊 Exploratory Data Summary")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("📌 Total Observations", len(df))
col2.metric("🪶 Unique Species", df['Common_Name'].nunique())
col3.metric("📍 Unique Sites", df['Site_Name'].nunique())
col4.metric("🧍 Observers", df['Observer'].nunique())

if df['Date'].notna().any():
    date_range_str = f"{df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}"
else:
    date_range_str = "N/A"
col5.markdown(f"<div style='white-space:nowrap; overflow-x:auto;'>📅 Date Range<br><b>{date_range_str}</b></div>", unsafe_allow_html=True)

# Filtered data table
st.subheader(f"📄 Filtered Results ({len(df)} rows)")
st.dataframe(df, use_container_width=True)

# Download
st.download_button("⬇ Download Filtered Data as CSV", df.to_csv(index=False), "filtered_bird_data.csv", "text/csv")

# Visualization 1: Top 10 species
st.subheader("🌟 Top 10 Most Observed Bird Species")
top_species = df['Common_Name'].value_counts().head(10).reset_index()
top_species.columns = ['Common_Name', 'Count']
fig_species = px.bar(top_species, x="Common_Name", y="Count", title="Top 10 Species Observed", text_auto=True)
st.plotly_chart(fig_species, use_container_width=True)

# Visualization 2: Sex Distribution
st.subheader("⚧ Observation Distribution by Sex")
sex_dist = df['Sex'].value_counts().reset_index()
sex_dist.columns = ['Sex', 'Count']
fig_sex = px.pie(sex_dist, names='Sex', values='Count', title="Observation Distribution by Sex")
st.plotly_chart(fig_sex, use_container_width=True)

# 📈 Observation Trends Over Time
st.subheader("📈 Observation Trends Over Time")

df_trend = df.copy()
df_trend = df_trend[df_trend['Date'].notna()]

# Group observations by date
observation_trends = df_trend.groupby(df_trend['Date'].dt.date).size().reset_index(name='Observation_Count')

# Plot based on number of dates
if len(observation_trends) >= 2:
    fig_line = px.line(
        observation_trends,
        x='Date',
        y='Observation_Count',
        title='Observation Trends Over Time',
        markers=True
    )
    st.plotly_chart(fig_line, use_container_width=True)

elif len(observation_trends) == 1:
    st.warning("⚠️ Only one date found in filtered data. Showing as a bar chart.")
    fig_bar = px.bar(
        observation_trends,
        x='Date',
        y='Observation_Count',
        title='Observations on Single Date',
        text_auto=True
    )
    st.plotly_chart(fig_bar, use_container_width=True)

else:
    st.warning("⚠️ No valid observation dates found after applying filters.")

# Visualization 4: Heatmap
st.subheader("🔥 Heatmap: Species vs Site Name")
heatmap_data = df.groupby(['Site_Name', 'Common_Name']).size().unstack(fill_value=0)
if not heatmap_data.empty:
    fig_heatmap = px.imshow(heatmap_data, labels=dict(x="Species", y="Site Name", color="Observations"))
    st.plotly_chart(fig_heatmap, use_container_width=True)
else:
    st.warning("⚠️ No data available to create heatmap.")

# Visualization 5: Environmental Conditions
st.subheader("🌦️ Environmental Conditions vs Sightings")
env_cols = ['Humidity', 'Wind', 'Sky']
for col in env_cols:
    if col in df.columns and df[col].notna().any():
        env_dist = df[col].value_counts().reset_index()
        env_dist.columns = [col, 'Count']
        fig_env = px.bar(env_dist, x=col, y='Count', title=f"{col} vs Sightings", text_auto=True)
        st.plotly_chart(fig_env, use_container_width=True)
