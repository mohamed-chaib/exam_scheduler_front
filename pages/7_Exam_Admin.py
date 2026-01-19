import streamlit as st
import pandas as pd
import time
import altair as alt
from mock_data import (
    exam_schedule,
    modules,
    formations,
    departments,
    rooms,
    professors
)

st.set_page_config(layout="wide")

st.title("🧑‍💻 Planning Service - Exam Administrator")
st.markdown("Central hub for **Automatic Generation**, **Conflict Detection**, and **Resource Optimization**.")

# ---------------- PREPARE DATA ----------------
df_exams = pd.DataFrame(exam_schedule)
df_modules = pd.DataFrame(modules)
df_formations = pd.DataFrame(formations)
df_depts = pd.DataFrame(departments)
df_rooms = pd.DataFrame(rooms)
df_profs = pd.DataFrame(professors)

# Add mock department to professors
prof_dept_map = {
    "PROF01": "DEP01", "PROF02": "DEP01", 
    "PROF03": "DEP02", "PROF04": "DEP01",
}
df_profs["dept_id"] = df_profs["id"].map(prof_dept_map)

# Joins
master_df = pd.merge(df_exams, df_modules, left_on="module_id", right_on="id")
master_df = pd.merge(master_df, df_formations, left_on="formation_id", right_on="id", suffixes=("", "_form"))
master_df = pd.merge(master_df, df_depts, left_on="dept_id", right_on="id", suffixes=("", "_dept"))
master_df = pd.merge(master_df, df_rooms, left_on="salle_id", right_on="id", suffixes=("", "_salle"))
master_df = pd.merge(master_df, df_profs, left_on="prof_id", right_on="id", suffixes=("", "_prof"))

master_df = master_df.rename(columns={
    "nom_dept": "Department",
    "nom_form": "Formation",
    "student_count": "Formation_Size",
    "nom": "Module",
    "nom_salle": "Room",
    "capacity": "Capacity",
    "nom_prof": "Professor",
    "dept_id_prof": "Prof_Dept_ID",
    "date_heure": "Date",
})
master_df["Time"] = pd.to_datetime(master_df["Date"]).dt.time
master_df["Date"] = pd.to_datetime(master_df["Date"]).dt.date

# Calculate Efficiency
master_df["Occupancy"] = master_df["Formation_Size"] / master_df["Capacity"]
master_df["Empty_Seats"] = master_df["Capacity"] - master_df["Formation_Size"]

# ---------------- TABS ----------------
tab_gen, tab_conflict, tab_opti = st.tabs([
    "⚙️ Automatic Generation", 
    "⚠️ Conflict Detection", 
    "📊 Resource Optimization"
])

# ---------------- TAB 1: GENERATION ----------------
with tab_gen:
    col_settings, col_action = st.columns([1, 2])
    
    with col_settings:
        st.subheader("Algorithm Settings")
        algo_mode = st.selectbox("Optimization Mode", ["Balanced", "Minimize Conflicts", "Maximize Comfort", "Compact Schedule"])
        time_limit = st.slider("Time Limit (seconds)", 10, 60, 45)
        
        st.write("**Constraints Weighting:**")
        w_students = st.slider("Student Constraints", 0.0, 1.0, 1.0)
        w_resources = st.slider("Resource Efficiency", 0.0, 1.0, 0.8)
        
    with col_action:
        st.subheader("Execution")
        st.info("Ready to generate schedule for Semester 2 (2025).")
        
        if st.button("🚀 Launch Genetic Algorithm", use_container_width=True):
            status_text = st.empty()
            bar = st.progress(0)
            
            for i in range(100):
                time.sleep(0.02) # Fast simulation
                status_text.text(f"Generation {i+1}/100: Mutating schedules... (Best Score: {90 + i/10:.1f})")
                bar.progress(i + 1)
                
            status_text.text("✅ Optimization Converged!")
            st.success(f"Schedule generated in 3.42s. (Simulated) [Mode: {algo_mode}]")
            st.dataframe(master_df[["Date", "Time", "Formation", "Module", "Room"]].head(), use_container_width=True)

# ---------------- TAB 2: CONFLICTS ----------------
with tab_conflict:
    st.header("Real-time Conflict Detection")
    
    # 1. Check Capacity Violations
    cap_violations = master_df[master_df["Capacity"] < master_df["Formation_Size"]]
    
    # 2. Check Dept Mismatches
    dept_mismatch = master_df[master_df["department_id"] != master_df["Prof_Dept_ID"]]
    
    # 3. Prof Overload (Simulated check for > 3)
    prof_daily = master_df.groupby(["Professor", "Date"]).size().reset_index(name="Count")
    prof_overload = prof_daily[prof_daily["Count"] > 3]

    err_c, warn_c = st.columns(2)
    
    with err_c:
        st.error(f"🔴 Critical Errors: {len(cap_violations) + len(prof_overload)}")
        if not cap_violations.empty:
            st.write("**Room Capacity Exceeded:**")
            st.dataframe(cap_violations[["Module", "Room", "Capacity", "Formation_Size"]])
        
        if not prof_overload.empty:
            st.write("**Professor Overload (>3/day):**")
            st.dataframe(prof_overload)
            
    with warn_c:
        st.warning(f"🟠 Warnings: {len(dept_mismatch)}")
        if not dept_mismatch.empty:
            st.write("**Department Mismatch (Priority Rule):**")
            st.dataframe(dept_mismatch[["Professor", "Department", "Module"]])
            if st.button("Auto-Reassign Supervisors"):
                st.success("Supervisors reassigned to match departments (Simulated).")

