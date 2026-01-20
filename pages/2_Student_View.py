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
st.title("👨‍🎓 Student View")

# ---------------- PREPARE DATA ----------------
df_students = pd.DataFrame(students)
df_formations = pd.DataFrame(formations)
df_modules = pd.DataFrame(modules)
df_exams = pd.DataFrame(exam_schedule)
df_rooms = pd.DataFrame(rooms)
df_professors = pd.DataFrame(professors)

# ---------------- STUDENT SELECTION ----------------
st.subheader("🎯 Select Student")

student_map = {s["nom"]: s["id"] for s in students}
selected_student_name = st.selectbox("Choose a student", list(student_map.keys()))
selected_student_id = student_map[selected_student_name]

student_info = df_students[df_students["id"] == selected_student_id].iloc[0]
formation_id = student_info["formation_id"]
formation_name = df_formations[df_formations["id"] == formation_id]["nom"].iloc[0]

st.info(f"🎓 **Enrolled in:** {formation_name}")

# ---------------- RETRIEVE EXAMS ----------------
# 1. Get modules for this formation
student_modules = df_modules[df_modules["formation_id"] == formation_id]

if student_modules.empty:
    st.warning("No modules found for this formation.")
else:
    # Rename 'nom' to 'Module' to avoid conflicts
    student_modules_renamed = student_modules.rename(columns={"nom": "Module"})

    # Merge exams with modules
    my_exams = pd.merge(
        df_exams, 
        student_modules_renamed, 
        left_on="module_id", 
        right_on="id",
        suffixes=("_exam", "_module")
    )

    if my_exams.empty:
        st.warning("No exams scheduled for your modules yet.")
    else:
        # Merge with Rooms
        df_rooms_renamed = df_rooms.rename(columns={"nom": "Room"})
        my_exams = pd.merge(
            my_exams,
            df_rooms_renamed,
            left_on="salle_id",
            right_on="id",
            how="left",
            suffixes=("", "_room")
        )

        # Merge with Professors
        df_profs_renamed = df_professors.rename(columns={"nom": "Professor"})
        my_exams = pd.merge(
            my_exams,
            df_profs_renamed,
            left_on="prof_id",
            right_on="id",
            how="left",
            suffixes=("", "_prof")
        )

        # ---------------- FORMAT DISPLAY ----------------
        my_exams["Date"] = pd.to_datetime(my_exams["date_heure"]).dt.date
        my_exams["Time"] = pd.to_datetime(my_exams["date_heure"]).dt.time
        my_exams["Duration (min)"] = my_exams["duree_minutes"]

        display_df = my_exams[["Module", "Date", "Time", "Room", "Professor", "Duration (min)"]]
        display_df = display_df.sort_values(by=["Date", "Time"])

        # ---------------- DISPLAY ----------------
        st.subheader(f"📅 Exam Schedule for {selected_student_name}")
        st.dataframe(display_df, use_container_width=True)

        # ---------------- METRICS ----------------
        st.subheader("📊 Overview")
        c1, c2 = st.columns(2)
        c1.metric("Total Exams", len(display_df))
        c2.metric("Exam Days", display_df["Date"].nunique())
