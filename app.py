import os
import random
import string
import pandas as pd
import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Hanek Technology and Business College - Registrar SIS",
    page_icon="🎓",
    layout="wide",
)

# --- DIRECTORY & CSV FILE PATHS ---
PHOTO_DIR = "student_photos"
os.makedirs(PHOTO_DIR, exist_ok=True)

STUDENT_FILE = "students.csv"
GRADES_FILE = "grades.csv"
PENDING_FILE = "pending_grades.csv"
STAFF_FILE = "staff.csv"
ADMIN_FILE = "admin.csv"
FINANCE_FILE = "finances.csv"
DEPT_FILE = "departments.csv"
PROG_FILE = "programs.csv"
ANNOUNCE_FILE = "announcements.csv"
APPLICATIONS_FILE = "applications.csv"
LOGO_FILE = "logo.png"

CAMPUSES = ["Wolaita Sodo", "Basketo Laska", "Boloso Bombe", "Jinka"]

DEFAULT_DEPARTMENTS = [
    "Cooperative Accounting and Auditing",
    "Cooperative Business Management",
    "Cooperative Marketing",
    "Hardware and Network System (HNS)",
    "Natural Resource Management (NARM)",
    "Crop Production (Plant Science)",
]

DEFAULT_PROGRAMS = [
    "TVET Level I",
    "TVET Level II",
    "TVET Level III",
    "TVET Level IV",
    "Degree Program",
    "Regular",
    "Extension",
]

STAFF_ROLES = [
    "College President",
    "Vice President for Academic Affairs",
    "Cross-Campus Institutional Coach / QA Director",
    "College Dean",
    "Vice Dean",
    "Department Head",
    "Head Registrar",
    "Assistant Registrar",
    "Registrar Officer / Credential Specialist",
    "Senior Secretary",
    "Human Resources Officer",
    "Finance & Procurement Officer",
    "IT / Systems Administrator",
    "Head of Facility Services",
    "Campus Security Guard",
    "Custodial / Maintenance Personnel",
    "Instructor / Lecturer",
]


# --- INITIALIZE CSV STORAGE ---
def init_csvs():
  if not os.path.exists(STUDENT_FILE):
    pd.DataFrame(
        columns=[
            "StudentID",
            "FullName",
            "Campus",
            "Department",
            "ProgramLevel",
            "Modality",
            "Year",
            "Password",
            "Photo",
            "PhotoStatus",
        ]
    ).to_csv(STUDENT_FILE, index=False)
  else:
    df = pd.read_csv(STUDENT_FILE)
    if "PhotoStatus" not in df.columns:
      df["PhotoStatus"] = "Not Uploaded"
      df.to_csv(STUDENT_FILE, index=False)
    if "Photo" not in df.columns:
      df["Photo"] = ""
      df.to_csv(STUDENT_FILE, index=False)

  if not os.path.exists(GRADES_FILE):
    pd.DataFrame(
        columns=[
            "StudentID",
            "FullName",
            "CourseCode",
            "CourseName",
            "CreditHour",
            "Score",
            "Grade",
            "Level",
            "Semester",
            "AcademicYear",
        ]
    ).to_csv(GRADES_FILE, index=False)

  if not os.path.exists(PENDING_FILE):
    pd.DataFrame(
        columns=[
            "PendingID",
            "StudentID",
            "FullName",
            "CourseCode",
            "CourseName",
            "CreditHour",
            "Score",
            "Grade",
            "Level",
            "Semester",
            "Instructor",
        ]
    ).to_csv(PENDING_FILE, index=False)

  if not os.path.exists(STAFF_FILE):
    pd.DataFrame(
        columns=[
            "StaffID",
            "FullName",
            "Role",
            "Campus",
            "Department",
            "InstitutionalEmail",
            "Password",
        ]
    ).to_csv(STAFF_FILE, index=False)

  if not os.path.exists(ADMIN_FILE):
    pd.DataFrame([{"Username": "admin", "Password": "password123"}]).to_csv(
        ADMIN_FILE, index=False
    )

  if not os.path.exists(FINANCE_FILE):
    pd.DataFrame(
        columns=[
            "StudentID",
            "TotalFeeETB",
            "PaidETB",
            "Status",
            "LastUpdated",
        ]
    ).to_csv(FINANCE_FILE, index=False)

  if not os.path.exists(DEPT_FILE):
    pd.DataFrame({"Department": DEFAULT_DEPARTMENTS}).to_csv(
        DEPT_FILE, index=False
    )

  if not os.path.exists(PROG_FILE):
    pd.DataFrame({"Program": DEFAULT_PROGRAMS}).to_csv(PROG_FILE, index=False)

  if not os.path.exists(ANNOUNCE_FILE):
    pd.DataFrame(
        columns=["NoticeID", "Title", "Date", "Category", "Content"]
    ).to_csv(ANNOUNCE_FILE, index=False)

  if not os.path.exists(APPLICATIONS_FILE):
    pd.DataFrame(
        columns=[
            "AppID",
            "FullName",
            "Phone",
            "Campus",
            "Department",
            "ProgramLevel",
            "Modality",
            "Status",
            "DateSubmitted",
        ]
    ).to_csv(APPLICATIONS_FILE, index=False)


