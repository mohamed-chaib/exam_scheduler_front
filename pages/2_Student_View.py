import streamlit as st
import pandas as pd
from mock_data import (
    students, 
    formations, 
    modules, 
    exam_schedule, 
    rooms, 
    professors,
    departments
)

st.set_page_config(layout="wide")

st.title("👨‍🎓 Student View")

# ---------------- PREPARE DATA ----------------
# Convert lists to DataFrames for easier joining
df_students = pd.DataFrame(students)
df_formations = pd.DataFrame(formations)
df_modules = pd.DataFrame(modules)
df_exams = pd.DataFrame(exam_schedule)
df_rooms = pd.DataFrame(rooms)
df_professors = pd.DataFrame(professors)

# ---------------- STUDENT SELECTION ----------------
st.subheader("🎯 Select Student")

# Create a mapping for the selectbox
student_map = {s["nom"]: s["id"] for s in students}
selected_student_name = st.selectbox("Choose a student", list(student_map.keys()))
selected_student_id = student_map[selected_student_name]

# Get Student Details
student_info = df_students[df_students["id"] == selected_student_id].iloc[0]
formation_id = student_info["formation_id"]
formation_name = df_formations[df_formations["id"] == formation_id]["nom"].iloc[0]

st.info(f"🎓 **Enrolled in:** {formation_name}")

# ---------------- RETRIEVE EXAMS ----------------
# Logic: Student -> Formation -> Modules -> Exams

# 1. Get modules for this formation
student_modules = df_modules[df_modules["formation_id"] == formation_id]

if student_modules.empty:
    st.warning("No modules found for this formation.")
else:
    # 2. Get exams for these modules
    # Merge exams with modules to keep module names
    # 2. Get exams for these modules
    # Merge exams with modules to keep module names
    # Rename 'name' to 'Module' before merge to avoid confusion
    student_modules_renamed = student_modules.rename(columns={"nom": "Module"})
    
    my_exams = pd.merge(
        df_exams, 
        student_modules_renamed, 
        left_on="module_id", 
        right_on="id"
    )
    
    if my_exams.empty:
        st.warning("No exams scheduled for your modules yet.")
    else:
        # 3. Enrich with Room and Professor details
        # Rename 'name' to 'Room' and 'Professor' before merge
        df_rooms_renamed = df_rooms.rename(columns={"nom": "salle"})
        df_profs_renamed = df_professors.rename(columns={"nom": "professeur"})

        my_exams = pd.merge(my_exams, df_rooms_renamed, left_on="salle_id", right_on="id", how="left")
        my_exams = pd.merge(my_exams, df_profs_renamed, left_on="prof_id", right_on="id", how="left")
        
        # 4. Select and Rename Columns for Display
        display_df = my_exams[[
            "Module", 
            "date", 
            "time", 
            "Room", 
            "Professor", 
            "duration"
        ]].copy()
        
        display_df.columns = ["Module", "Date", "Time", "Room", "Professor", "Duration (min)"]
        
        # Sort by Date and Time
        display_df = display_df.sort_values(by=["Date", "Time"])

        # ---------------- DISPLAY ----------------
        st.subheader(f"📅 Exam Schedule for {selected_student_name}")
        st.dataframe(display_df, use_container_width=True)

        # ---------------- METRICS ----------------
        st.subheader("📊 Overview")
        c1, c2 = st.columns(2)
        c1.metric("Total Exams", len(display_df))
        c2.metric("Exam Days", display_df["Date"].nunique())
