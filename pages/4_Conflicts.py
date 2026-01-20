import streamlit as st
import pandas as pd
from mock_data import (
    department_conflicts,
    professor_workload
)

st.set_page_config(layout="wide")

st.title("⚠️ Conflicts & Alerts")

# ---------------- PREPARE DATA ----------------
df_conflicts = pd.DataFrame(department_conflicts)
df_workload = pd.DataFrame(professor_workload)

# ---------------- SUMMARY ----------------
st.subheader("📊 Conflict Summary")

c1, c2 = st.columns(2)

total_conflicts = df_conflicts["conflicts"].sum()
overloaded_profs = df_workload[df_workload["status"] == "Overload"].shape[0]

c1.metric("Total Departmental Conflicts", total_conflicts)
c2.metric("Professors Overloaded", overloaded_profs)

# ---------------- DETAILED CONFLICTS ----------------
st.subheader("🏢 Departmental Conflicts")

if total_conflicts == 0:
    st.success("✅ No conflicts detected across departments.")
else:
    st.error(f"❌ {total_conflicts } conflicts detected!")
    # Filter to show only departments with conflicts
    st.dataframe(
        df_conflicts[df_conflicts["conflicts"] > 0], 
        use_container_width=True
    )

# ---------------- PROFESSOR OVERLOAD ----------------
st.subheader("👨‍🏫 Professor Workload Issues")

overloaded_df = df_workload[df_workload["status"] == "Overload"]

if overloaded_df.empty:
    st.success("✅ No professor overload detected.")
else:
    st.warning("⚠️ Some professors are exceeding their hour limits.")
    st.dataframe(overloaded_df, use_container_width=True)
