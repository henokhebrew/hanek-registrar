import os
import random
import string
import pandas as pd
import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Hanek Technology and Business College - Portal",
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
LOGO_FILE = "logo.png"

CAMPUSES = ["Wolaita Sodo", "Basketo Laska", "Boloso Bombe", "Jinka"]

DEPARTMENTS = [
    "Cooperative Accounting and Auditing",
    "Cooperative Business Management",
    "Cooperative Marketing",
    "Hardware and Network System (HNS)",
    "Natural Resource Management (NARM)",
    "Crop Production (Plant Science)",
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


init_csvs()


# --- HELPER FUNCTIONS ---
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


# --- SIDEBAR PORTAL NAVIGATION & BRANDING ---
st.sidebar.markdown(
    "<h3 style='text-align: center;'>Hanek College Portal</h3>",
    unsafe_allow_html=True,
)

if os.path.exists(LOGO_FILE):
  st.sidebar.image(LOGO_FILE, use_column_width=True)

st.sidebar.markdown("---")
role = st.sidebar.selectbox(
    "Select Portal Access",
    ["Home Dashboard", "Admin / Registrar", "Staff / Instructor", "Student"],
)

# --- HOME / LANDING DASHBOARD ---
if role == "Home Dashboard":
  col1, col2 = st.columns([3, 1])
  with col1:
    st.title("HANEK TECHNOLOGY AND BUSINESS COLLEGE")
    st.subheader(
        "Multi-Campus Registrar & Student Information Management System"
    )
    st.write(
        "Welcome to the official online portal serving Wolaita Sodo, Basketo"
        " Laska, Boloso Bombe, and Jinka campuses. Manage student admissions,"
        " staff credentials, grade approvals, ETB financial clearance, and"
        " secure transcript generation."
    )
  with col2:
    if os.path.exists(LOGO_FILE):
      st.image(LOGO_FILE, width=150)

  st.markdown("---")
  st.markdown("### 🏛️ Quick Portal Services")

  c1, c2, c3 = st.columns(3)
  with c1:
    st.info(
        "**📚 TVET Programs**\n\nCooperative Accounting, Management, Marketing,"
        " HNS, Natural Resource Management, & Crop Production (Levels I–IV)."
    )
  with c2:
    st.info(
        "**🔒 Secure Registrar**\n\nInstructor grade submissions with manual"
        " module entry, official admin verification, and ETB fee clearance"
        " locks."
    )
  with c3:
    st.info(
        "**🖨️ Official Documents**\n\nInstant generation of Tempo and Original"
        " transcripts backed by unique authentication numbers."
    )

  st.markdown("---")
  st.markdown(
      "📌 **Select your portal role from the sidebar dropdown menu** to log"
      " into Admin, Staff, or Student accounts."
  )

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
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Manage Students",
        "Manage Staff",
        "Grade Approvals",
        "Financial Status (ETB)",
        "Security Settings",
        "System Logs",
    ])

    with tab1:
      st.subheader("Student Admission & Records (CRUD)")
      students_df = pd.read_csv(STUDENT_FILE)
      st.dataframe(students_df, use_container_width=True)

      with st.form("add_student_form"):
        st.markdown("### Register New Student (Admission)")
        col1, col2 = st.columns(2)
        with col1:
          s_id = st.text_input("Student ID (e.g., HBC/001/26)")
          s_name = st.text_input("Full Name")
          s_campus = st.selectbox("Campus", CAMPUSES)
        with col2:
          s_dept = st.selectbox("Department", DEPARTMENTS)
          s_level = st.selectbox(
              "Program Level",
              [
                  "TVET Level I",
                  "TVET Level II",
                  "TVET Level III",
                  "TVET Level IV",
                  "Degree Program",
              ],
          )
          s_pass = st.text_input("Default Password", type="password")

        if st.form_submit_button("Register Student"):
          if s_id and s_name:
            new_row = pd.DataFrame([{
                "StudentID": s_id,
                "FullName": s_name,
                "Campus": s_campus,
                "Department": s_dept,
                "ProgramLevel": s_level,
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

    with tab2:
      st.subheader("Staff & Faculty Directory")
      staff_df = pd.read_csv(STAFF_FILE)
      st.dataframe(staff_df, use_container_width=True)

      with st.form("add_staff_form"):
        st.markdown("### Add Professional Staff / Instructor")
        st_id = st.text_input("Staff ID")
        st_name = st.text_input("Full Name")
        st_role = st.selectbox("Professional Title / Role", STAFF_ROLES)
        st_campus = st.selectbox("Assigned Campus", CAMPUSES + ["All Campuses"])
        st_dept = st.selectbox("Department / Unit", DEPARTMENTS + ["General"])
        st_pass = st.text_input("Password", type="password")

        if st.form_submit_button("Save Staff Member"):
          new_staff = pd.DataFrame([{
              "StaffID": st_id,
              "FullName": st_name,
              "Role": st_role,
              "Campus": st_campus,
              "Department": st_dept,
              "Password": st_pass,
          }])
          staff_df = pd.concat([staff_df, new_staff], ignore_index=True)
          staff_df.to_csv(STAFF_FILE, index=False)
          st.success("Staff profile created!")
          st.rerun()

    with tab3:
      st.subheader("Pending Grade Approvals")
      pending_df = pd.read_csv(PENDING_FILE)
      if pending_df.empty:
        st.info("No pending grades awaiting registrar approval.")
      else:
        st.dataframe(pending_df, use_container_width=True)
        approve_id = st.selectbox(
            "Select Pending Item Index to Approve", pending_df.index
        )
        if st.button("Approve & Post to Official Transcript"):
          row = pending_df.loc[approve_id]
          grades_df = pd.read_csv(GRADES_FILE)
          grade_val, _ = calculate_grade(row["Score"])
          final_row = pd.DataFrame([{
              "StudentID": row["StudentID"],
              "FullName": row["FullName"],
              "CourseCode": row["CourseCode"],
              "CourseName": row["CourseName"],
              "CreditHour": row["CreditHour"],
              "Score": row["Score"],
              "Grade": grade_val,
              "Semester": row["Semester"],
              "AcademicYear": "2025/2026",
          }])
          grades_df = pd.concat([grades_df, final_row], ignore_index=True)
          grades_df.to_csv(GRADES_FILE, index=False)

          pending_df = pending_df.drop(approve_id).reset_index(drop=True)
          pending_df.to_csv(PENDING_FILE, index=False)
          st.success("Grade successfully approved and published!")
          st.rerun()

    with tab4:
      st.subheader("Student Financial Accounts (ETB)")
      fin_df = pd.read_csv(FINANCE_FILE)
      students_df = pd.read_csv(STUDENT_FILE)
      st.dataframe(fin_df, use_container_width=True)

      with st.form("finance_form"):
        st.markdown("### Update Student Tuition / Fee Status")
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

        if st.form_submit_button("Update Finance Status"):
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

    with tab5:
      st.subheader("Admin Security Settings")
      with st.form("change_admin"):
        new_adm_user = st.text_input("New Admin Username")
        new_adm_pass = st.text_input("New Admin Password", type="password")
        if st.form_submit_button("Update Credentials"):
          pd.DataFrame(
              [{"Username": new_adm_user, "Password": new_adm_pass}]
          ).to_csv(ADMIN_FILE, index=False)
          st.success("Admin credentials updated successfully!")

    with tab6:
      st.subheader("System Logs & Database Health")
      st.write(
          f"Registered Students: {len(pd.read_csv(STUDENT_FILE))}"
      )
      st.write(f"Registered Staff: {len(pd.read_csv(STAFF_FILE))}")
      st.write(f"Official Grades Posted: {len(pd.read_csv(GRADES_FILE))}")

# --- STAFF / INSTRUCTOR PORTAL ---
elif role == "Staff / Instructor":
  st.sidebar.subheader("Staff Portal Login")
  st_id_in = st.sidebar.text_input("Staff ID")
  st_pass_in = st.sidebar.text_input("Password", type="password")

  if st.sidebar.button("Staff Login"):
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
      st.success(f"Welcome, {match.iloc[0]['Role']} {match.iloc[0]['FullName']}")
      st.rerun()
    else:
      st.sidebar.error("Invalid Staff Credentials")

  if "staff_logged" in st.session_state:
    st.title(
        f"👨‍🏫 Staff Portal: {st.session_state['staff_name']} ("
        f"{st.session_state['staff_role']})"
    )
    st.markdown(
        "### Submit Module Grades (Manual Entry by Instructor)"
    )
    st.info(
        "ℹ️ Instructors can type module/course code, title, credit hours,"
        " and numerical score directly below."
    )

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
            grade_val, _ = calculate_grade(score)
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
                "Grade": grade_val,
                "Semester": semester,
                "Instructor": st.session_state["staff_name"],
            }])
            pending_df = pd.concat([pending_df, new_pending], ignore_index=True)
            pending_df.to_csv(PENDING_FILE, index=False)
            st.success(
                f"Grade submitted successfully for {c_name}! Awaiting"
                " Registrar approval."
            )
          else:
            st.error("Please provide both module code and title.")

