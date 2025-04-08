import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

# ---------- MySQL Connection ----------
def load_data():
    conn = mysql.connector.connect(
        host="localhost",
        user="your_username",      # 🔁 change this
        password="your_password",  # 🔁 change this
        database="bird_monitoring_db"
    )
    query = "SELECT * FROM bird_table"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ---------- Streamlit App ----------
st.set_page_config(page_title="Bird Monitoring Dashboard", layout="wide")
st.title("🕊️ Bird Monitoring Dashboard")

# Load data
df = load_data()

# ---------- Sidebar Filters ----------
st.sidebar.header("📊 Filter Data")

year = st.sidebar.multiselect("Year", sorted(df["Year"].dropna().unique()), default=None)
observer = st.sidebar.multiselect("Observer", sorted(df["Observer"].dropna().unique()), default=None)
site = st.sidebar.multiselect("Site Name", sorted(df["Site_Name"].dropna().unique()), default=None)
species = st.sidebar.multiselect("Common Name", sorted(df["Common_Name"].dropna().unique()), default=None)
sex = st.sidebar.multiselect("Sex", sorted(df["Sex"].dropna().unique()), default=None)
temperature_range = st.sidebar.slider("Temperature (°F)", 
    float(df["Temperature"].min()), float(df["Temperature"].max()), 
    (float(df["Temperature"].min()), float(df["Temperature"].max()))
)

# ---------- Apply Filters ----------
filtered_df = df.copy()

if year:
    filtered_df = filtered_df[filtered_df["Year"].isin(year)]
if observer:
    filtered_df = filtered_df[filtered_df["Observer"].isin(observer)]
if site:
    filtered_df = filtered_df[filtered_df["Site_Name"].isin(site)]
if species:
    filtered_df = filtered_df[filtered_df["Common_Name"].isin(species)]
if sex:
    filtered_df = filtered_df[filtered_df["Sex"].isin(sex)]
filtered_df = filtered_df[
    (filtered_df["Temperature"] >= temperature_range[0]) &
    (filtered_df["Temperature"] <= temperature_range[1])
]

st.markdown(f"### Showing {len(filtered_df)} filtered records")

# ---------- Summary Cards ----------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Observations", len(filtered_df))
col2.metric("Distinct Species", filtered_df["Common_Name"].nunique())
col3.metric("Unique Sites", filtered_df["Site_Name"].nunique())
col4.metric("Observers", filtered_df["Observer"].nunique())

# ---------- Charts ----------
st.subheader("🔹 Sex Distribution")
fig_sex = px.pie(filtered_df, names="Sex", title="Sex Distribution of Observations")
st.plotly_chart(fig_sex, use_container_width=True)

st.subheader("🔹 Top Observed Species")
top_species = (
    filtered_df["Common_Name"].value_counts().nlargest(10).reset_index()
    .rename(columns={"index": "Common_Name", "Common_Name": "Count"})
)
fig_species = px.bar(top_species, x="Common_Name", y="Count", title="Top 10 Species Observed")
st.plotly_chart(fig_species, use_container_width=True)

st.subheader("🔹 Observations Over Time")
fig_time = px.histogram(filtered_df, x="Date", nbins=30, title="Observation Dates Histogram")
st.plotly_chart(fig_time, use_container_width=True)

# ---------- Raw Data ----------
with st.expander("🔍 View Raw Filtered Data"):
    st.dataframe(filtered_df)

