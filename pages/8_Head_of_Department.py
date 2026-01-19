import streamlit as st
import pandas as pd
from mock_data import (
    exam_schedule,
    modules,
    formations,
    departments,
    rooms,
    professors,
    department_conflicts
)

st.set_page_config(layout="wide")

st.title("🎓 Head of Department")

# ---------------- PREPARE DATA ----------------
# Load raw data
df_exams = pd.DataFrame(exam_schedule)
df_modules = pd.DataFrame(modules)
df_formations = pd.DataFrame(formations)
df_depts = pd.DataFrame(departments)
df_rooms = pd.DataFrame(rooms)
df_profs = pd.DataFrame(professors)

# Joins
master_df = pd.merge(df_exams, df_modules, left_on="module_id", right_on="id")
# Join formations with suffix to avoid 'name' collision
master_df = pd.merge(master_df, df_formations, left_on="formation_id", right_on="id", suffixes=("", "_form"))
# Join depts with suffix
master_df = pd.merge(master_df, df_depts, left_on="dept_id", right_on="id", suffixes=("", "_dept"))
# Join rooms with suffix
master_df = pd.merge(master_df, df_rooms, left_on="salle_id", right_on="id", suffixes=("", "_salle"))
# Join profs with suffix
master_df = pd.merge(master_df, df_profs, left_on="prof_id", right_on="id", suffixes=("", "_prof"))

# Rename columns for clear usage
master_df = master_df.rename(columns={
    "nom_dept": "Department",
    "nom_form": "Formation",
    "nom": "Module",
    "nom_salle": "Room",
    "nom_prof": "Professor",
    "date_heure": "Date",
    "duree_minutes": "Duration"
})
master_df["Time"] = pd.to_datetime(master_df["Date"]).dt.time
master_df["Date"] = pd.to_datetime(master_df["Date"]).dt.date


# ---------------- DEPARTMENT SELECTION ----------------
st.sidebar.header("Configuration")
dept_list = sorted(master_df["Department"].unique().tolist())
selected_dept = st.sidebar.selectbox("Select your Department", dept_list)

# Filter data for this department
dept_df = master_df[master_df["Department"] == selected_dept]

st.subheader(f"Department Management: {selected_dept}")

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["✅ Validation", "📊 Statistics", "⚠️ Conflicts by Formation"])

with tab1:
    st.header("Timetable Validation")
    
    st.dataframe(
        dept_df[["Formation", "Module", "Date", "Time", "Room", "Professor", "Duration"]].sort_values(["Date", "Time"]),
        use_container_width=True
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("Please review the schedule slots above.")
    
    with col2:
        status = st.radio("Head of Department Decision", ["Pending", "Validate", "Reject"], horizontal=True)
        if status == "Validate":
            st.success(f" The schedule for {selected_dept} has been **VALIDATED**.")
        elif status == "Reject":
            st.error(f" The schedule for {selected_dept} has been **REJECTED**.")

with tab2:
    st.header("Department Statistics")
    
    c1, c2, c3 = st.columns(3)
    
    num_formations = dept_df["Formation"].nunique()
    num_modules = dept_df["Module"].nunique()
    num_exams = len(dept_df)
    
    c1.metric("Formations", num_formations)
    c2.metric("Modules", num_modules)
    c3.metric("Total Exams", num_exams)
    
    # Chart: Exams per Formation
    exams_per_form = dept_df["Formation"].value_counts().reset_index()
    exams_per_form.columns = ["Formation", "Exam Count"]
    
    st.bar_chart(exams_per_form.set_index("Formation"))

with tab3:
    st.header("Conflicts by Formation")
    
    # Simulate conflict detection logic for the selected department
    # For now, we simulate this based on the 'department_conflicts' mock data
    # but theoretically we would check overlap here.
    
    # 1. Simple Check: Do any exams in the SAME formation overlap?
    # (Mock logic: grouping by formation, date, time and counting > 1)
    
    conflicts_found = []
    
    for formation in dept_df["Formation"].unique():
        form_exams = dept_df[dept_df["Formation"] == formation]
        # Check for duplicates in Date + Time
        overlaps = form_exams[form_exams.duplicated(subset=["Date", "Time"], keep=False)]
        
        if not overlaps.empty:
            conflicts_found.append({
                "Formation": formation,
                "Type": "Time Overlap",
                "Details": f"{len(overlaps)} exams at the same time"
            })
            
    # Also pull from the global mock data
    mock_conflict = next((item for item in department_conflicts if item["department"] == selected_dept), None)
    
    if mock_conflict and mock_conflict["conflicts"] > 0:
        st.warning(f"Central system detects {mock_conflict['conflicts']} conflicts for this department.")
    else:
        st.success("No major conflicts reported by the central system.")

    if conflicts_found:
        st.error("Conflicts detected within formations:")
        st.table(pd.DataFrame(conflicts_found))
    else:
        st.info("No direct time overlaps detected in formations.")
