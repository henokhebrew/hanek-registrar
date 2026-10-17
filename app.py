import base64
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


# --- INITIALIZE CSV STORAGE & ADMIN CREDENTIALS ---
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
    pd.DataFrame(
        [{"Username": "admin.hanek", "Password": "He,Ma&Eb!3"}]
    ).to_csv(ADMIN_FILE, index=False)
  else:
    # Ensure admin.hanek exists
    adm_df = pd.read_csv(ADMIN_FILE)
    if "admin.hanek" not in adm_df["Username"].values:
      new_adm = pd.DataFrame(
          [{"Username": "admin.hanek", "Password": "He,Ma&Eb!3"}]
      )
      adm_df = pd.concat([adm_df, new_adm], ignore_index=True)
      adm_df.to_csv(ADMIN_FILE, index=False)

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


# --- UI STYLING & PRINT OPTIMIZATION ---
st.markdown(
    """
    <style>
        .main { background-color: #f1f5f9; }
        h1, h2, h3 { color: #0f172a; font-family: sans-serif; font-weight: 800; }
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
        @media print {
            body { -webkit-print-color-adjust: exact; }
            .stSidebar, .stButton, header { display: none !important; }
            .single-page-doc { page-break-inside: avoid; max-height: 100vh; overflow: hidden; }
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
  username = st.sidebar.text_input("Username", value="admin.hanek")
  password = st.sidebar.text_input("Password", type="password")

  if st.sidebar.button("Login"):
    admin_df = pd.read_csv(ADMIN_FILE)
    match = admin_df[
        (admin_df["Username"] == username) & (admin_df["Password"] == password)
    ]
    if not match.empty:
      st.session_state["authenticated"] = True
      st.session_state["role"] = "Admin"
      st.success("Logged in successfully!")
      st.rerun()
    else:
      st.sidebar.error("Invalid Credentials")

  if st.session_state.get("role") == "Admin":
    st.title("🛡️ Head Registrar Control Dashboard")

    # ALL 10 ADMINISTRATIVE CONTROL TABS
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "Student Records Master",
        "Photo Approvals",
        "Applicants & Admissions",
        "Staff & Officer Directory",
        "Announcements & Notices",
        "Departments & Programs",
        "Grade Approvals & Audits",
        "Financial Accounts",
        "Official Credential Issuance",
        "System Configuration & Logs",
    ])

    departments_list = get_departments()
    programs_list = get_programs()

    with tab1:
      st.subheader("🎓 Student Master Record Management (CRUD)")
      students_df = pd.read_csv(STUDENT_FILE)
      with st.expander("➕ Register New Student Profile", expanded=False):
        with st.form("add_student_form"):
          col1, col2 = st.columns(2)
          with col1:
            s_id = st.text_input("Student ID (e.g., HBC/001/26)")
            s_name = st.text_input("Full Legal Name")
            s_campus = st.selectbox("Assigned Campus", CAMPUSES)
          with col2:
            s_dept = st.selectbox("Department", departments_list)
            s_prog = st.selectbox("Program Level", programs_list)
            s_mod = st.selectbox("Modality", ["Regular", "Extension"])
            s_pass = st.text_input("Default Student Password", type="password")

          if st.form_submit_button("Admit Student Official Record"):
            if s_id and s_name:
              if s_id in students_df["StudentID"].values:
                st.error("Student ID already exists.")
              else:
                new_row = pd.DataFrame([{
                    "StudentID": s_id,
                    "FullName": s_name,
                    "Campus": s_campus,
                    "Department": s_dept,
                    "ProgramLevel": s_prog,
                    "Modality": s_mod,
                    "Year": "1",
                    "Password": s_pass,
                    "Photo": "",
                    "PhotoStatus": "Not Uploaded",
                }])
                students_df = pd.concat(
                    [students_df, new_row], ignore_index=True
                )
                students_df.to_csv(STUDENT_FILE, index=False)
                st.success(f"Student {s_name} admitted successfully!")
                st.rerun()

      st.markdown("---")
      st.markdown("### Existing Student Database")
      if students_df.empty:
        st.info("No student records found.")
      else:
        st.dataframe(students_df, use_container_width=True)
        sel_edit = st.selectbox(
            "Select Student ID for Modification", students_df["StudentID"].tolist()
        )
        if sel_edit:
          st_row = students_df[students_df["StudentID"] == sel_edit].iloc[0]
          with st.form("edit_student_form"):
            e_name = st.text_input("Full Legal Name", value=st_row["FullName"])
            e_campus = st.selectbox(
                "Campus",
                CAMPUSES,
                index=CAMPUSES.index(st_row["Campus"])
                if st_row["Campus"] in CAMPUSES
                else 0,
            )
            e_dept = st.selectbox(
                "Department",
                departments_list,
                index=departments_list.index(st_row["Department"])
                if st_row["Department"] in departments_list
                else 0,
            )
            e_prog = st.selectbox(
                "Program Level",
                programs_list,
                index=programs_list.index(st_row["ProgramLevel"])
                if st_row["ProgramLevel"] in programs_list
                else 0,
            )
            e_pass = st.text_input(
                "Password", value=st_row["Password"], type="password"
            )

            col_btn1, col_btn2 = st.columns(2)
            if col_btn1.form_submit_button("💾 Save Record Changes"):
              students_df.loc[
                  students_df["StudentID"] == sel_edit,
                  ["FullName", "Campus", "Department", "ProgramLevel", "Password"],
              ] = [e_name, e_campus, e_dept, e_prog, e_pass]
              students_df.to_csv(STUDENT_FILE, index=False)
              st.success("Student updated successfully!")
              st.rerun()
            if col_btn2.form_submit_button("🗑️ Purge Student Record"):
              students_df = students_df[students_df["StudentID"] != sel_edit]
              students_df.to_csv(STUDENT_FILE, index=False)
              st.warning("Student purged.")
              st.rerun()

    with tab2:
      st.subheader("🖼️ Student Profile Photo Verification & Authorization")
      students_df = pd.read_csv(STUDENT_FILE)
      pending_p = students_df[students_df["PhotoStatus"] == "Pending Approval"]
      if pending_p.empty:
        st.info("No student profile photographs awaiting approval.")
      else:
        for _, p_row in pending_p.iterrows():
          col_p1, col_p2 = st.columns([1, 2])
          with col_p1:
            if p_row["Photo"] and os.path.exists(p_row["Photo"]):
              st.image(p_row["Photo"], width=120)
            else:
              st.warning("Photo file missing.")
          with col_p2:
            st.write(
                f"**ID:** {p_row['StudentID']} | **Name:** {p_row['FullName']}"
            )
            st.write(
                f"**Campus:** {p_row['Campus']} | **Department:**"
                f" {p_row['Department']}"
            )
            if st.button(
                f"✅ Authorize Photo ({p_row['StudentID']})",
                key=f"auth_p_{p_row['StudentID']}",
            ):
              students_df.loc[
                  students_df["StudentID"] == p_row["StudentID"], "PhotoStatus"
              ] = "Approved"
              students_df.to_csv(STUDENT_FILE, index=False)
              st.success("Photograph authorized successfully!")
              st.rerun()
          st.markdown("---")

    with tab3:
      st.subheader("📋 Online Admission Applications")
      apps_df = pd.read_csv(APPLICATIONS_FILE)
      if apps_df.empty:
        st.info("No online applications.")
      else:
        st.dataframe(apps_df, use_container_width=True)
        sel_app = st.selectbox(
            "Select App ID to Admit", apps_df["AppID"].tolist()
        )
        if st.button("🎓 Convert Applicant to Enrolled Student"):
          app_row = apps_df[apps_df["AppID"] == sel_app].iloc[0]
          new_sid = f"HBC/{random.randint(100,999)}/26"
          new_s = pd.DataFrame([{
              "StudentID": new_sid,
              "FullName": app_row["FullName"],
              "Campus": app_row["Campus"],
              "Department": app_row["Department"],
              "ProgramLevel": app_row["ProgramLevel"],
              "Modality": app_row["Modality"],
              "Year": "1",
              "Password": "password123",
              "Photo": "",
              "PhotoStatus": "Not Uploaded",
          }])
          students_df = pd.read_csv(STUDENT_FILE)
          students_df = pd.concat([students_df, new_s], ignore_index=True)
          students_df.to_csv(STUDENT_FILE, index=False)
          apps_df.loc[apps_df["AppID"] == sel_app, "Status"] = "Admitted"
          apps_df.to_csv(APPLICATIONS_FILE, index=False)
          st.success(f"Admitted successfully as {new_sid}!")
          st.rerun()

    with tab4:
      st.subheader("👨‍🏫 Staff & Registrar Officers Directory")
      staff_df = pd.read_csv(STAFF_FILE)
      if "InstitutionalEmail" not in staff_df.columns:
        staff_df["InstitutionalEmail"] = ""
      with st.expander("➕ Register Staff Member", expanded=False):
        with st.form("add_staff"):
          st_id = st.text_input("Staff ID")
          st_name = st.text_input("Full Name")
          st_role = st.selectbox("Role", STAFF_ROLES)
          st_campus = st.selectbox("Campus", CAMPUSES + ["All Campuses"])
          st_dept = st.text_input(
              "Department / Unit", value="Office of the Registrar"
          )
          st_email = st.text_input("Institutional Email")
          st_pass = st.text_input("Password", type="password")
          if st.form_submit_button("Save Staff Profile"):
            if st_id and st_name:
              new_st = pd.DataFrame([{
                  "StaffID": st_id,
                  "FullName": st_name,
                  "Role": st_role,
                  "Campus": st_campus,
                  "Department": st_dept,
                  "InstitutionalEmail": st_email,
                  "Password": st_pass,
              }])
              staff_df = pd.concat([staff_df, new_st], ignore_index=True)
              staff_df.to_csv(STAFF_FILE, index=False)
              st.success("Staff profile saved!")
              st.rerun()
      if not staff_df.empty:
        st.dataframe(staff_df, use_container_width=True)

    with tab5:
      st.subheader("📢 Announcements & Noticeboard")
      ann_df = pd.read_csv(ANNOUNCE_FILE)
      st.dataframe(ann_df, use_container_width=True)
      with st.form("add_ann"):
        a_title = st.text_input("Notice Title")
        a_cat = st.selectbox(
            "Category",
            ["General Notice", "Exam Schedule", "Registration Deadline"],
        )
        a_cont = st.text_area("Content")
        if st.form_submit_button("Broadcast Notice"):
          if a_title and a_cont:
            new_a = pd.DataFrame([{
                "NoticeID": "".join(random.choices(string.ascii_uppercase, k=5)),
                "Title": a_title,
                "Date": pd.Timestamp.now().strftime("%Y-%m-%d"),
                "Category": a_cat,
                "Content": a_cont,
            }])
            ann_df = pd.concat([ann_df, new_a], ignore_index=True)
            ann_df.to_csv(ANNOUNCE_FILE, index=False)
            st.success("Notice broadcasted!")
            st.rerun()

    with tab6:
      st.subheader("📚 Departments & Programs")
      col_d, col_p = st.columns(2)
      with col_d:
        st.markdown("**Departments**")
        st.write(departments_list)
        with st.form("add_d"):
          nd = st.text_input("New Department")
          if st.form_submit_button("Add Dept"):
            if nd and nd not in departments_list:
              departments_list.append(nd)
              pd.DataFrame({"Department": departments_list}).to_csv(
                  DEPT_FILE, index=False
              )
              st.success("Department added!")
              st.rerun()
      with col_p:
        st.markdown("**Programs**")
        st.write(programs_list)
        with st.form("add_p"):
          np_val = st.text_input("New Program Level")
          if st.form_submit_button("Add Program"):
            if np_val and np_val not in programs_list:
              programs_list.append(np_val)
              pd.DataFrame({"Program": programs_list}).to_csv(
                  PROG_FILE, index=False
              )
              st.success("Program added!")
              st.rerun()

    with tab7:
      st.subheader("✅ Pending Grade Submissions Audit")
      pending_df = pd.read_csv(PENDING_FILE)
      if pending_df.empty:
        st.info("No pending grades.")
      else:
        st.dataframe(pending_df, use_container_width=True)
        idx = st.selectbox("Select Pending Index to Authorize", pending_df.index)
        col_g1, col_g2 = st.columns(2)
        if col_g1.button("✅ Authorize & Post Grade"):
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
        if col_g2.button("❌ Reject Pending Grade"):
          pending_df = pending_df.drop(idx).reset_index(drop=True)
          pending_df.to_csv(PENDING_FILE, index=False)
          st.warning("Pending grade rejected.")
          st.rerun()

    with tab8:
      st.subheader("💰 Student Financial Accounts (ETB)")
      fin_df = pd.read_csv(FINANCE_FILE)
      students_df = pd.read_csv(STUDENT_FILE)
      st.dataframe(fin_df, use_container_width=True)
      with st.form("fin_form"):
        f_sid = st.selectbox(
            "Student ID",
            students_df["StudentID"].tolist()
            if not students_df.empty
            else [],
        )
        tot_f = st.number_input("Total Fee (ETB)", value=15000.0)
        paid_f = st.number_input("Paid (ETB)", value=0.0)
        stat = st.selectbox("Status", ["Pending Clearance", "Fully Cleared"])
        if st.form_submit_button("Update Financial Ledger"):
          if f_sid:
            if not fin_df.empty and f_sid in fin_df["StudentID"].values:
              fin_df.loc[
                  fin_df["StudentID"] == f_sid,
                  ["TotalFeeETB", "PaidETB", "Status"],
              ] = [tot_f, paid_f, stat]
            else:
              new_f = pd.DataFrame([{
                  "StudentID": f_sid,
                  "TotalFeeETB": tot_f,
                  "PaidETB": paid_f,
                  "Status": stat,
                  "LastUpdated": pd.Timestamp.now().strftime("%Y-%m-%d"),
              }])
              fin_df = pd.concat([fin_df, new_f], ignore_index=True)
            fin_df.to_csv(FINANCE_FILE, index=False)
            st.success("Financial ledger updated!")
            st.rerun()

    with tab9:
      st.subheader("🖨️ Official Academic Credential Issuance (Single Page Layout)")
      students_df = pd.read_csv(STUDENT_FILE)
      if not students_df.empty:
        sel_s = st.selectbox(
            "Select Student for Credential",
            students_df["StudentID"] + " - " + students_df["FullName"],
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

        fin_df = pd.read_csv(FINANCE_FILE)
        is_cleared = True
        if not fin_df.empty:
          chk = fin_df[fin_df["StudentID"] == sel_sid]
          if not chk.empty and chk.iloc[0]["Status"] != "Fully Cleared":
            is_cleared = False

        if not is_cleared and doc_type in [
            "Official Academic Transcript",
            "Official TVET Diploma Certificate",
        ]:
          st.error(
              "⚠️ Financial Clearance Required: Outstanding balance in ETB."
          )
        else:
          auth_code = generate_auth_code()
          grades_df = pd.read_csv(GRADES_FILE)
          s_grades = grades_df[grades_df["StudentID"] == sel_sid]

          p_b64_tag = ""
          s_photo = s_info.get("Photo", "")
          if (
              isinstance(s_photo, str)
              and s_photo != ""
              and os.path.exists(s_photo)
          ):
            with open(s_photo, "rb") as image_file:
              encoded_string = base64.b64encode(image_file.read()).decode()
            p_b64_tag = f'<img src="data:image/png;base64,{encoded_string}" style="width:65px; height:80px; border:1px solid #111; object-fit: cover; float: right;" />'

          if doc_type == "Official TVET Diploma Certificate":
            st.markdown(
                f"""
                    <div class="single-page-doc" style="border: 6px double #1e3a8a; padding: 25px; background: #fffdfa; text-align: center; color: #111;">
                        <h2 style="color: #1e3a8a; margin: 0; font-size: 22px;">HANEK TECHNOLOGY AND BUSINESS COLLEGE</h2>
                        <p style="margin: 2px 0; font-size: 12px; font-weight: bold; color: #555;">OFFICE OF THE REGISTRAR</p>
                        <p style="margin: 2px 0; font-size: 10px; color: #444;">Tel: +251-46-180-3164 / +251916747538 | P.O. Box 23, Wolaita Sodo, Ethiopia</p>
                        <hr style="border: 1px solid #1e3a8a; width: 50%; margin: 10px auto;">
                        <h3 style="margin: 8px 0; font-size: 16px; text-transform: uppercase;">TVET LEVEL IV DIPLOMA</h3>
                        <p style="font-size: 12px; font-style: italic; margin: 4px 0;">This is to certify that</p>
                        <h1 style="font-size: 24px; color: #0f172a; margin: 4px 0; text-transform: uppercase;">{s_info['FullName']}</h1>
                        <p style="font-size: 11.5px; line-height: 1.4; max-width: 700px; margin: 8px auto;">
                            having successfully completed the prescribed training program and fulfilled all requirements under the Department of <b>{s_info['Department']}</b>, is hereby awarded the <b>LEVEL IV DIPLOMA</b>.
                        </p>
                        <table style="width: 75%; margin: 10px auto; font-size: 11px; text-align: center;">
                            <tr>
                                <td><b>Student ID:</b> {sel_sid}</td>
                                <td><b>Admission Year:</b> 2026</td>
                                <td><b>Medium:</b> English</td>
                            </tr>
                        </table>
                        <div style="display: flex; justify-content: space-between; margin-top: 25px; padding: 0 30px; font-size: 11px;">
                            <div style="text-align: left;">
                                <p style="margin: 2px 0;"><b>Auth Code:</b> <span style="color: blue; font-family: monospace;">{auth_code}</span></p>
                            </div>
                            <div style="text-align: right;">
                                <p style="margin: 0 0 15px 0;">___________________________</p>
                                <p style="margin: 0; font-weight: bold;">Head Registrar Signature</p>
                            </div>
                        </div>
                    </div>
                """,
                unsafe_allow_html=True,
            )
          else:
            st.markdown(
                f"""
                    <div class="single-page-doc" style="border: 2px solid #111; padding: 15px; background: white; font-family: sans-serif; font-size: 10px; color: #000;">
                        <div style="text-align: center; border-bottom: 2px solid #111; padding-bottom: 5px; margin-bottom: 6px;">
                            {p_b64_tag}
                            <h2 style="margin: 0; font-size: 14px; font-weight: bold;">HANEK TECHNOLOGY AND BUSINESS COLLEGE</h2>
                            <h4 style="margin: 2px 0; font-size: 10px; color: #333;">OFFICE OF THE REGISTRAR</h4>
                            <div style="font-size: 9px; color: #444;">Tel: +251-46-180-3164 | P.O. Box 23, Wolaita Sodo, Ethiopia | Website: http://www.hanekcollege.edu.et</div>
                            <div style="font-size: 10.5px; font-weight: bold; margin-top: 2px; text-transform: uppercase; color: #1e3a8a;">{doc_type}</div>
                        </div>
                        <table style="width: 100%; margin-bottom: 6px; font-size: 10px;">
                            <tr>
                                <td><b>Student Name:</b> {s_info['FullName']}</td>
                                <td><b>Student ID:</b> {sel_sid}</td>
                                <td><b>Admission Year:</b> 2026</td>
                            </tr>
                            <tr>
                                <td><b>Department:</b> {s_info['Department']}</td>
                                <td><b>Program:</b> {s_info['ProgramLevel']}</td>
                                <td><b>Medium:</b> English</td>
                            </tr>
                        </table>
                        <table style="width: 100%; border-collapse: collapse; font-size: 9.5px; margin-bottom: 8px;">
                            <thead>
                                <tr style="background: #f1f5f9;">
                                    <th style="border: 1px solid #bbb; padding: 3px;">Level</th>
                                    <th style="border: 1px solid #bbb; padding: 3px;">Code</th>
                                    <th style="border: 1px solid #bbb; padding: 3px;">Module Title</th>
                                    <th style="border: 1px solid #bbb; padding: 3px;">Cr.Hr</th>
                                    <th style="border: 1px solid #bbb; padding: 3px;">Score</th>
                                    <th style="border: 1px solid #bbb; padding: 3px;">Grade</th>
                                </tr>
                            </thead>
                            <tbody>
                """,
                unsafe_allow_html=True,
            )
            if s_grades.empty:
              st.markdown(
                  '<tr><td colspan="6" style="text-align: center; border: 1px'
                  ' solid #bbb; padding: 5px;">No authorized modules recorded'
                  ' yet.</td></tr>',
                  unsafe_allow_html=True,
              )
            else:
              for _, g_row in s_grades.iterrows():
                st.markdown(
                    f"""
                        <tr>
                            <td style="border: 1px solid #bbb; padding: 3px;">{g_row['Level']}</td>
                            <td style="border: 1px solid #bbb; padding: 3px;">{g_row['CourseCode']}</td>
                            <td style="border: 1px solid #bbb; padding: 3px;">{g_row['CourseName']}</td>
                            <td style="border: 1px solid #bbb; padding: 3px;">{g_row['CreditHour']}</td>
                            <td style="border: 1px solid #bbb; padding: 3px;">{g_row['Score']}</td>
                            <td style="border: 1px solid #bbb; padding: 3px;">{g_row['Grade']}</td>
                        </tr>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown(
                f"""
                            </tbody>
                        </table>
                        <div style="display: flex; justify-content: space-between; border-top: 1px solid #111; padding-top: 5px; font-size: 9.5px;">
                            <div><b>Auth Code:</b> <span style="color: blue; font-family: monospace;">{auth_code}</span></div>
                            <div style="text-align: right;"><b>Head Registrar Signature:</b> ___________________</div>
                        </div>
                    </div>
                """,
                unsafe_allow_html=True,
            )

    with tab10:
      st.subheader("⚙️ System Configuration & Health")
      st.write(f"Total Students: {len(pd.read_csv(STUDENT_FILE))}")
      st.write(f"Total Staff: {len(pd.read_csv(STAFF_FILE))}")
      st.write(f"Pending Grades: {len(pd.read_csv(PENDING_FILE))}")
      st.markdown("---")
      st.markdown("### Upload Institutional Logo")
      ul_logo = st.file_uploader("Logo File", type=["png", "jpg", "jpeg"])
      if ul_logo is not None:
        with open(LOGO_FILE, "wb") as f:
          f.write(ul_logo.getbuffer())
        st.success("Logo uploaded!")

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
          score = st.number_input(
              "Score", min_value=0.0, max_value=100.0, value=75.0
          )

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
    tab_p, tab_g = st.tabs(["My Profile & Photo Upload", "My Grades"])

    with tab_p:
      col1, col2 = st.columns([1, 2])
      with col1:
        st.markdown("### Profile Photograph")
        p_path = s_info.get("Photo", "")
        p_status = s_info.get("PhotoStatus", "Not Uploaded")
        if p_path and os.path.exists(p_path):
          st.image(p_path, width=130)
        else:
          st.info("No photo uploaded.")
        st.write(f"**Status:** `{p_status}`")

        up_p = st.file_uploader(
            "Upload New Passport Photo", type=["png", "jpg", "jpeg"]
        )
        if up_p is not None:
          saved_path = os.path.join(PHOTO_DIR, f"{cur_sid}.png")
          with open(saved_path, "wb") as f:
            f.write(up_p.getbuffer())
          stud_df.loc[
              stud_df["StudentID"] == cur_sid, ["Photo", "PhotoStatus"]
          ] = [saved_path, "Pending Approval"]
          stud_df.to_csv(STUDENT_FILE, index=False)
          st.success("Photo uploaded! Awaiting Head Registrar approval.")
          st.rerun()

      with col2:
        st.info(
            f"**ID:** {cur_sid}\n\n**Campus:**"
            f" {s_info['Campus']}\n\n**Department:**"
            f" {s_info['Department']}\n\n**Program:** {s_info['ProgramLevel']}"
        )

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
    " <b>Ebirawi Henok Loha</b>[span_1](start_span)[span_1](end_span) | 📱 Phone: <b>+251965514327</b> [cite:"
    " 1] | ✉️ Email: <b>henokebirawi3@gmail.com</b>[span_2](start_span)[span_2](end_span)<br><span"
    " style='color: #64748b;'>Hanek Technology and Business College —"
    " Multi-Campus Registrar & SIS © 2026</span></p>",
    unsafe_allow_html=True,
)
