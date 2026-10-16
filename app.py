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
else:
  st.sidebar.info(
      "💡 Tip: Upload your college logo in the Admin Control Panel under"
      " 'System Settings & Logo'."
  )

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
    st.subheader("Office of the Registrar & Student Information System")
    st.write(
        "Welcome to the official institutional portal serving Wolaita Sodo,"
        " Basketo Laska, Boloso Bombe, and Jinka campuses. Manage student"
        " admissions, faculty records, grade approvals, financial clearance in"
        " Ethiopian Birr (ETB), and smart landscape-optimized academic"
        " document printing."
    )
  with col2:
    if os.path.exists(LOGO_FILE):
      st.image(LOGO_FILE, width=150)

  st.markdown("---")
  st.markdown("### 🏛️ Core Registrar Services")

  c1, c2, c3 = st.columns(3)
  with c1:
    st.info(
        "**📋 Student Admissions & Records**\n\nFull CRUD management for TVET"
        " Programs (Levels I–IV) across all multi-campus branches."
    )
  with c2:
    st.info(
        "**🔒 Grade Workflow & Finance**\n\nInstructor grade submissions with"
        " registrar verification and ETB tuition clearance locks."
    )
  with c3:
    st.info(
        "**🖨️ Smart Landscape Printing**\n\nOptimized multi-level TVET"
        " transcripts, temporary reports (Tempo), and original certificates"
        " with authentication codes."
    )

  st.markdown("---")
  st.markdown(
      "📌 **Please select your portal role from the sidebar dropdown menu** to"
      " proceed to Admin, Staff, or Student login."
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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Student Admission",
        "Staff Directory",
        "Grade Approvals",
        "Financial Accounts (ETB)",
        "Smart Document Printing",
        "System Settings & Logo",
        "System Logs",
    ])

    with tab1:
      st.subheader("Student Admission & Records Management")
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

        if st.form_submit_button("Admit Student"):
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
          st.success("Staff profile created successfully!")
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
          grade_val, gp = calculate_grade(row["Score"])
          final_row = pd.DataFrame([{
              "StudentID": row["StudentID"],
              "FullName": row["FullName"],
              "CourseCode": row["CourseCode"],
              "CourseName": row["CourseName"],
              "CreditHour": row["CreditHour"],
              "Score": row["Score"],
              "Grade": f"{grade_val} ({gp})",
              "Level": row.get("Level", "Level I"),
              "Semester": row["Semester"],
              "AcademicYear": "2025/2026",
          }])
          grades_df = pd.concat([grades_df, final_row], ignore_index=True)
          grades_df.to_csv(GRADES_FILE, index=False)

          pending_df = pending_df.drop(approve_id).reset_index(drop=True)
          pending_df.to_csv(PENDING_FILE, index=False)
          st.success("Grade successfully approved and posted to transcript!")
          st.rerun()

    with tab4:
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

    with tab5:
      st.subheader("Smart Landscape Academic Document Generation (Admin Office)")
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

          # Smart Landscape Multi-Level TVET Layout CSS & HTML Template
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
                            <h4>OFFICE OF THE REGISTRAR — {s_info['Campus'].upper()} CAMPUS</h4>
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
                                <td><b>Program Level:</b> {s_info['ProgramLevel']}</td>
                                <td><b>Medium of Instruction:</b> English</td>
                            </tr>
                        </table>

                        <div class="level-grid">
                """,
              unsafe_allow_html=True,
          )

          grades_df = pd.read_csv(GRADES_FILE)
          s_grades = grades_df[grades_df["StudentID"] == sel_sid]

          # Render Multi-Level Cards (Level I to IV optimization)
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
                                <p style="margin: 2px 0; font-size: 10px; color: #555;">Certified official academic document. Any alteration renders this document invalid.</p>
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

    with tab6:
      st.subheader("System Settings & College Logo Upload")
      st.markdown(
          "### Upload College Logo\nUpload your college badge/logo image"
          " (`logo.png`) directly here so it appears across the sidebar and"
          " portal headers."
      )

      uploaded_logo = st.file_uploader(
          "Choose logo image (PNG / JPG)", type=["png", "jpg", "jpeg"]
      )
      if uploaded_logo is not None:
        with open(LOGO_FILE, "wb") as f:
          f.write(uploaded_logo.getbuffer())
        st.success(
            "Logo uploaded successfully! Please refresh or reload the page to"
            " view it."
        )

      st.markdown("---")
      st.markdown("### Update Admin Credentials")
      with st.form("change_admin"):
        new_adm_user = st.text_input("New Admin Username")
        new_adm_pass = st.text_input("New Admin Password", type="password")
        if st.form_submit_button("Update Credentials"):
          pd.DataFrame(
              [{"Username": new_adm_user, "Password": new_adm_pass}]
          ).to_csv(ADMIN_FILE, index=False)
          st.success("Admin credentials updated successfully!")

    with tab7:
      st.subheader("System Logs & Database Health")
      st.write(
          f"Total Registered Students: {len(pd.read_csv(STUDENT_FILE))}"
      )
      st.write(f"Total Registered Staff: {len(pd.read_csv(STAFF_FILE))}")
      st.write(
          f"Pending Grade Approvals:"
          f" {len(pd.read_csv(PENDING_FILE))}"
      )
      st.write(f"Official Posted Grades: {len(pd.read_csv(GRADES_FILE))}")

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
        "ℹ️ Instructors can select the TVET Level, input course module codes,"
        " titles, credit hours, and numerical scores (0-100) for review and"
        " approval."
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
        "Smart Documents & Printing",
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
                            <td><b>Program Level:</b> {student_info['ProgramLevel']}</td>
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
                            <p style="margin: 2px 0; font-size: 10px; color: #555;">Certified official academic document. Any alteration renders this document invalid.</p>
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