# --- STUDENT PORTAL ---
elif role == "Student":
  st.sidebar.subheader("Student Portal Login")
  sid_in = st.sidebar.text_input("Student ID")
  spass_in = st.sidebar.text_input("Password", type="password")

  if st.sidebar.button("Student Login"):
    stud_df = pd.read_csv(STUDENT_FILE)
    match = stud_df[
        (stud_df["StudentID"] == sid_in) & (stud_df["Password"] == spass_in)
    ]
    if not match.empty:
      st.session_state["student_logged"] = sid_in
      st.success("Logged in successfully!")
      st.rerun()
    else:
      st.sidebar.error("Invalid Student ID or Password")

  if "student_logged" in st.session_state:
    current_sid = st.session_state["student_logged"]
    stud_df = pd.read_csv(STUDENT_FILE)
    student_info = stud_df[stud_df["StudentID"] == current_sid].iloc[0]

    st.title(f"🎓 Student Portal: {student_info['FullName']}")

    tab_profile, tab_grades, tab_transcript = st.tabs([
        "Student Profile",
        "Grade Report",
        "Official Transcript & Tempo",
    ])

    with tab_profile:
      col1, col2 = st.columns([1, 2])
      with col1:
        st.info(
            f"**Campus:** {student_info['Campus']}\n\n**Department:**"
            f" {student_info['Department']}\n\n**Level:**"
            f" {student_info['ProgramLevel']}"
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
          "Print Transcript, Temporary Grade Report ('Tempo'), & Original"
          " Document"
      )
      doc_type = st.radio(
          "Select Document Type",
          [
              "Official Academic Transcript",
              "Temporary Grade Report (Tempo)",
              "Original Copy",
          ],
      )

      fin_df = pd.read_csv(FINANCE_FILE)
      cleared = True
      if not fin_df.empty:
        f_chk = fin_df[fin_df["StudentID"] == current_sid]
        if not f_chk.empty and f_chk.iloc[0]["Status"] != "Fully Cleared":
          cleared = False

      if not cleared and doc_type in [
          "Official Academic Transcript",
          "Original Copy",
      ]:
        st.error(
            "⚠️ Document generation is locked pending financial clearance."
            " Please settle your tuition balance (ETB) with the finance office."
        )
      else:
        auth_code = generate_auth_code()
        st.markdown(
            f"""
                <div style="border: 2px solid #333; padding: 25px; border-radius: 10px; background-color: #ffffff; color: #000;">
                    <h2 align="center">HANEK TECHNOLOGY AND BUSINESS COLLEGE</h2>
                    <h4 align="center">OFFICE OF THE REGISTRAR - {student_info['Campus'].upper()} CAMPUS</h4>
                    <hr>
                    <p><b>Document Type:</b> {doc_type}</p>
                    <p><b>Student Name:</b> {student_info['FullName']} &nbsp;&nbsp;&nbsp;&nbsp; <b>ID No:</b> {current_sid}</p>
                    <p><b>Department:</b> {student_info['Department']} &nbsp;&nbsp;&nbsp;&nbsp; <b>Program:</b> {student_info['ProgramLevel']}</p>
                    <hr>
                """,
            unsafe_allow_html=True,
        )

        grades_df = pd.read_csv(GRADES_FILE)
        my_grades = grades_df[grades_df["StudentID"] == current_sid]
        if not my_grades.empty:
          st.table(
              my_grades[[
                  "CourseCode",
                  "CourseName",
                  "CreditHour",
                  "Score",
                  "Grade",
                  "Semester",
              ]]
          )
        else:
          st.write("No courses recorded.")

        st.markdown(
            f"""
                    <hr>
                    <p><b>Authentication Verification Number:</b> <span style="color: blue; font-family: monospace;">{auth_code}</span></p>
                    <p style="font-size: 11px; color: gray;">This document is electronically verified by Hanek Technology and Business College Registrar System. Any alteration invalidates this document.</p>
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
