import os

import pandas as pd
import plotly.express as px
import streamlit as st

SKILLS = [
    "Python", "SQL", "Machine Learning", "Deep Learning",
    "NLP", "LLMs", "PyTorch", "TensorFlow", "Spark",
    "Docker", "Cloud", "Statistics", "dbt", "Tableau", "Power BI"
]

BINARY_COLS = [skill.replace(" ", "_") + "_binary" for skill in SKILLS]

st.set_page_config(page_title="Data Science Skill Tracker", layout="wide", page_icon="📊")


def load_data():
    if not os.path.exists("skills_data.csv"):
        st.error("No data found. Run pipeline.py and skills.py first.")
        st.stop()
    skills_df = pd.read_csv("skills_data.csv")
    
    if os.path.exists("jobs_raw.csv"):
        jobs_df = pd.read_csv("jobs_raw.csv", dtype=str)
        skills_df["job_id"] = skills_df["job_id"].astype(str)
        jobs_df["job_id"] = jobs_df["job_id"].astype(str)
        skills_df = skills_df.merge(jobs_df[["job_id", "url"]], on="job_id", how="left")
    
    return skills_df


df = load_data()
most_recent_date = df["date"].max()
unique_jobs = df["job_id"].nunique()
unique_days = df["date"].nunique()

st.title("📊 Data Science Skill Tracker")
st.markdown("<span style='color:gray'>Tracking skill demand across remote tech job postings — updated daily</span>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
col1.metric("Total jobs tracked", unique_jobs)
col2.metric("Days of data", unique_days)
col3.metric("Skills tracked", len(SKILLS))

st.subheader("🔥 Today's Most In-Demand Skills")
st.caption(f"Date: {most_recent_date}")

latest_df = df[df["date"] == most_recent_date]
skill_counts = latest_df[BINARY_COLS].sum().sort_values(ascending=True)
skill_counts = skill_counts.reset_index()
skill_counts.columns = ["skill", "count"]
skill_counts["skill"] = skill_counts["skill"].str.replace("_binary", "", regex=False).str.replace("_", " ", regex=False)
fig_bar = px.bar(skill_counts, x="count", y="skill", orientation="h", labels={"count": "Count", "skill": "Skill"})
st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("📈 Skill Trends Over Time")
selected_skills = st.multiselect(
    "Select skills to compare",
    SKILLS,
    default=["Python", "SQL", "Machine Learning", "Docker", "Cloud"],
)

if not selected_skills:
    st.warning("Please select at least one skill to display.")
else:
    selected_cols = [skill.replace(" ", "_") + "_binary" for skill in selected_skills]
    trend_df = df[["date"] + selected_cols].copy()
    trend_df["date"] = pd.to_datetime(trend_df["date"]).dt.date
    trend_df = trend_df.groupby("date")[selected_cols].sum().reset_index()
    trend_df = trend_df.melt(id_vars="date", value_vars=selected_cols, var_name="skill", value_name="count")
    trend_df["skill"] = trend_df["skill"].str.replace("_binary", "", regex=False).str.replace("_", " ", regex=False)
    fig_line = px.line(trend_df, x="date", y="count", color="skill", labels={"count": "Job count", "date": "Date"}, markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

st.subheader("🔍 Drilldown: Jobs Mentioning a Skill")
skill_to_explore = st.selectbox("Select a skill to explore", SKILLS)
skill_filter_col = skill_to_explore.replace(" ", "_") + "_binary"
matched_jobs = df[df[skill_filter_col] == 1].copy()
matched_count = len(matched_jobs)

if matched_count == 0:
    st.write(f"No jobs found mentioning this skill yet.")
else:
    st.write(f"{matched_count} job postings mention {skill_to_explore}")
    matched_jobs = matched_jobs[["date", "title", "url"]].sort_values("date", ascending=False).copy()
    
    if "url" in matched_jobs.columns:
        matched_jobs["title"] = matched_jobs.apply(
            lambda row: f'<a href="{row["url"]}" target="_blank">{row["title"]}</a>' if pd.notna(row.get("url")) else row["title"],
            axis=1
        )
    
    display_df = matched_jobs[["date", "title"]]
    st.markdown(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)

st.markdown("---")
st.markdown("<span style='color:gray; font-size:small'>Data sourced from RemoteOK · NLP by spaCy · Built with Streamlit</span>", unsafe_allow_html=True)

with st.sidebar:
    st.title("About")
    st.write(
        "This dashboard tracks which technical skills appear most frequently in remote job postings. Data is collected daily and analyzed using keyword matching and spaCy NLP."
    )
    st.metric("Last updated", most_recent_date)
