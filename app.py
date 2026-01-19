import streamlit as st

st.set_page_config(
    page_title="Exam Scheduling System",
    layout="wide"
)

st.title("📘 Exam Scheduling System")
st.markdown("""
Welcome to the **Exam Timetable Optimization Platform**.

Use the **sidebar** to navigate between pages:
- 📅 Exam Schedule
- 👨‍🎓 Student View
- 👨‍🏫 Professor View
- ⚠️ Conflicts
- 📊 Statistics
- 👨‍💼 Dean Dashboard
- 🧑‍💻 Exam Admin
- 🎓 Head of Department
""")
