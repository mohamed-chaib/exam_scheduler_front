import streamlit as st
import pandas as pd
from mock_data import (
    students,
    formations,
    modules,
    exam_schedule,
    rooms,
    professors
)

st.set_page_config(layout="wide")
st.title("🏫 Exam Administration Dashboard")

# ---------------- PREPARE DATA ----------------
df_students = pd.DataFrame(students)
df_formations = pd.DataFrame(formations)
df_modules = pd.DataFrame(modules)
df_exams = pd.DataFrame(exam_schedule)
df_rooms = pd.DataFrame(rooms)
df_professors = pd.DataFrame(professors)

# ---------------- CALCULATE FORMATION SIZE ----------------
# عدد الطلاب لكل formation
formation_sizes = df_students.groupby("formation_id").size().reset_index(name="Formation_Size")

# دمج مع df_formations
df_formations = pd.merge(df_formations, formation_sizes, left_on="id", right_on="formation_id", how="left")
df_formations["Formation_Size"] = df_formations["Formation_Size"].fillna(0)

# ---------------- ENRICH EXAMS ----------------
# Merge exams with modules
df_modules_renamed = df_modules.rename(columns={"nom": "Module"})
master_df = pd.merge(
    df_exams,
    df_modules_renamed,
    left_on="module_id",
    right_on="id",
    suffixes=("_exam", "_module")
)

# Merge with formations to get Formation_Size
master_df = pd.merge(
    master_df,
    df_formations[["id", "nom", "Formation_Size"]],
    left_on="formation_id",
    right_on="id",
    how="left",
    suffixes=("", "_formation")
)

# Merge with rooms to get capacity
df_rooms_renamed = df_rooms.rename(columns={"nom": "Room"})
master_df = pd.merge(
    master_df,
    df_rooms_renamed[["id", "Room", "capacite"]],
    left_on="salle_id",
    right_on="id",
    how="left",
    suffixes=("", "_room")
)

# Merge with professors
df_professors_renamed = df_professors.rename(columns={"nom": "Professor"})
master_df = pd.merge(
    master_df,
    df_professors_renamed[["id", "Professor"]],
    left_on="prof_id",
    right_on="id",
    how="left",
    suffixes=("", "_prof")
)

# ---------------- CALCULATE OCCUPANCY ----------------
master_df["Occupancy"] = master_df["Formation_Size"] / master_df["capacite"]

# ---------------- FORMAT DATE & TIME ----------------
master_df["Date"] = pd.to_datetime(master_df["date_heure"]).dt.date
master_df["Time"] = pd.to_datetime(master_df["date_heure"]).dt.time
master_df["Duration (min)"] = master_df["duree_minutes"]

# ---------------- DISPLAY ----------------
st.subheader("📅 Exam Schedule Overview")
display_df = master_df[[
    "Module",
    "nom",
    "Room",
    "Professor",
    "Date",
    "Time",
    "Duration (min)",
    "Formation_Size",
    "capacite",
    "Occupancy"
]].copy()
display_df = display_df.rename(columns={"nom": "Formation", "capacite": "Capacity"})
display_df = display_df.sort_values(by=["Date", "Time"])

st.dataframe(display_df, use_container_width=True)

# ---------------- METRICS ----------------
st.subheader("📊 Key Metrics")
c1, c2, c3 = st.columns(3)
c1.metric("Total Exams", len(display_df))
c2.metric("Total Students", int(df_students.shape[0]))
c3.metric("Avg Occupancy (%)", f"{(master_df['Occupancy'].mean()*100):.2f}%")
