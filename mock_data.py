import requests

# رابط الـ API
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

rooms_usage = [
    {"room": "Amphi A", "usage_rate": 85, "capacity_check": "OK"},
    {"room": "Amphi B", "usage_rate": 60, "capacity_check": "OK"},
    {"room": "Salle 101", "usage_rate": 100, "capacity_check": "FULL"},
    {"room": "Salle 102", "usage_rate": 45, "capacity_check": "OK"},
]

department_conflicts = [
    {"department": "Informatique", "conflicts": 12, "resolved": 8},
    {"department": "Mathématiques", "conflicts": 4, "resolved": 4},
    {"department": "Lettres", "conflicts": 2, "resolved": 0},
    {"department": "Physique", "conflicts": 0, "resolved": 0},
    {"department": "Biologie", "conflicts": 1, "resolved": 1},
    {"department": "Chimie", "conflicts": 3, "resolved": 2},
    {"department": "Économie", "conflicts": 0, "resolved": 0},
]

professor_workload = [
    {"professor": "Dr. Turing", "hours": 12, "status": "Overload"},
    {"professor": "Dr. Lovelace", "hours": 9, "status": "OK"},
    {"professor": "Dr. Shannon", "hours": 6, "status": "OK"},
    {"professor": "Dr. Hopper", "hours": 4, "status": "Underutilized"},
]