init_csvs()


# --- HELPER FUNCTIONS ---
def get_departments():
  if os.path.exists(DEPT_FILE):
    df = pd.read_csv(DEPT_FILE)
    if "Department" in df.columns:
      return df["Department"].dropna().tolist()
  return DEFAULT_DEPARTMENTS


def get_programs():
  if os.path.exists(PROG_FILE):
    df = pd.read_csv(PROG_FILE)
    if "Program" in df.columns:
      return df["Program"].dropna().tolist()
  return DEFAULT_PROGRAMS


def generate_auth_code():
  letters = random.choices(string.ascii_uppercase, k=3)
  digits = random.choices(string.digits, k=5)
  return f"HBC-AUTH-{''.join(letters)}-{''.join(digits)}"


def calculate_grade(score):
  if score >= 90:
    return "A+", 4.0, 12.0
  elif score >= 85:
    return "A", 4.0, 12.0
  elif score >= 80:
    return "A-", 3.75, 11.25
  elif score >= 75:
    return "B+", 3.25, 9.75
  elif score >= 70:
    return "B", 3.0, 9.0
  elif score >= 65:
    return "B-", 2.75, 8.25
  elif score >= 60:
    return "C+", 2.5, 7.5
  elif score >= 50:
    return "C", 2.0, 6.0
  elif score >= 40:
    return "D", 1.0, 3.0
  else:
    return "F", 0.0, 0.0


