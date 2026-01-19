import streamlit as st
import pandas as pd
from mock_data import (
    exam_schedule, 
    modules, 
    formations, 
    departments, 
    rooms, 
    professors
)

st.set_page_config(layout="wide")

st.title("📅 Master Exam Schedule")

# ---------------- PREPARE DATA ----------------
# Load raw data
df_exams = pd.DataFrame(exam_schedule)
df_modules = pd.DataFrame(modules)
df_formations = pd.DataFrame(formations)
df_depts = pd.DataFrame(departments)
df_rooms = pd.DataFrame(rooms)
df_profs = pd.DataFrame(professors)

# Perform Joins to create a Master DataFrame
# Exams + Modules
master_df = pd.merge(df_exams, df_modules, left_on="module_id", right_on="id", suffixes=("_exam", "_mod"))
# + Formations
master_df = pd.merge(master_df, df_formations, left_on="formation_id", right_on="id", suffixes=("", "_form"))
# + Departments
master_df = pd.merge(master_df, df_depts, left_on="dept_id", right_on="id", suffixes=("", "_dept"))
# + Rooms
master_df = pd.merge(master_df, df_rooms, left_on="salle_id", right_on="id", suffixes=("", "_room"))
# + Professors
master_df = pd.merge(master_df, df_profs, left_on="prof_id", right_on="id", suffixes=("", "_prof"))

# Rename columns for clarity
master_df = master_df.rename(columns={
    "nom": "Module",
    "nom_form": "Formation",
    "nom_dept": "Department",
    "nom_room": "Room",
    "nom_prof": "Professor",
    "date_heure": "Date",
    "duree_minutes": "Duration"
})
master_df["Time"] = pd.to_datetime(master_df["Date"]).dt.time
master_df["Date"] = pd.to_datetime(master_df["Date"]).dt.date

# ---------------- FILTERS ----------------
st.subheader("🔎 Filters")

col1, col2, col3, col4 = st.columns(4)

with col1:
    dept_list = ["All"] + sorted(master_df["Department"].unique().tolist())
    selected_dept = st.selectbox("Department", dept_list)

with col2:
    # Filter formations based on selected department if possible, otherwise all
    if selected_dept != "All":
        form_list = ["All"] + sorted(master_df[master_df["Department"] == selected_dept]["Formation"].unique().tolist())
    else:
        form_list = ["All"] + sorted(master_df["Formation"].unique().tolist())
    selected_form = st.selectbox("Formation", form_list)

with col3:
    date_list = ["All"] + sorted(master_df["Date"].unique().tolist())
    selected_date = st.selectbox("Date", date_list)

with col4:
    room_list = ["All"] + sorted(master_df["Room"].unique().tolist())
    selected_room = st.selectbox("Room", room_list)

# ---------------- APPLY FILTERS ----------------
filtered_df = master_df.copy()

if selected_dept != "All":
    filtered_df = filtered_df[filtered_df["Department"] == selected_dept]

if selected_form != "All":
    filtered_df = filtered_df[filtered_df["Formation"] == selected_form]

if selected_date != "All":
    filtered_df = filtered_df[filtered_df["Date"] == selected_date]

if selected_room != "All":
    filtered_df = filtered_df[filtered_df["Room"] == selected_room]

# ---------------- TABLE ----------------
# Select final columns to display
display_cols = ["Department", "Formation", "Module", "Professor", "Date", "Time", "Room", "Duration"]

st.subheader("📋 Exam Timetable")
st.dataframe(
    filtered_df[display_cols].sort_values(by=["Date", "Time"]),
    use_container_width=True
)

# ---------------- METRICS ----------------
st.subheader("📊 Overview")

c1, c2, c3 = st.columns(3)

c1.metric("Exams Listed", len(filtered_df))
c2.metric("Professors Involved", filtered_df["Professor"].nunique())
c3.metric("Departments Involved", filtered_df["Department"].nunique())
