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

# --- CSV FILE PATHS ---
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
        ]
    ).to_csv(STUDENT_FILE, index=False)

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
    return "A+", 4.0
  elif score >= 85:
    return "A", 4.0
  elif score >= 80:
    return "A-", 3.75
  elif score >= 75:
    return "B+", 3.25
  elif score >= 70:
    return "B", 3.0
  elif score >= 65:
    return "B-", 2.75
  elif score >= 60:
    return "C+", 2.5
  elif score >= 50:
    return "C", 2.0
  elif score >= 40:
    return "D", 1.0
  else:
    return "F", 0.0


# --- CSS STYLING FOR UNIVERSITY PORTAL CARD MODE ---
st.markdown(
    """
    <style>
        .univ-card {
            background-color: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            margin: 0 auto;
            color: #1e293b;
        }
        .univ-header {
            text-align: center;
            margin-bottom: 20px;
        }
        .univ-header h3 {
            color: #0f172a;
            margin: 10px 0 5px 0;
            font-size: 20px;
            font-weight: bold;
        }
        .univ-header p {
            color: #64748b;
            font-size: 13px;
            margin: 0;
        }
        .portal-banner {
            background-color: #1e3a8a;
            color: white;
            padding: 10px 15px;
            border-radius: 6px;
            text-align: center;
            font-weight: bold;
            margin-bottom: 15px;
            font-size: 14px;
        }
        .notice-card {
            background: #f8fafc;
            border-left: 4px solid #1e3a8a;
            padding: 12px 15px;
            margin-bottom: 10px;
            border-radius: 4px;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# --- SIDEBAR PORTAL NAVIGATION & BRANDING ---
st.sidebar.markdown(
    "<h3 style='text-align: center;'>Hanek College Portal</h3>",
    unsafe_allow_html=True,
)

if os.path.exists(LOGO_FILE):
  st.sidebar.image(LOGO_FILE, use_column_width=True)
else:
  st.sidebar.info(
      "💡 Tip: Upload your college logo in the Admin Control Panel under"
      " 'System Settings & Logo'."
  )

st.sidebar.markdown("---")
role = st.sidebar.selectbox(
    "Select Portal Access",
    [
        "Home / Public Announcements",
        "Online Admission Application",
        "Admin / Registrar",
        "Staff / Instructor",
        "Student",
    ],
)

# --- HOME / PUBLIC ANNOUNCEMENTS DASHBOARD ---
if role == "Home / Public Announcements":
  col1, col2 = st.columns([2, 1])
  with col1:
    st.title("HANEK TECHNOLOGY AND BUSINESS COLLEGE")
    st.subheader(
        "Official Multi-Campus Registrar & Student Information System"
    )
    st.write(
        "Welcome to the official institutional portal serving **Wolaita Sodo,"
        " Basketo Laska, Boloso Bombe, and Jinka** campuses. Explore public"
        " announcements, submit new online admission applications, or access"
        " secure portal logins."
    )
  with col2:
    if os.path.exists(LOGO_FILE):
      st.image(LOGO_FILE, width=180)

  st.markdown("---")
  st.markdown("### 📢 Public Announcements & Institutional Notices")

  ann_df = pd.read_csv(ANNOUNCE_FILE)
  if ann_df.empty:
    st.info(
        "No public announcements currently posted. Check back soon for urgent"
        " notices!"
    )
  else:
    for _, row in ann_df.iterrows():
      st.markdown(
          f"""
                <div class="notice-card">
                    <h4 style="margin: 0; color: #1e3a8a;">{row['Title']}</h4>
                    <p style="font-size: 11px; color: #64748b; margin: 2px 0 8px 0;"><b>Date:</b> {row['Date']} | <b>Category:</b> {row['Category']}</p>
                    <p style="margin: 0; font-size: 13px; color: #334155;">{row['Content']}</p>
                </div>
            """,
          unsafe_allow_html=True,
      )

  st.markdown("---")
  st.markdown("### 🏛️ Quick Portal Access Gateways")
  c1, c2, c3 = st.columns(3)
  with c1:
    st.success(
        "**📋 Online Application**\n\nProspective students can apply directly"
        " for TVET and Degree programs."
    )
  with c2:
    st.warning(
        "**🛡️ Admin & Registrar**\n\nManage admissions, staff directory,"
        " announcements, and grade approvals."
    )
  with c3:
    st.error(
        "**🎓 Student & Staff Portals**\n\nSecure login for semester grades,"
        " transcripts, and grade postings."
    )

# --- ONLINE ADMISSION APPLICATION PORTAL ---
elif role == "Online Admission Application":
  st.title("📋 Online Admission Application Portal")
  st.write(
      "Prospective students seeking admission to Hanek Technology and Business"
      " College across **Wolaita Sodo, Basketo Laska, Boloso Bombe, and Jinka**"
      " campuses may submit their application below."
  )

  departments_list = get_departments()
  programs_list = get_programs()

  with st.form("online_application_form"):
    st.markdown("### Applicant Information Form")
    col1, col2 = st.columns(2)
    with col1:
      app_name = st.text_input("Full Legal Name")
      app_phone = st.text_input("Phone Number (+251...)")
      app_campus = st.selectbox("Preferred Campus", CAMPUSES)
    with col2:
      app_dept = st.selectbox("Department of Choice", departments_list)
      app_prog = st.selectbox("Program Level", programs_list)
      app_mod = st.selectbox("Modality", ["Regular", "Extension"])

    submit_app = st.form_submit_button("Submit Official Application")
    if submit_app:
      if app_name and app_phone:
        apps_df = pd.read_csv(APPLICATIONS_FILE)
        new_app = pd.DataFrame([{
            "AppID": "".join(
                random.choices(string.ascii_uppercase + string.digits, k=6)
            ),
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
        st.success(
            f"Application submitted successfully, {app_name}! The Registrar"
            " Office will review your details and contact you."
        )
      else:
        st.error("Please provide your full name and phone number.")

# --- ADMIN / REGISTRAR PORTAL ---
elif role == "Admin / Registrar":
  st.sidebar.subheader("Admin Authentication")
  adm_df = pd.read_csv(ADMIN_FILE)
  username = st.sidebar.text_input("Username")
  password = st.sidebar.text_input("Password", type="password")

  if st.sidebar.button("Login"):
    match = adm_df[
        (adm_df["Username"] == username) & (adm_df["Password"] == password)
    ]
    if not match.empty or (username == "admin" and password == "password123"):
      st.session_state["authenticated"] = True
      st.session_state["role"] = "Admin"
      st.success("Logged in successfully!")
      st.rerun()
    else:
      st.sidebar.error("Invalid Admin Credentials")

  if st.session_state.get("role") == "Admin":
    st.title("🛡️ Admin & Registrar Control Panel")
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "Student Records",
        "Applicants & Admissions",
        "Staff Directory",
        "Announcements & Notices",
        "Departments & Programs",
        "Grade Approvals",
        "Financial Accounts",
        "Document Printing",
        "System Settings & Logs",
    ])

    departments_list = get_departments()
    programs_list = get_programs()

    # TAB 1: STUDENT RECORDS (CRUD)
    with tab1:
      st.subheader("Student Record Management (CRUD)")
      students_df = pd.read_csv(STUDENT_FILE)

      with st.expander("➕ Register New Student", expanded=False):
        with st.form("add_student_form"):
          col1, col2 = st.columns(2)
          with col1:
            s_id = st.text_input("Student ID (e.g., HBC/001/26)")
            s_name = st.text_input("Full Name")
            s_campus = st.selectbox("Campus", CAMPUSES)
          with col2:
            s_dept = st.selectbox("Department", departments_list)
            s_prog = st.selectbox("Program Level", programs_list)
            s_mod = st.selectbox("Modality", ["Regular", "Extension"])
            s_pass = st.text_input("Default Password", type="password")

          if st.form_submit_button("Admit Student"):
            if s_id and s_name:
              if s_id in students_df["StudentID"].values:
                st.error("A student with this ID already exists.")
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
                }])
                students_df = pd.concat(
                    [students_df, new_row], ignore_index=True
                )
                students_df.to_csv(STUDENT_FILE, index=False)
                st.success(f"Student {s_name} admitted successfully!")
                st.rerun()

      st.markdown("---")
      st.markdown("### Existing Student Database (Edit / Delete)")
      if students_df.empty:
        st.info("No student records found.")
      else:
        st.dataframe(students_df, use_container_width=True)

        sel_edit_student = st.selectbox(
            "Select Student ID to Edit or Delete",
            students_df["StudentID"].tolist(),
        )
        if sel_edit_student:
          st_row = students_df[
              students_df["StudentID"] == sel_edit_student
          ].iloc[0]
          with st.form("edit_student_form"):
            e_name = st.text_input("Full Name", value=st_row["FullName"])
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
            e_mod = st.selectbox(
                "Modality",
                ["Regular", "Extension"],
                index=["Regular", "Extension"].index(
                    st_row.get("Modality", "Regular")
                ),
            )
            e_pass = st.text_input(
                "Password", value=st_row["Password"], type="password"
            )

            col_btn1, col_btn2 = st.columns(2)
            update_btn = col_btn1.form_submit_button("💾 Save Changes")
            delete_btn = col_btn2.form_submit_button("🗑️ Delete Student")

            if update_btn:
              students_df.loc[
                  students_df["StudentID"] == sel_edit_student,
                  [
                      "FullName",
                      "Campus",
                      "Department",
                      "ProgramLevel",
                      "Modality",
                      "Password",
                  ],
              ] = [e_name, e_campus, e_dept, e_prog, e_mod, e_pass]
              students_df.to_csv(STUDENT_FILE, index=False)
              st.success("Student record updated successfully!")
              st.rerun()

            if delete_btn:
              students_df = students_df[
                  students_df["StudentID"] != sel_edit_student
              ]
              students_df.to_csv(STUDENT_FILE, index=False)
              st.warning("Student record deleted permanently.")
              st.rerun()

    # TAB 2: APPLICANTS & ADMISSIONS
    with tab2:
      st.subheader("Online Admission Applications Review")
      apps_df = pd.read_csv(APPLICATIONS_FILE)
      if apps_df.empty:
        st.info("No online admission applications submitted yet.")
      else:
        st.dataframe(apps_df, use_container_width=True)
        sel_app = st.selectbox(
            "Select Application ID to Review / Admit", apps_df["AppID"].tolist()
        )
        if sel_app:
          app_row = apps_df[apps_df["AppID"] == sel_app].iloc[0]
          if st.button("🎓 Convert Applicant to Official Student"):
            new_sid = f"HBC/{random.randint(100,999)}/26"
            new_student = pd.DataFrame([{
                "StudentID": new_sid,
                "FullName": app_row["FullName"],
                "Campus": app_row["Campus"],
                "Department": app_row["Department"],
                "ProgramLevel": app_row["ProgramLevel"],
                "Modality": app_row["Modality"],
                "Year": "1",
                "Password": "password123",
                "Photo": "",
            }])
            students_df = pd.read_csv(STUDENT_FILE)
            students_df = pd.concat([students_df, new_student], ignore_index=True)
            students_df.to_csv(STUDENT_FILE, index=False)

            apps_df.loc[apps_df["AppID"] == sel_app, "Status"] = "Admitted"
            apps_df.to_csv(APPLICATIONS_FILE, index=False)
            st.success(
                f"Applicant {app_row['FullName']} successfully admitted with"
                f" ID: {new_sid}!"
            )
            st.rerun()

    # TAB 3: STAFF DIRECTORY
    with tab3:
      st.subheader("Staff & Faculty Directory Management")
      staff_df = pd.read_csv(STAFF_FILE)
      if "InstitutionalEmail" not in staff_df.columns:
        staff_df["InstitutionalEmail"] = ""

      with st.expander("➕ Add New Staff Member", expanded=False):
        with st.form("add_staff_form"):
          st_id = st.text_input("Staff ID")
          st_name = st.text_input("Full Name")
          st_role = st.selectbox("Professional Title / Role", STAFF_ROLES)
          st_campus = st.selectbox("Assigned Campus", CAMPUSES + ["All Campuses"])
          st_dept = st.selectbox(
              "Department / Unit", departments_list + ["General"]
          )
          st_email = st.text_input("Institutional Email")
          st_pass = st.text_input("Password", type="password")

          if st.form_submit_button("Save Staff Member"):
            if st_id and st_name:
              if st_id in staff_df["StaffID"].values:
                st.error("Staff ID already exists.")
              else:
                new_staff = pd.DataFrame([{
                    "StaffID": st_id,
                    "FullName": st_name,
                    "Role": st_role,
                    "Campus": st_campus,
                    "Department": st_dept,
                    "InstitutionalEmail": st_email,
                    "Password": st_pass,
                }])
                staff_df = pd.concat([staff_df, new_staff], ignore_index=True)
                staff_df.to_csv(STAFF_FILE, index=False)
                st.success("Staff profile created successfully!")
                st.rerun()

      st.markdown("---")
      st.markdown("### Existing Staff Database (Edit / Delete)")
      if staff_df.empty:
        st.info("No staff records found.")
      else:
        st.dataframe(staff_df, use_container_width=True)
        sel_edit_staff = st.selectbox(
            "Select Staff ID to Edit or Delete", staff_df["StaffID"].tolist()
        )
        if sel_edit_staff:
          s_row = staff_df[staff_df["StaffID"] == sel_edit_staff].iloc[0]
          with st.form("edit_staff_form"):
            es_name = st.text_input("Full Name", value=s_row["FullName"])
            es_role = st.selectbox(
                "Role",
                STAFF_ROLES,
                index=STAFF_ROLES.index(s_row["Role"])
                if s_row["Role"] in STAFF_ROLES
                else 0,
            )
            es_campus = st.selectbox(
                "Campus",
                CAMPUSES + ["All Campuses"],
                index=(CAMPUSES + ["All Campuses"]).index(s_row["Campus"])
                if s_row["Campus"] in (CAMPUSES + ["All Campuses"])
                else 0,
            )
            es_dept = st.selectbox(
                "Department",
                departments_list + ["General"],
                index=(departments_list + ["General"]).index(s_row["Department"])
                if s_row["Department"] in (departments_list + ["General"])
                else 0,
            )
            es_email = st.text_input(
                "Institutional Email",
                value=s_row.get("InstitutionalEmail", ""),
            )
            es_pass = st.text_input(
                "Password", value=s_row["Password"], type="password"
            )

            col_s1, col_s2 = st.columns(2)
            up_staff = col_s1.form_submit_button("💾 Save Staff Changes")
            del_staff = col_s2.form_submit_button("🗑️ Delete Staff")

            if up_staff:
              staff_df.loc[
                  staff_df["StaffID"] == sel_edit_staff,
                  [
                      "FullName",
                      "Role",
                      "Campus",
                      "Department",
                      "InstitutionalEmail",
                      "Password",
                  ],
              ] = [es_name, es_role, es_campus, es_dept, es_email, es_pass]
              staff_df.to_csv(STAFF_FILE, index=False)
              st.success("Staff record updated successfully!")
              st.rerun()

            if del_staff:
              staff_df = staff_df[staff_df["StaffID"] != sel_edit_staff]
              staff_df.to_csv(STAFF_FILE, index=False)
              st.warning("Staff record deleted permanently.")
              st.rerun()

    # TAB 4: ANNOUNCEMENTS & NOTICES
    with tab4:
      st.subheader("Manage Public Announcements & Notices")
      ann_df = pd.read_csv(ANNOUNCE_FILE)
      st.dataframe(ann_df, use_container_width=True)

      with st.form("add_announcement_form"):
        st.markdown("### Post New Institutional Notice")
        a_title = st.text_input("Notice Title")
        a_cat = st.selectbox(
            "Category",
            [
                "General Notice",
                "Exam Schedule",
                "Registration Deadline",
                "Graduation",
            ],
        )
        a_content = st.text_area("Notice Content")

        if st.form_submit_button("Publish Announcement"):
          if a_title and a_content:
            new_ann = pd.DataFrame([{
                "NoticeID": "".join(
                    random.choices(string.ascii_uppercase + string.digits, k=5)
                ),
                "Title": a_title,
                "Date": pd.Timestamp.now().strftime("%Y-%m-%d"),
                "Category": a_cat,
                "Content": a_content,
            }])
            ann_df = pd.concat([ann_df, new_ann], ignore_index=True)
            ann_df.to_csv(ANNOUNCE_FILE, index=False)
            st.success("Announcement published successfully!")
            st.rerun()

      if not ann_df.empty:
        with st.form("delete_ann_form"):
          del_notice = st.selectbox(
              "Select Notice to Delete", ann_df["Title"].tolist()
          )
          if st.form_submit_button("Delete Notice"):
            ann_df = ann_df[ann_df["Title"] != del_notice]
            ann_df.to_csv(ANNOUNCE_FILE, index=False)
            st.warning("Notice deleted.")
            st.rerun()

    # TAB 5: DEPARTMENTS & PROGRAMS
    with tab5:
      st.subheader("Manage Academic Departments & Programs")
      col_dept, col_prog = st.columns(2)

      with col_dept:
        st.markdown("### 📚 Departments")
        dept_df = pd.DataFrame({"Department": departments_list})
        st.dataframe(dept_df, use_container_width=True)

        with st.form("add_dept_form"):
          new_d = st.text_input("New Department Name")
          if st.form_submit_button("Add Department"):
            if new_d and new_d not in departments_list:
              departments_list.append(new_d)
              pd.DataFrame({"Department": departments_list}).to_csv(
                  DEPT_FILE, index=False
              )
              st.success(f"Department '{new_d}' added successfully!")
              st.rerun()

        with st.form("remove_dept_form"):
          rem_d = st.selectbox("Select Department to Remove", departments_list)
          if st.form_submit_button("Remove Department"):
            if len(departments_list) > 1:
              departments_list.remove(rem_d)
              pd.DataFrame({"Department": departments_list}).to_csv(
                  DEPT_FILE, index=False
              )
              st.warning(f"Department '{rem_d}' removed.")
              st.rerun()
            else:
              st.error("You must retain at least one department.")

      with col_prog:
        st.markdown("### 🎓 Program Levels & Modalities")
        prog_df = pd.DataFrame({"Program": programs_list})
        st.dataframe(prog_df, use_container_width=True)

        with st.form("add_prog_form"):
          new_p = st.text_input("New Program / Modality Name")
          if st.form_submit_button("Add Program"):
            if new_p and new_p not in programs_list:
              programs_list.append(new_p)
              pd.DataFrame({"Program": programs_list}).to_csv(
                  PROG_FILE, index=False
              )
              st.success(f"Program '{new_p}' added successfully!")
              st.rerun()

        with st.form("remove_prog_form"):
          rem_p = st.selectbox("Select Program to Remove", programs_list)
          if st.form_submit_button("Remove Program"):
            if len(programs_list) > 1:
              programs_list.remove(rem_p)
              pd.DataFrame({"Program": programs_list}).to_csv(
                  PROG_FILE, index=False
              )
              st.warning(f"Program '{rem_p}' removed.")
              st.rerun()
            else:
              st.error("You must retain at least one program.")

    # TAB 6: GRADE APPROVALS
    with tab6:
      st.subheader("Pending Grade Approvals & Moderation")
      pending_df = pd.read_csv(PENDING_FILE)
      if pending_df.empty:
        st.info("No pending grades awaiting registrar approval.")
      else:
        st.dataframe(pending_df, use_container_width=True)
        approve_id = st.selectbox(
            "Select Pending Item Index to Approve", pending_df.index
        )
        col_app1, col_app2 = st.columns(2)
        if col_app1.button("✅ Approve & Post Grade"):
          row = pending_df.loc[approve_id]
          grades_df = pd.read_csv(GRADES_FILE)
          grade_val, gp = calculate_grade(row["Score"])
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

          pending_df = pending_df.drop(approve_id).reset_index(drop=True)
          pending_df.to_csv(PENDING_FILE, index=False)
          st.success("Grade successfully approved and posted to transcript!")
          st.rerun()

        if col_app2.button("❌ Reject / Delete Pending Grade"):
          pending_df = pending_df.drop(approve_id).reset_index(drop=True)
          pending_df.to_csv(PENDING_FILE, index=False)
          st.warning("Pending grade submission rejected and deleted.")
          st.rerun()

    # TAB 7: FINANCIAL ACCOUNTS (ETB)
    with tab7:
      st.subheader("Student Financial Accounts & Clearance (ETB)")
      fin_df = pd.read_csv(FINANCE_FILE)
      students_df = pd.read_csv(STUDENT_FILE)
      st.dataframe(fin_df, use_container_width=True)

      with st.form("finance_form"):
        st.markdown("### Update Student Tuition Balance (ETB)")
        f_sid = st.selectbox(
            "Select Student ID",
            students_df["StudentID"].tolist()
            if not students_df.empty
            else [],
        )
        tot_fee = st.number_input("Total Tuition Fee (ETB)", value=15000.0)
        paid_fee = st.number_input("Amount Paid (ETB)", value=0.0)
        f_status = st.selectbox(
            "Financial Clearance Status",
            ["Pending Clearance", "Fully Cleared"],
        )

        if st.form_submit_button("Update Financial Status"):
          if f_sid:
            if not fin_df.empty and f_sid in fin_df["StudentID"].values:
              fin_df.loc[fin_df["StudentID"] == f_sid, [
                  "TotalFeeETB",
                  "PaidETB",
                  "Status",
              ]] = [tot_fee, paid_fee, f_status]
            else:
              new_f = pd.DataFrame([{
                  "StudentID": f_sid,
                  "TotalFeeETB": tot_fee,
                  "PaidETB": paid_fee,
                  "Status": f_status,
                  "LastUpdated": pd.Timestamp.now().strftime("%Y-%m-%d"),
              }])
              fin_df = pd.concat([fin_df, new_f], ignore_index=True)
            fin_df.to_csv(FINANCE_FILE, index=False)
            st.success("Financial records updated successfully!")
            st.rerun()

    # TAB 8: DOCUMENT PRINTING
    with tab8:
      st.subheader(
          "Smart Landscape Academic Document Generation (Admin Office)"
      )
      students_df = pd.read_csv(STUDENT_FILE)
      if students_df.empty:
        st.info("No students available in the system.")
      else:
        target_s = st.selectbox(
            "Select Student for Smart Document Generation",
            students_df["StudentID"]
            + " - "
            + students_df["FullName"]
            + " ("
            + students_df["Department"]
            + ")",
        )
        sel_sid = target_s.split(" - ")[0]
        s_info = students_df[students_df["StudentID"] == sel_sid].iloc[0]

        doc_type = st.selectbox(
            "Select Document Type",
            [
                "Official Academic Transcript (Multi-Level TVET)",
                "Temporary Grade Report (Tempo)",
                "Original Document Copy",
            ],
        )

        fin_df = pd.read_csv(FINANCE_FILE)
        is_cleared = True
        if not fin_df.empty:
          chk = fin_df[fin_df["StudentID"] == sel_sid]
          if not chk.empty and chk.iloc[0]["Status"] != "Fully Cleared":
            is_cleared = False

        if not is_cleared and doc_type in [
            "Official Academic Transcript (Multi-Level TVET)",
            "Original Document Copy",
        ]:
          st.error(
              "⚠️ Financial Clearance Required: This student has an unpaid"
              " balance in ETB. Official transcripts and original copies are"
              " locked until clearance is settled."
          )
        else:
          auth_code = generate_auth_code()
          st.markdown(
              f"""
                    <style>
                        @media print {{
                            @page {{ size: landscape; margin: 10mm; }}
                            body {{ -webkit-print-color-adjust: exact; }}
                        }}
                        .transcript-box {{
                            border: 2px solid #111;
                            padding: 20px;
                            border-radius: 6px;
                            background-color: #ffffff;
                            color: #000;
                            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                            font-size: 11px;
                            width: 100%;
                        }}
                        .t-header {{
                            text-align: center;
                            border-bottom: 2px solid #111;
                            padding-bottom: 8px;
                            margin-bottom: 10px;
                        }}
                        .t-header h2 {{ margin: 0; font-size: 16px; font-weight: bold; letter-spacing: 0.5px; }}
                        .t-header h4 {{ margin: 3px 0; font-size: 12px; color: #333; }}
                        .t-info-table {{
                            width: 100%;
                            margin-bottom: 10px;
                            font-size: 11px;
                        }}
                        .t-info-table td {{ padding: 2px 4px; }}
                        .level-grid {{
                            display: flex;
                            flex-wrap: wrap;
                            gap: 15px;
                            justify-content: space-between;
                        }}
                        .level-card {{
                            width: 48%;
                            border: 1px solid #666;
                            padding: 8px;
                            margin-bottom: 10px;
                            border-radius: 4px;
                            background: #fafafa;
                        }}
                        .level-title {{
                            font-weight: bold;
                            background: #e2e8f0;
                            padding: 3px 6px;
                            margin-bottom: 5px;
                            font-size: 11px;
                            text-align: center;
                            border-bottom: 1px solid #ccc;
                        }}
                        .mini-table {{
                            width: 100%;
                            border-collapse: collapse;
                            font-size: 10px;
                        }}
                        .mini-table th, .mini-table td {{
                            border: 1px solid #bbb;
                            padding: 3px 5px;
                            text-align: left;
                        }}
                        .mini-table th {{ background: #f1f5f9; }}
                        .t-footer {{
                            margin-top: 15px;
                            border-top: 1px solid #111;
                            padding-top: 10px;
                            display: flex;
                            justify-content: space-between;
                            align-items: flex-end;
                            font-size: 11px;
                        }}
                    </style>

                    <div class="transcript-box">
                        <div class="t-header">
                            <h2>HANEK TECHNOLOGY AND BUSINESS COLLEGE</h2>
                            <h4>OFFICE OF THE REGISTRAR - {s_info['Campus'].upper()} CAMPUS</h4>
                            <div style="font-size: 12px; font-weight: bold; margin-top: 2px; text-transform: uppercase;">{doc_type}</div>
                        </div>

                        <table class="t-info-table">
                            <tr>
                                <td><b>Student Name:</b> {s_info['FullName']}</td>
                                <td><b>Student ID:</b> {sel_sid}</td>
                                <td><b>Admission Year:</b> 2026</td>
                            </tr>
                            <tr>
                                <td><b>Department:</b> {s_info['Department']}</td>
                                <td><b>Program Level:</b> {s_info['ProgramLevel']} ({s_info.get('Modality', 'Regular')})</td>
                                <td><b>Medium of Instruction:</b> English</td>
                            </tr>
                        </table>

                        <div class="level-grid">
                """,
              unsafe_allow_html=True,
          )

          grades_df = pd.read_csv(GRADES_FILE)
          s_grades = grades_df[grades_df["StudentID"] == sel_sid]

          levels = [
              "TVET Level I",
              "TVET Level II",
              "TVET Level III",
              "TVET Level IV",
          ]
          for lvl in levels:
            lvl_grades = s_grades[s_grades["Level"] == lvl]
            st.markdown(
                f"""
                        <div class="level-card">
                            <div class="level-title">{lvl} Modules & Assessment</div>
                            <table class="mini-table">
                                <thead>
                                    <tr>
                                        <th>Code</th>
                                        <th>Module Title</th>
                                        <th>Cr.Hr</th>
                                        <th>Score</th>
                                        <th>Grade</th>
                                    </tr>
                                </thead>
                                <tbody>
                    """,
                unsafe_allow_html=True,
            )

            if not lvl_grades.empty:
              for _, row in lvl_grades.iterrows():
                st.markdown(
                    f"""
                            <tr>
                                <td>{row['CourseCode']}</td>
                                <td>{row['CourseName']}</td>
                                <td>{row['CreditHour']}</td>
                                <td>{row['Score']}</td>
                                <td>{row['Grade']}</td>
                            </tr>
                        """,
                    unsafe_allow_html=True,
                )
            else:
              st.markdown(
                  """
                            <tr>
                                <td colspan="5" style="text-align: center; color: #777;">No modules recorded for this level.</td>
                            </tr>
                        """,
                  unsafe_allow_html=True,
              )

            st.markdown(
                """
                                </tbody>
                            </table>
                        </div>
                    """,
                unsafe_allow_html=True,
            )

          st.markdown(
              f"""
                        </div>

                        <div class="t-footer">
                            <div>
                                <p style="margin: 2px 0;"><b>Authentication Code:</b> <span style="color: blue; font-family: monospace;">{auth_code}</span></p>
                                <p style="margin: 2px 0; font-size: 10px; color: #555;">Certified true record issued by the Registrar Office, Hanek Technology and Business College. Any alterations invalidate this document.</p>
                            </div>
                            <div style="text-align: right;">
                                <p style="margin: 15px 0 2px 0;">___________________________</p>
                                <p style="margin: 0; font-weight: bold;">Registrar Office Seal & Signature</p>
                            </div>
                        </div>
                    </div>
                """,
              unsafe_allow_html=True,
          )

          st.info(
              "💡 **Smart Print Tip:** Press `Ctrl + P` (or use browser share"
              " menu on mobile) and select **Landscape** orientation to print"
              " this multi-level compact layout perfectly on a single sheet!"
          )

    # TAB 9: SYSTEM SETTINGS & LOGS
    with tab9:
      st.subheader("System Settings & Database Health")
      st.write(
          f"Total Registered Students: {len(pd.read_csv(STUDENT_FILE))}"
      )
      st.write(f"Total Registered Staff: {len(pd.read_csv(STAFF_FILE))}")
      st.write(
          f"Pending Grade Approvals:"
          f" {len(pd.read_csv(PENDING_FILE))}"
      )
      st.write(f"Official Posted Grades: {len(pd.read_csv(GRADES_FILE))}")
      st.write(f"Total Applications: {len(pd.read_csv(APPLICATIONS_FILE))}")

      st.markdown("---")
      st.markdown("### Upload College Logo")
      uploaded_logo = st.file_uploader(
          "Choose logo image (PNG / JPG)", type=["png", "jpg", "jpeg"]
      )
      if uploaded_logo is not None:
        with open(LOGO_FILE, "wb") as f:
          f.write(uploaded_logo.getbuffer())
        st.success("Logo uploaded successfully!")

# --- STAFF / INSTRUCTOR PORTAL ---
elif role == "Staff / Instructor":
  st.markdown("<br>", unsafe_allow_html=True)
  st.markdown(
      """
        <div class="univ-card">
            <div class="univ-header">
    """,
      unsafe_allow_html=True,
  )

  if os.path.exists(LOGO_FILE):
    st.image(LOGO_FILE, width=90)

  st.markdown(
      """
                <h3>Hanek Technology & Business College</h3>
                <p>Staff & Faculty Portal Authentication</p>
            </div>
            <div class="portal-banner">FACULTY & INSTRUCTOR LOGIN</div>
    """,
      unsafe_allow_html=True,
  )

  st_id_in = st.text_input("Staff ID")
  st_pass_in = st.text_input("Password", type="password")

  if st.button("Staff Login", use_container_width=True):
    staff_df = pd.read_csv(STAFF_FILE)
    match = staff_df[
        (staff_df["StaffID"] == st_id_in)
        & (staff_df["Password"] == st_pass_in)
    ]
    if not match.empty:
      st.session_state["staff_logged"] = st_id_in
      st.session_state["staff_name"] = match.iloc[0]["FullName"]
      st.session_state["staff_role"] = match.iloc[0]["Role"]
      st.session_state["staff_dept"] = match.iloc[0]["Department"]
      st.session_state["staff_email"] = match.get(
          "InstitutionalEmail", pd.Series([""])
      ).iloc[0]
      st.success(f"Welcome, {match.iloc[0]['Role']} {match.iloc[0]['FullName']}")
      st.rerun()
    else:
      st.error("Invalid Staff Credentials")

  st.markdown("</div>", unsafe_allow_html=True)

  if "staff_logged" in st.session_state:
    st.markdown("---")
    st.title(
        f"👨‍🏫 Staff Portal: {st.session_state['staff_name']} ("
        f"{st.session_state['staff_role']})"
    )
    st.info(
        f"📧 **Institutional Email:**"
        f" {st.session_state.get('staff_email', 'Not Assigned')}"
    )
    st.markdown("### Submit Module Grades (Manual Entry by Instructor)")

    students_df = pd.read_csv(STUDENT_FILE)
    if students_df.empty:
      st.warning("No students found in system.")
    else:
      with st.form("submit_grade_form"):
        target_student = st.selectbox(
            "Select Student ID & Name",
            students_df["StudentID"]
            + " - "
            + students_df["FullName"]
            + " ("
            + students_df["Department"]
            + ")",
        )

        selected_sid = target_student.split(" - ")[0]
        student_row = students_df[students_df["StudentID"] == selected_sid].iloc[
            0
        ]

        c_level = st.selectbox(
            "Select TVET Level",
            ["TVET Level I", "TVET Level II", "TVET Level III", "TVET Level IV"],
        )
        c_code = st.text_input("Module / Course Code (e.g., COAC-311)")
        c_name = st.text_input("Module / Course Title")
        c_credit = st.number_input(
            "Credit Hours", min_value=1, max_value=10, value=3
        )
        score = st.number_input(
            "Numerical Score (0 - 100)",
            min_value=0.0,
            max_value=100.0,
            value=75.0,
        )
        semester = st.selectbox("Semester", ["Semester I", "Semester II"])

        if st.form_submit_button("Submit Grade to Registrar"):
          if c_code and c_name:
            pending_df = pd.read_csv(PENDING_FILE)
            grade_val, gp = calculate_grade(score)
            new_pending = pd.DataFrame([{
                "PendingID": "".join(
                    random.choices(string.ascii_uppercase + string.digits, k=6)
                ),
                "StudentID": selected_sid,
                "FullName": student_row["FullName"],
                "CourseCode": c_code,
                "CourseName": c_name,
                "CreditHour": c_credit,
                "Score": score,
                "Grade": f"{grade_val} ({gp})",
                "Level": c_level,
                "Semester": semester,
                "Instructor": st.session_state["staff_name"],
            }])
            pending_df = pd.concat([pending_df, new_pending], ignore_index=True)
            pending_df.to_csv(PENDING_FILE, index=False)
            st.success(
                f"Grade submitted successfully for {c_name} ({c_level})!"
                " Awaiting Registrar approval."
            )
          else:
            st.error("Please provide both module code and title.")

# --- STUDENT PORTAL ---
elif role == "Student":
  st.markdown("<br>", unsafe_allow_html=True)
  st.markdown(
      """
        <div class="univ-card">
            <div class="univ-header">
    """,
      unsafe_allow_html=True,
  )

  if os.path.exists(LOGO_FILE):
    st.image(LOGO_FILE, width=90)

  st.markdown(
      """
                <h3>Hanek Technology & Business College</h3>
                <p>Student Information System Portal</p>
            </div>
            <div class="portal-banner">STUDENT PORTAL LOGIN</div>
    """,
      unsafe_allow_html=True,
  )

  sid_in = st.text_input("Student ID")
  spass_in = st.text_input("Password", type="password")

  if st.button("Student Login", use_container_width=True):
    stud_df = pd.read_csv(STUDENT_FILE)
    match = stud_df[
        (stud_df["StudentID"] == sid_in) & (stud_df["Password"] == spass_in)
    ]
    if not match.empty:
      st.session_state["student_logged"] = sid_in
      st.success("Logged in successfully!")
      st.rerun()
    else:
      st.error("Invalid Student ID or Password")

  st.markdown("</div>", unsafe_allow_html=True)

  if "student_logged" in st.session_state:
    st.markdown("---")
    current_sid = st.session_state["student_logged"]
    stud_df = pd.read_csv(STUDENT_FILE)
    student_info = stud_df[stud_df["StudentID"] == current_sid].iloc[0]

    st.title(f"🎓 Student Portal: {student_info['FullName']}")

    tab_profile, tab_grades, tab_transcript = st.tabs([
        "Student Profile",
        "Grade Report",
        "Smart Documents & Printing",
    ])

    with tab_profile:
      col1, col2 = st.columns([1, 2])
      with col1:
        st.info(
            f"**Campus:** {student_info['Campus']}\n\n**Department:**"
            f" {student_info['Department']}\n\n**Program Level:**"
            f" {student_info['ProgramLevel']}"
            f" ({student_info.get('Modality', 'Regular')})"
        )
      with col2:
        fin_df = pd.read_csv(FINANCE_FILE)
        f_record = fin_df[fin_df["StudentID"] == current_sid]
        if not f_record.empty:
          status = f_record.iloc[0]["Status"]
          paid = f_record.iloc[0]["PaidETB"]
          total = f_record.iloc[0]["TotalFeeETB"]
          st.metric(
              label="Financial Status (ETB)",
              value=status,
              delta=f"Paid: {paid} ETB / Total: {total} ETB",
          )
        else:
          st.metric(
              label="Financial Status (ETB)", value="No Financial Record"
          )

    with tab_grades:
      st.subheader("My Course Grades")
      grades_df = pd.read_csv(GRADES_FILE)
      my_grades = grades_df[grades_df["StudentID"] == current_sid]
      if my_grades.empty:
        st.info("No approved grades available yet.")
      else:
        st.dataframe(my_grades, use_container_width=True)

    with tab_transcript:
      st.subheader(
          "Smart Multi-Level Academic Document Generation & Printing"
      )
      doc_type = st.radio(
          "Select Document Type",
          [
              "Official Academic Transcript (Multi-Level TVET)",
              "Temporary Grade Report (Tempo)",
              "Original Document Copy",
          ],
      )

      fin_df = pd.read_csv(FINANCE_FILE)
      cleared = True
      if not fin_df.empty:
        f_chk = fin_df[fin_df["StudentID"] == current_sid]
        if not f_chk.empty and f_chk.iloc[0]["Status"] != "Fully Cleared":
          cleared = False

      if not cleared and doc_type in [
          "Official Academic Transcript (Multi-Level TVET)",
          "Original Document Copy",
      ]:
        st.error(
            "⚠️ Document generation is locked pending financial clearance."
            " Please settle your tuition balance (ETB) with the finance office."
        )
      else:
        auth_code = generate_auth_code()
        st.markdown(
            f"""
                <style>
                    @media print {{
                        @page {{ size: landscape; margin: 10mm; }}
                        body {{ -webkit-print-color-adjust: exact; }}
                    }}
                    .transcript-box {{
                        border: 2px solid #111;
                        padding: 20px;
                        border-radius: 6px;
                        background-color: #ffffff;
                        color: #000;
                        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                        font-size: 11px;
                        width: 100%;
                    }}
                    .t-header {{
                        text-align: center;
                        border-bottom: 2px solid #111;
                        padding-bottom: 8px;
                        margin-bottom: 10px;
                    }}
                    .t-header h2 {{ margin: 0; font-size: 16px; font-weight: bold; letter-spacing: 0.5px; }}
                    .t-header h4 {{ margin: 3px 0; font-size: 12px; color: #333; }}
                    .t-info-table {{
                        width: 100%;
                        margin-bottom: 10px;
                        font-size: 11px;
                    }}
                    .t-info-table td {{ padding: 2px 4px; }}
                    .level-grid {{
                        display: flex;
                        flex-wrap: wrap;
                        gap: 15px;
                        justify-content: space-between;
                    }}
                    .level-card {{
                        width: 48%;
                        border: 1px solid #666;
                        padding: 8px;
                        margin-bottom: 10px;
                        border-radius: 4px;
                        background: #fafafa;
                    }}
                    .level-title {{
                        font-weight: bold;
                        background: #e2e8f0;
                        padding: 3px 6px;
                        margin-bottom: 5px;
                        font-size: 11px;
                        text-align: center;
                        border-bottom: 1px solid #ccc;
                    }}
                    .mini-table {{
                        width: 100%;
                        border-collapse: collapse;
                        font-size: 10px;
                    }}
                    .mini-table th, .mini-table td {{
                        border: 1px solid #bbb;
                        padding: 3px 5px;
                        text-align: left;
                    }}
                    .mini-table th {{ background: #f1f5f9; }}
                    .t-footer {{
                        margin-top: 15px;
                        border-top: 1px solid #111;
                        padding-top: 10px;
                        display: flex;
                        justify-content: space-between;
                        align-items: flex-end;
                        font-size: 11px;
                    }}
                </style>

                <div class="transcript-box">
                    <div class="t-header">
                        <h2>HANEK TECHNOLOGY AND BUSINESS COLLEGE</h2>
                        <h4>OFFICE OF THE REGISTRAR - {student_info['Campus'].upper()} CAMPUS</h4>
                        <div style="font-size: 12px; font-weight: bold; margin-top: 2px; text-transform: uppercase;">{doc_type}</div>
                    </div>

                    <table class="t-info-table">
                        <tr>
                            <td><b>Student Name:</b> {student_info['FullName']}</td>
                            <td><b>Student ID:</b> {current_sid}</td>
                            <td><b>Admission Year:</b> 2026</td>
                        </tr>
                        <tr>
                            <td><b>Department:</b> {student_info['Department']}</td>
                            <td><b>Program Level:</b> {student_info['ProgramLevel']} ({student_info.get('Modality', 'Regular')})</td>
                            <td><b>Medium of Instruction:</b> English</td>
                        </tr>
                    </table>

                    <div class="level-grid">
            """,
            unsafe_allow_html=True,
        )

        grades_df = pd.read_csv(GRADES_FILE)
        my_grades = grades_df[grades_df["StudentID"] == current_sid]

        levels = [
            "TVET Level I",
            "TVET Level II",
            "TVET Level III",
            "TVET Level IV",
        ]
        for lvl in levels:
          lvl_grades = my_grades[my_grades["Level"] == lvl]
          st.markdown(
              f"""
                    <div class="level-card">
                        <div class="level-title">{lvl} Modules & Assessment</div>
                        <table class="mini-table">
                            <thead>
                                <tr>
                                    <th>Code</th>
                                    <th>Module Title</th>
                                    <th>Cr.Hr</th>
                                    <th>Score</th>
                                    <th>Grade</th>
                                </tr>
                            </thead>
                            <tbody>
                """,
              unsafe_allow_html=True,
          )

          if not lvl_grades.empty:
            for _, row in lvl_grades.iterrows():
              st.markdown(
                  f"""
                        <tr>
                            <td>{row['CourseCode']}</td>
                            <td>{row['CourseName']}</td>
                            <td>{row['CreditHour']}</td>
                            <td>{row['Score']}</td>
                            <td>{row['Grade']}</td>
                        </tr>
                    """,
                  unsafe_allow_html=True,
              )
          else:
            st.markdown(
                """
                        <tr>
                            <td colspan="5" style="text-align: center; color: #777;">No modules recorded for this level.</td>
                        </tr>
                    """,
                unsafe_allow_html=True,
            )

          st.markdown(
              """
                            </tbody>
                        </table>
                    </div>
                """,
              unsafe_allow_html=True,
          )

        st.markdown(
            f"""
                    </div>

                    <div class="t-footer">
                        <div>
                            <p style="margin: 2px 0;"><b>Authentication Code:</b> <span style="color: blue; font-family: monospace;">{auth_code}</span></p>
                            <p style="margin: 2px 0; font-size: 10px; color: #555;">This document is electronically verified by Hanek Technology and Business College Registrar System. Any alteration invalidates this document.</p>
                        </div>
                        <div style="text-align: right;">
                            <p style="margin: 15px 0 2px 0;">___________________________</p>
                            <p style="margin: 0; font-weight: bold;">Registrar Office Seal & Signature</p>
                        </div>
                    </div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🖨️ Print / Save Document"):
          st.success(
              f"Document generated successfully with Authentication Code:"
              f" {auth_code}"
          )

# --- DEVELOPER FOOTER BRANDING ---
st.markdown("---")
st.markdown(
    "<p style='text-align: center; font-size: 13px; color: gray;'>Developed by"
    " <b>Ebirawi Henok Loha</b> | Contact: +251965514327 | Email:"
    " henokebirawi3@gmail.com<br>Hanek Technology and Business College ©"
    " 2026</p>",
    unsafe_allow_html=True,
)