# --- UI STYLING ---
st.markdown(
    """
    <style>
        .main { background-color: #f1f5f9; }
        h1, h2, h3 { color: #0f172a; font-family: sans-serif; font-weight: 800; }
        .univ-card {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-top: 5px solid #1e3a8a;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 15px -3px rgba(30, 58, 138, 0.1);
            max-width: 500px;
            margin: 0 auto;
            color: #1e293b;
        }
        .portal-banner {
            background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            text-align: center;
            font-weight: 800;
            margin-bottom: 20px;
        }
        .notice-card {
            background: #ffffff;
            border-left: 6px solid #1e3a8a;
            border: 1px solid #e2e8f0;
            padding: 18px 22px;
            margin-bottom: 15px;
            border-radius: 8px;
        }
        .contact-box {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown(
    "<h2 style='text-align: center; color: #1e3a8a;'>Hanek College</h2>",
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    "<p style='text-align: center; font-size: 11px; color: #64748b; margin-top:"
    " -10px;'>Multi-Campus SIS & Registrar</p>",
    unsafe_allow_html=True,
)

if os.path.exists(LOGO_FILE):
  st.sidebar.image(LOGO_FILE, use_column_width=True)

st.sidebar.markdown("---")
role = st.sidebar.selectbox(
    "🧭 Select Portal Access",
    [
        "Home / Public Announcements & Contacts",
        "Online Admission Application",
        "Head Registrar & Administration",
        "Staff & Registrar Officers",
        "Student Portal",
    ],
)

# --- HOME PORTAL ---
if role == "Home / Public Announcements & Contacts":
  col1, col2 = st.columns([2, 1])
  with col1:
    st.title("🏛️ HANEK TECHNOLOGY AND BUSINESS COLLEGE")
    st.subheader(
        "Official Multi-Campus Registrar & Student Information System"
    )
    st.markdown(
        "Serving Wolaita Sodo, Basketo Laska, Boloso Bombe, and Jinka campuses."
    )
  with col2:
    if os.path.exists(LOGO_FILE):
      st.image(LOGO_FILE, width=200)

  st.markdown("---")
  st.markdown("### 📢 Public Announcements")
  ann_df = pd.read_csv(ANNOUNCE_FILE)
  if ann_df.empty:
    st.info("No public announcements currently posted.")
  else:
    for _, row in ann_df.iterrows():
      st.markdown(
          f"""
                <div class="notice-card">
                    <h4 style="margin: 0; color: #1e3a8a;">{row['Title']}</h4>
                    <p style="font-size: 12px; color: #64748b;"><b>Date:</b> {row['Date']} | <b>{row['Category']}</b></p>
                    <p style="margin: 0;">{row['Content']}</p>
                </div>
            """,
          unsafe_allow_html=True,
      )

  st.markdown("---")
  st.markdown("### 📞 Institutional Contact Directory")
  st.markdown(
      """
        <div class="contact-box">
            <h4 style="color: #1e3a8a; margin-top: 0;">Office of the Registrar</h4>
            <p><b>Headquarters:</b> Wolaita Sodo, Ethiopia (P.O. Box 23)</p>
            <p><b>Telephone:</b> +251-46-180-3164 / +251916747538</p>
            <p><b>Email:</b> registrar@hanekcollege.edu.et</p>
            <p><b>Website:</b> http://www.hanekcollege.edu.et</p>
        </div>
    """,
      unsafe_allow_html=True,
  )

# --- ONLINE ADMISSION ---
elif role == "Online Admission Application":
  st.title("📋 Online Admission Application")
  departments_list = get_departments()
  programs_list = get_programs()

  with st.form("online_app"):
    app_name = st.text_input("Full Legal Name")
    app_phone = st.text_input("Phone Number (+251...)")
    app_campus = st.selectbox("Preferred Campus", CAMPUSES)
    app_dept = st.selectbox("Department", departments_list)
    app_prog = st.selectbox("Program Level", programs_list)
    app_mod = st.selectbox("Modality", ["Regular", "Extension"])

    if st.form_submit_button("Submit Application"):
      if app_name and app_phone:
        apps_df = pd.read_csv(APPLICATIONS_FILE)
        new_app = pd.DataFrame([{
            "AppID": "".join(random.choices(string.ascii_uppercase, k=6)),
            "FullName": app_name,
            "Phone": app_phone,
            "Campus": app_campus,
            "Department": app_dept,
            "ProgramLevel": app_prog,
            "Modality": app_mod,
            "Status": "Pending Review",
            "DateSubmitted": pd.Timestamp.now().strftime("%Y-%m-%d"),
        }])
        apps_df = pd.concat([apps_df, new_app], ignore_index=True)
        apps_df.to_csv(APPLICATIONS_FILE, index=False)
        st.success(f"Application submitted successfully for {app_name}!")
      else:
        st.error("Please provide name and phone number.")

# --- HEAD REGISTRAR PORTAL ---
elif role == "Head Registrar & Administration":
  st.sidebar.subheader("🔐 Head Registrar Login")
  username = st.sidebar.text_input("Username")
  password = st.sidebar.text_input("Password", type="password")

  if st.sidebar.button("Login"):
    if username == "admin" and password == "password123":
      st.session_state["authenticated"] = True
      st.session_state["role"] = "Admin"
      st.success("Logged in successfully!")
      st.rerun()
    else:
      st.sidebar.error("Invalid Credentials")

  if st.session_state.get("role") == "Admin":
    st.title("🛡️ Head Registrar Control Dashboard")
    tab1, tab2, tab3 = st.tabs(
        ["Student Records", "Grade Audits", "Credential Issuance"]
    )

    with tab1:
      st.subheader("Student Directory")
      students_df = pd.read_csv(STUDENT_FILE)
      st.dataframe(students_df, use_container_width=True)

    with tab2:
      st.subheader("Pending Grade Approvals")
      pending_df = pd.read_csv(PENDING_FILE)
      if pending_df.empty:
        st.info("No pending grades.")
      else:
        st.dataframe(pending_df, use_container_width=True)
        idx = st.selectbox("Select Pending Index to Authorize", pending_df.index)
        if st.button("Authorize & Post Grade"):
          row = pending_df.loc[idx]
          grades_df = pd.read_csv(GRADES_FILE)
          grade_val, gp, _ = calculate_grade(row["Score"])
          final_row = pd.DataFrame([{
              "StudentID": row["StudentID"],
              "FullName": row["FullName"],
              "CourseCode": row["CourseCode"],
              "CourseName": row["CourseName"],
              "CreditHour": row["CreditHour"],
              "Score": row["Score"],
              "Grade": f"{grade_val} ({gp})",
              "Level": row.get("Level", "TVET Level I"),
              "Semester": row["Semester"],
              "AcademicYear": "2025/2026",
          }])
          grades_df = pd.concat([grades_df, final_row], ignore_index=True)
          grades_df.to_csv(GRADES_FILE, index=False)
          pending_df = pending_df.drop(idx).reset_index(drop=True)
          pending_df.to_csv(PENDING_FILE, index=False)
          st.success("Grade posted successfully!")
          st.rerun()

    with tab3:
      st.subheader("Official Credential Generation")
      students_df = pd.read_csv(STUDENT_FILE)
      if not students_df.empty:
        sel_s = st.selectbox(
            "Select Student", students_df["StudentID"] + " - " + students_df["FullName"]
        )
        sel_sid = sel_s.split(" - ")[0]
        s_info = students_df[students_df["StudentID"] == sel_sid].iloc[0]
        doc_type = st.selectbox(
            "Document Type",
            [
                "Official Academic Transcript",
                "Temporary Grade Report",
                "Official TVET Diploma Certificate",
            ],
        )

        auth_code = generate_auth_code()
        st.markdown(
            f"""
                <div style="border: 2px solid #1e3a8a; padding: 20px; background: white; border-radius: 8px;">
                    <h3 style="text-align: center; color: #1e3a8a;">HANEK TECHNOLOGY AND BUSINESS COLLEGE</h3>
                    <p style="text-align: center; font-size: 12px;">Office of the Registrar | P.O. Box 23, Wolaita Sodo, Ethiopia</p>
                    <hr>
                    <p><b>Student Name:</b> {s_info['FullName']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>ID:</b> {sel_sid}</p>
                    <p><b>Department:</b> {s_info['Department']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Document:</b> {doc_type}</p>
                    <p style="color: blue; font-family: monospace;"><b>Authentication Code:</b> {auth_code}</p>
                </div>
            """,
            unsafe_allow_html=True,
        )

# --- STAFF PORTAL ---
elif role == "Staff & Registrar Officers":
  st.title("👨‍🏫 Staff & Registrar Officers Portal")
  st_id = st.text_input("Staff ID")
  st_pass = st.text_input("Password", type="password")

  if st.button("Staff Login"):
    staff_df = pd.read_csv(STAFF_FILE)
    match = staff_df[
        (staff_df["StaffID"] == st_id) & (staff_df["Password"] == st_pass)
    ]
    if not match.empty:
      st.session_state["staff_logged"] = st_id
      st.session_state["staff_name"] = match.iloc[0]["FullName"]
      st.session_state["staff_role"] = match.iloc[0]["Role"]
      st.success(f"Welcome, {match.iloc[0]['Role']} {match.iloc[0]['FullName']}")
      st.rerun()
    else:
      st.error("Invalid Staff Credentials")

  if "staff_logged" in st.session_state:
    role_title = st.session_state["staff_role"]
    st.info(f"Logged in as: {role_title}")

    if role_title in ["Instructor / Lecturer", "Department Head"]:
      st.subheader("Submit Module Grades")
      students_df = pd.read_csv(STUDENT_FILE)
      if not students_df.empty:
        with st.form("grade_sub"):
          st_target = st.selectbox(
              "Student",
              students_df["StudentID"] + " - " + students_df["FullName"],
          )
          s_id_sel = st_target.split(" - ")[0]
          s_name_sel = st_target.split(" - ")[1]
          lvl = st.selectbox(
              "Level",
              [
                  "TVET Level I",
                  "TVET Level II",
                  "TVET Level III",
                  "TVET Level IV",
              ],
          )
          code = st.text_input("Course Code")
          cname = st.text_input("Course Name")
          cred = st.number_input("Credit Hours", value=3)
          score = st.number_input("Score", min_value=0.0, max_value=100.0, value=75.0)

          if st.form_submit_button("Submit Grade"):
            pending_df = pd.read_csv(PENDING_FILE)
            grade_val, gp, _ = calculate_grade(score)
            new_p = pd.DataFrame([{
                "PendingID": "".join(random.choices(string.ascii_uppercase, k=5)),
                "StudentID": s_id_sel,
                "FullName": s_name_sel,
                "CourseCode": code,
                "CourseName": cname,
                "CreditHour": cred,
                "Score": score,
                "Grade": f"{grade_val} ({gp})",
                "Level": lvl,
                "Semester": "Semester I",
                "Instructor": st.session_state["staff_name"],
            }])
            pending_df = pd.concat([pending_df, new_p], ignore_index=True)
            pending_df.to_csv(PENDING_FILE, index=False)
            st.success("Grade submitted for Head Registrar review!")

# --- STUDENT PORTAL ---
elif role == "Student Portal":
  st.title("🎓 Student Portal Login")
  sid_in = st.text_input("Student ID")
  spass_in = st.text_input("Password", type="password")

  if st.button("Student Login"):
    stud_df = pd.read_csv(STUDENT_FILE)
    match = stud_df[
        (stud_df["StudentID"] == sid_in) & (stud_df["Password"] == spass_in)
    ]
    if not match.empty:
      st.session_state["student_logged"] = sid_in
      st.success("Student Login Successful!")
      st.rerun()
    else:
      st.error("Invalid Student ID or Password")

  if "student_logged" in st.session_state:
    cur_sid = st.session_state["student_logged"]
    stud_df = pd.read_csv(STUDENT_FILE)
    s_info = stud_df[stud_df["StudentID"] == cur_sid].iloc[0]

    st.subheader(f"Welcome, {s_info['FullName']}")
    tab_p, tab_g = st.tabs(["My Profile", "My Grades"])

    with tab_p:
      st.write(f"**Student ID:** {cur_sid}")
      st.write(f"**Campus:** {s_info['Campus']}")
      st.write(f"**Department:** {s_info['Department']}")
      st.write(f"**Program:** {s_info['ProgramLevel']}")

    with tab_g:
      grades_df = pd.read_csv(GRADES_FILE)
      my_g = grades_df[grades_df["StudentID"] == cur_sid]
      if my_g.empty:
        st.info("No authorized grades posted yet.")
      else:
        st.dataframe(my_g, use_container_width=True)

# --- GLOBAL DEVELOPER FOOTER ---
st.markdown("---")
st.markdown(
    "<p style='text-align: center; font-size: 13px; color: #1e3a8a;'>Developed by"
    " <b>Ebirawi Henok Loha</b> | 📱 Phone: <b>+251965514327</b> | ✉️ Email:"
    " <b>henokebirawi3@gmail.com</b><br><span style='color: #64748b;'>Hanek"
    " Technology and Business College — Multi-Campus Registrar & SIS ©"
    " 2026</span></p>",
    unsafe_allow_html=True,
)
