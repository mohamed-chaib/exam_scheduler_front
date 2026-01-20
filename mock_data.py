import requests

url = "http://127.0.0.1:8000"

# 1. Departments (7 total)
departments =  requests.get(url+"/departments").json()

# 2. Formations (A distinct set of formations linked to departments)
# Formations have 6-9 modules typically.
formations = requests.get(url+"/formations").json()

# 3. Modules (Linked to Formations)
modules = requests.get(url+"/modules").json()
# 4. Students (Linked to Formations - Inherit modules automatically)
students =  requests.get(url+"/etudiants").json()
# ---------------- RESOURCES ----------------

# Rooms with capacities
# Rooms limited to 20 students max (Exam mode)
rooms = requests.get(url+"/lieu_examen").json()

professors = requests.get(url+"/professeurs").json()


# ---------------- EXAM SCHEDULE ----------------

# Exams are scheduled per MODULE.
exam_schedule = requests.get(url+"/examens").json()

# ---------------- ANALYTICS MOCK DATA ----------------

rooms_usage = requests.get(url+"/analytics/room_usage").json()

department_conflicts = requests.get(url+"/analytics/department_conflicts").json()

professor_workload = requests.get(url+"/analytics/professor_workload").json()