# ---------------- TAB 3: OPTIMIZATION ----------------
with tab_opti:
    st.header("Resource Optimization")
    
    # --- 1. ROOM OPTIMIZATION ---
    st.subheader("1. Room Optimization")
    
    # Identify Underused and Overloaded rooms
    underused = master_df[master_df["Occupancy"] < 0.5]
    overloaded = master_df[master_df["Occupancy"] > 1.0]
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("**Analysis:**")
        st.write(f"- Underused Rooms (<50%): **{len(underused)}** exams")
        st.write(f"- Overloaded Rooms (>100%): **{len(overloaded)}** exams")
        
        if not underused.empty:
            st.warning(f"⚠️ {len(underused)} exams are in rooms too large for the class size.")
        if not overloaded.empty:
            st.error(f"❌ {len(overloaded)} exams exceed room capacity!")

    with col_r2:
        # Pre-calculate status for cleaner plotting
        def get_status(occ):
            if occ > 1.0: return "Overloaded"
            if occ < 0.5: return "Underused"
            return "Optimal"
        
        master_df["Status"] = master_df["Occupancy"].apply(get_status)

        # Visualization: Bar Chart of Occupancy by Exam (Module)
        st.markdown("**Room Occupancy per Module**")
        chart_rooms = alt.Chart(master_df).mark_bar().encode(
            x=alt.X('Module', sort='-y'),
            y=alt.Y('Occupancy', title='Occupancy Rate (Students/Capacity)'),
            color=alt.Color('Status', scale=alt.Scale(
                domain=['Overloaded', 'Underused', 'Optimal'],
                range=['red', 'orange', 'green']
            )),
            tooltip=['Module', 'Room', 'Formation', 'Occupancy', 'Capacity', 'Formation_Size', 'Status']
        )
        st.altair_chart(chart_rooms, use_container_width=True)

    # --- 2. PROFESSOR WORKLOAD OPTIMIZATION ---
    st.subheader("2. Professor Workload Optimization")
    
    # Calculate daily hours per professor
    # Duration is in minutes, convert to hours
    master_df["Duration_Hours"] = master_df["duration"] / 60.0
    prof_daily_hours = master_df.groupby(["Professor", "Date"])["Duration_Hours"].sum().reset_index()
    
    # Threshold: Max 8 hours
    prof_daily_hours["Overload"] = prof_daily_hours["Duration_Hours"] > 8.0
    prof_overloaded = prof_daily_hours[prof_daily_hours["Overload"] == True]
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.write("**Workload Table (Hours/Day)**")
        st.dataframe(prof_daily_hours, use_container_width=True)
        
    with col_p2:
        if not prof_overloaded.empty:
            st.error(f"❌ **{len(prof_overloaded)} critical overload instances detected (> 8h/day)!**")
            st.dataframe(prof_overloaded)
            st.markdown("👉 **Suggestion:** Reassign exams to underutilized professors.")
        else:
            st.success("✅ No professor exceeds the 8-hour daily limit.")

    # --- 3. TIME SLOT OPTIMIZATION ---
    st.subheader("3. Time Slot Optimization")
    
    exams_per_day = master_df.groupby("Date").size().reset_index(name="Exam_Count")
    
    avg_per_day = exams_per_day["Exam_Count"].mean()
    peak_day = exams_per_day.loc[exams_per_day["Exam_Count"].idxmax()]
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.markdown(f"**Average Exams/Day:** {avg_per_day:.1f}")
        st.markdown(f"**Peak Day:** {peak_day['Date']} ({peak_day['Exam_Count']} exams)")
        
        # Identify "Unused Days" (Simplification: just checking variance)
        if exams_per_day["Exam_Count"].std() > 2:
            st.warning("⚠️ High variance in daily exam counts. Consider spreading exams.")
            
    with col_t2:
         chart_time = alt.Chart(exams_per_day).mark_bar().encode(
            x='Date',
            y='Exam_Count',
            tooltip=['Date', 'Exam_Count']
        )
         st.altair_chart(chart_time, use_container_width=True)

    # --- 4. ADMIN ACTION (SIMULATION) ---
    st.markdown("---")
    st.subheader("🛠️ Global Resource Optimization")
    
    col_act1, col_act2 = st.columns([1, 3])
    
    with col_act1:
        if st.button("✨ Optimize Resources", type="primary"):
            st.session_state["optimized"] = True
            
    with col_act2:
        if st.session_state.get("optimized"):
            st.success("Optimization Simulation Complete.")
            
            # Show Before vs After Comparison
            c_a, c_b = st.columns(2)
            c_a.metric("Empty Seats (Before)", int(master_df["Empty_Seats"].sum()))
            c_a.metric("Overloaded Profs (Before)", len(prof_overloaded))
            
            # Simulation: Reduce empty seats by ~20%, Fix all overloads
            c_b.metric("Empty Seats (After)", int(master_df["Empty_Seats"].sum() * 0.8), delta="-20%", delta_color="normal")
            c_b.metric("Overloaded Profs (After)", 0, delta=f"-{len(prof_overloaded)}", delta_color="inverse")
            
            st.info("Actions Taken: Moved 3 exams to smaller rooms. Reassigned Dr. Turing's afternoon slot.")
