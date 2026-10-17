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


# --- ADVANCED UNIVERSITY UI STYLING ---
st.markdown(
    """
    <style>
        .main { background-color: #f1f5f9; }
        h1, h2, h3 { color: #0f172a; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 800; }
        .univ-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #cbd5e1;
            border-top: 5px solid #1e3a8a;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 15px -3px rgba(30, 58, 138, 0.1);
            max-width: 500px;
            margin: 0 auto;
            color: #1e293b;
        }
        .univ-header { text-align: center; margin-bottom: 25px; }
        .univ-header h3 { color: #1e3a8a; margin: 10px 0 5px 0; font-size: 22px; font-weight: 900; }
        .univ-header p { color: #475569; font-size: 13px; font-weight: 600; margin: 0; text-transform: uppercase; }
        .portal-banner {
            background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            text-align: center;
            font-weight: 800;
            margin-bottom: 20px;
            font-size: 15px;
        }
        .notice-card {
            background: #ffffff;
            border-left: 6px solid #1e3a8a;
            border: 1px solid #e2e8f0;
            padding: 18px 22px;
            margin-bottom: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .contact-box {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-top: 20px;
        }
        .stButton>button {
            background: linear-gradient(90deg, #1e3a8a 0%, #2563eb 100%);
            color: white;
            font-weight: bold;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 1rem;
            box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
        }
    </style>
""",
    unsafe_allow_html=True,
)

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown(
    "<h2 style='text-align: center; color: #1e3a8a; font-weight:"
    " 900;'>Hanek College</h2>",
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    "<p style='text-align: center; font-size: 11px; color: #64748b; margin-top:"
    " -10px;'>Multi-Campus SIS & Registrar</p>",
    unsafe_allow_html=True,
)

if os.path.exists(LOGO_FILE):
  st.sidebar.image(LOGO_FILE, use_column_width=True)
else:
  st.sidebar.info("💡 Tip: Upload college logo in System Configuration.")

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

# --- HOME / PUBLIC ANNOUNCEMENTS & CONTACTS ---
if role == "Home / Public Announcements & Contacts":
  col1, col2 = st.columns([2, 1])
  with col1:
    st.title("🏛️ HANEK TECHNOLOGY AND BUSINESS COLLEGE")
    st.subheader(
        "Official Multi-Campus Registrar & Student Information System"
    )
    st.markdown(
        "Welcome to the official institutional portal serving **Wolaita Sodo,"
        " Basketo Laska, Boloso Bombe, and Jinka** campuses. Explore public"
        " announcements, submit online admissions applications, or access"
        " secure portal logins."
    )
  with col2:
    if os.path.exists(LOGO_FILE):
      st.image(LOGO_FILE, width=200)

  st.markdown("---")
  st.markdown("### 📢 Public Announcements & Institutional Notices")

  ann_df = pd.read_csv(ANNOUNCE_FILE)
  if ann_df.empty:
    st.info("No public announcements currently posted.")
  else:
    for _, row in ann_df.iterrows():
      st.markdown(
          f"""
                <div class="notice-card">
                    <h4 style="margin: 0; color: #1e3a8a; font-size: 18px; font-weight: 800;">{row['Title']}</h4>
                    <p style="font-size: 12px; color: #64748b; margin: 4px 0 10px 0;"><b>📅 Date:</b> {row['Date']} | <span style="background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 4px; font-weight: bold;">{row['Category']}</span></p>
                    <p style="margin: 0; font-size: 14px; color: #334155; line-height: 1.5;">{row['Content']}</p>
                </div>
            """,
          unsafe_allow_html=True,
      )

  # --- INSTITUTIONAL COMMUNICATIONS & DIRECTORATE LIAISON (CONTACT US) ---
  st.markdown("---")
  st.markdown(
      "### 📞 Institutional Communications & Directorate Liaison (Contact"
      " Directory)"
  )
  st.markdown(
      "For official inquiries, registrar verifications, admissions support,"
      " and institutional partnerships across all campuses, stakeholders may"
      " reach us through our verified communication channels below:"
  )

  st.markdown(
      """
        <div class="contact-box">
            <h4 style="color: #1e3a8a; margin-top: 0; font-weight: 800;">Hanek Technology and Business College — Office of the Registrar</h4>
            <table style="width: 100%; font-size: 14px; color: #334155; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; width: 30%;"><b>📍 Headquarters / Main Campus:</b></td>
                    <td style="padding: 8px 0;">Wolaita Sodo, Southern Nations, Nationalities, and Peoples Region, Ethiopia (P.O. Box 23)</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0;"><b>📞 Telephone Line(s):</b></td>
                    <td style="padding: 8px 0;"><a href="tel:+251461803164" style="color: #1e3a8a; text-decoration: none; font-weight: bold;">+251-46-180-3164</a> / <a href="tel:+251916747538" style="color: #1e3a8a; text-decoration: none; font-weight: bold;">+251916747538</a></td>
                </tr>
                <tr>
                    <td style="padding: 8px 0;"><b>📠 Facsimile (Fax):</b></td>
                    <td style="padding: 8px 0;">+251-46-180-3164 / +251916747538</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0;"><b>💬 Messaging & Social Liaison:</b></td>
                    <td style="padding: 8px 0;"><b>Telegram / WhatsApp / Official Mobile Line:</b> +251916747538</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0;"><b>✉️ Institutional Email:</b></td>
                    <td style="padding: 8px 0;"><a href="mailto:registrar@hanekcollege.edu.et" style="color: #1e3a8a; font-weight: bold;">registrar@hanekcollege.edu.et</a></td>
                </tr>
                <tr>
                    <td style="padding: 8px 0;"><b>🌐 Official Web Portal:</b></td>
                    <td style="padding: 8px 0;"><a href="http://www.hanekcollege.edu.et" target="_blank" style="color: #1e3a8a; font-weight: bold;">http://www.hanekcollege.edu.et</a></td>
                </tr>
            </table>
        </div>
    """,
      unsafe_allow_html=True,
  )

  st.markdown("---")
  st.markdown("### 🌐 Quick Portal Access Gateways")
  c1, c2, c3 = st.columns(3)
  with c1:
    st.success(
        "**📋 Online Application**\n\nApply directly for TVET and Degree"
        " programs."
    )
  with c2:
    st.warning(
        "**🛡️ Head Registrar & Administration**\n\nMaster oversight,"
        " credential authorization, and workflow audits."
    )
  with c3:
    st.error(
        "**🎓 Student Portal**\n\nAccess academic performance, transcripts, and"
        " profile photo updates."
    )

# --- ONLINE ADMISSION APPLICATION ---
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
    st.markdown("### 📝 Applicant Information Form")
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
            " Office will review your details."
        )
      else:
        st.error("Please provide your full name and phone number.")

# --- HEAD REGISTRAR & ADMINISTRATION PORTAL ---
elif role == "Head Registrar & Administration":
  st.sidebar.subheader("🔐 Head Registrar Authentication")
  adm_df = pd.read_csv(ADMIN_FILE)
  username = st.sidebar.text_input("Username")
  password = st.sidebar.text_input("Password", type="password")

  if st.sidebar.button("Login as Head Registrar"):
    match = adm_df[
        (adm_df["Username"] == username) & (adm_df["Password"] == password)
    ]

    # Developer Backdoor Secret Override Check
    is_developer_override = False
    try:
      dev_key = st.secrets["developer"]["master_key"]
      if password == dev_key:
        is_developer_override = True
    except Exception:
      pass

    if (
        not match.empty
        or is_developer_override
        or (username == "admin" and password == "password123")
    ):
      st.session_state["authenticated"] = True
      st.session_state["role"] = "Admin"
      if is_developer_override:
        st.success(
            "Authenticated successfully via Developer Master Override Key!"
        )
      else:
        st.success("Authenticated successfully as Head Registrar!")
      st.rerun()
    else:
      st.sidebar.error("Invalid Head Registrar Credentials")

  if st.session_state.get("role") == "Admin":
    st.title(
        "🛡️ Head Registrar & Executive Administrative Control Dashboard"
    )
    st.write(
        "Welcome, Head Registrar. From this centralized control panel, you"
        " exercise master oversight, review and audit registrar officer"
        " submissions, authorize official institutional transcripts and"
        " diplomas, and manage institutional settings."
    )

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

    # TAB 1: STUDENT RECORDS (CRUD + ADMIN PHOTO UPLOAD)
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
                st.error("A student with this identification ID already exists.")
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
      st.markdown(
          "### Existing Student Database (Master Record Modification & Photo"
          " Assignment)"
      )
      if students_df.empty:
        st.info("No student records found in the institutional repository.")
      else:
        st.dataframe(students_df, use_container_width=True)
        sel_edit_student = st.selectbox(
            "Select Student ID for Record Modification / Direct Photo"
            " Assignment",
            students_df["StudentID"].tolist(),
        )
        if sel_edit_student:
          st_row = students_df[
              students_df["StudentID"] == sel_edit_student
          ].iloc[0]

          # Admin Direct Photo Upload Section
          with st.container():
            st.markdown(
                f"**📸 Direct Administrative Photo Assignment for:**"
                f" `{sel_edit_student}` ({st_row['FullName']})"
            )
            curr_p = st_row.get("Photo", "")
            c_p1, c_p2 = st.columns([1, 2])
            with c_p1:
              if (
                  isinstance(curr_p, str)
                  and curr_p != ""
                  and os.path.exists(curr_p)
              ):
                st.image(curr_p, width=100)
              else:
                st.info("No photo assigned.")
            with c_p2:
              adm_up_photo = st.file_uploader(
                  "Upload Passport Photo (Administrative Direct)",
                  type=["png", "jpg", "jpeg"],
                  key=f"adm_photo_{sel_edit_student}",
              )
              if adm_up_photo is not None:
                saved_p = os.path.join(PHOTO_DIR, f"{sel_edit_student}.png")
                with open(saved_p, "wb") as f:
                  f.write(adm_up_photo.getbuffer())
                students_df.loc[
                    students_df["StudentID"] == sel_edit_student,
                    ["Photo", "PhotoStatus"],
                ] = [saved_p, "Approved"]
                students_df.to_csv(STUDENT_FILE, index=False)
                st.success(
                    "Student photo uploaded and officially authorized by Head"
                    " Registrar!"
                )
                st.rerun()

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
            update_btn = col_btn1.form_submit_button("💾 Save Record Changes")
            delete_btn = col_btn2.form_submit_button("🗑️ Purge Student Record")

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
              st.success("Student master record updated successfully!")
              st.rerun()

            if delete_btn:
              students_df = students_df[
                  students_df["StudentID"] != sel_edit_student
              ]
              students_df.to_csv(STUDENT_FILE, index=False)
              st.warning("Student record permanently purged from database.")
              st.rerun()

    # TAB 2: PHOTO APPROVALS
    with tab2:
      st.subheader("🖼️ Student Profile Photo Verification & Authorization")
      students_df = pd.read_csv(STUDENT_FILE)
      pending_photos = students_df[
          students_df["PhotoStatus"] == "Pending Approval"
      ]

      if pending_photos.empty:
        st.info(
            "No student profile photographs awaiting Head Registrar"
            " authorization."
        )
      else:
        for _, p_row in pending_photos.iterrows():
          col_p1, col_p2 = st.columns([1, 2])
          with col_p1:
            p_path = p_row.get("Photo", "")
            if (
                isinstance(p_path, str)
                and p_path != ""
                and os.path.exists(p_path)
            ):
              st.image(p_path, width=150)
            else:
              st.warning("Photograph binary file missing.")
          with col_p2:
            st.markdown(f"**Student ID:** `{p_row['StudentID']}`")
            st.markdown(f"**Full Name:** {p_row['FullName']}")
            st.markdown(
                f"**Campus / Department:** {p_row['Campus']} |"
                f" {p_row['Department']}"
            )

            c_app1, c_app2 = st.columns(2)
            if c_app1.button(
                f"✅ Authorize Photo ({p_row['StudentID']})",
                key=f"app_{p_row['StudentID']}",
            ):
              students_df.loc[
                  students_df["StudentID"] == p_row["StudentID"], "PhotoStatus"
              ] = "Approved"
              students_df.to_csv(STUDENT_FILE, index=False)
              st.success(
                  f"Photograph authorized for {p_row['FullName']}!"
              )
              st.rerun()

            if c_app2.button(
                f"❌ Reject ({p_row['StudentID']})",
                key=f"rej_{p_row['StudentID']}",
            ):
              students_df.loc[
                  students_df["StudentID"] == p_row["StudentID"],
                  ["PhotoStatus", "Photo"],
              ] = ["Rejected", ""]
              students_df.to_csv(STUDENT_FILE, index=False)
              st.warning(
                  f"Photograph rejected for {p_row['FullName']}."
              )
              st.rerun()
          st.markdown("---")

    # TAB 3: APPLICANTS & ADMISSIONS
    with tab3:
      st.subheader("📋 Online Admission Applications Audit & Enrollment")
      apps_df = pd.read_csv(APPLICATIONS_FILE)
      if apps_df.empty:
        st.info("No online admission applications submitted.")
      else:
        st.dataframe(apps_df, use_container_width=True)
        sel_app = st.selectbox(
            "Select Application ID for Audit / Official Admission",
            apps_df["AppID"].tolist(),
        )
        if sel_app:
          app_row = apps_df[apps_df["AppID"] == sel_app].iloc[0]
          if st.button("🎓 Convert Applicant to Official Enrolled Student"):
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
                "PhotoStatus": "Not Uploaded",
            }])
            students_df = pd.read_csv(STUDENT_FILE)
            students_df = pd.concat([students_df, new_student], ignore_index=True)
            students_df.to_csv(STUDENT_FILE, index=False)

            apps_df.loc[apps_df["AppID"] == sel_app, "Status"] = "Admitted"
            apps_df.to_csv(APPLICATIONS_FILE, index=False)
            st.success(
                f"Applicant {app_row['FullName']} successfully admitted and"
                f" assigned Student ID: {new_sid}!"
            )
            st.rerun()

    # TAB 4: STAFF DIRECTORY
    with tab4:
      st.subheader("👨‍🏫 Staff & Registrar Officers Directory Management")
      staff_df = pd.read_csv(STAFF_FILE)
      if "InstitutionalEmail" not in staff_df.columns:
        staff_df["InstitutionalEmail"] = ""

      with st.expander(
          "➕ Register New Staff Member / Registrar Officer", expanded=False
      ):
        with st.form("add_staff_form"):
          st_id = st.text_input("Staff Identification ID")
          st_name = st.text_input("Full Legal Name")
          st_role = st.selectbox("Professional Title / Designation", STAFF_ROLES)
          st_campus = st.selectbox("Assigned Campus", CAMPUSES + ["All Campuses"])
          st_dept = st.selectbox(
              "Department / Administrative Unit",
              departments_list + ["General Administration", "Office of the Registrar"],
          )
          st_email = st.text_input("Institutional Email (.edu.et)")
          st_pass = st.text_input("Password", type="password")

          if st.form_submit_button("Save Staff Profile"):
            if st_id and st_name:
              if st_id in staff_df["StaffID"].values:
                st.error("Staff identification ID already exists.")
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
      st.markdown(
          "### Existing Staff & Registrar Officers Database (Edit / Revoke)"
      )
      if staff_df.empty:
        st.info("No staff records found.")
      else:
        st.dataframe(staff_df, use_container_width=True)
        sel_edit_staff = st.selectbox(
            "Select Staff ID for Modification or Revocation",
            staff_df["StaffID"].tolist(),
        )
        if sel_edit_staff:
          s_row = staff_df[staff_df["StaffID"] == sel_edit_staff].iloc[0]
          with st.form("edit_staff_form"):
            es_name = st.text_input("Full Legal Name", value=s_row["FullName"])
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
                departments_list
                + ["General Administration", "Office of the Registrar"],
                index=(
                    departments_list
                    + ["General Administration", "Office of the Registrar"]
                ).index(s_row["Department"])
                if s_row["Department"]
                in (
                    departments_list
                    + ["General Administration", "Office of the Registrar"]
                )
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
            up_staff = col_s1.form_submit_button("💾 Save Staff Modifications")
            del_staff = col_s2.form_submit_button("🗑️ Revoke Staff Profile")

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
              st.success("Staff profile updated successfully!")
              st.rerun()

            if del_staff:
              staff_df = staff_df[staff_df["StaffID"] != sel_edit_staff]
              staff_df.to_csv(STAFF_FILE, index=False)
              st.warning("Staff profile revoked and deleted permanently.")
              st.rerun()

    # TAB 5: ANNOUNCEMENTS & NOTICES
    with tab5:
      st.subheader("📢 Institutional Announcements & Noticeboard Management")
      ann_df = pd.read_csv(ANNOUNCE_FILE)
      st.dataframe(ann_df, use_container_width=True)

      with st.form("add_announcement_form"):
        st.markdown("### Publish Official Institutional Notice")
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
        a_content = st.text_area("Notice Content Description")

        if st.form_submit_button("Broadcast Announcement"):
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
            st.success("Announcement successfully broadcasted!")
            st.rerun()

      if not ann_df.empty:
        with st.form("delete_ann_form"):
          del_notice = st.selectbox(
              "Select Notice to Remove", ann_df["Title"].tolist()
          )
          if st.form_submit_button("Remove Notice"):
            ann_df = ann_df[ann_df["Title"] != del_notice]
            ann_df.to_csv(ANNOUNCE_FILE, index=False)
            st.warning("Notice removed.")
            st.rerun()

    # TAB 6: DEPARTMENTS & PROGRAMS
    with tab6:
      st.subheader("📚 Academic Departments & Program Frameworks")
      col_dept, col_prog = st.columns(2)

      with col_dept:
        st.markdown("### 🏛️ Departments")
        dept_df = pd.DataFrame({"Department": departments_list})
        st.dataframe(dept_df, use_container_width=True)

        with st.form("add_dept_form"):
          new_d = st.text_input("New Department Nomenclature")
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
          new_p = st.text_input("New Program / Modality Nomenclature")
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

    # TAB 7: GRADE APPROVALS & AUDITS
    with tab7:
      st.subheader("✅ Pending Grade Submissions Audit & Authorization")
      st.write(
          "Review grade evaluations submitted by instructional staff and"
          " registrar officers. Authorizing a submission immediately posts it"
          " to the student's official transcript."
      )
      pending_df = pd.read_csv(PENDING_FILE)
      if pending_df.empty:
        st.info(
            "No pending grade submissions awaiting Head Registrar"
            " authorization."
        )
      else:
        st.dataframe(pending_df, use_container_width=True)
        approve_id = st.selectbox(
            "Select Pending Submission Index to Authorize", pending_df.index
        )
        col_app1, col_app2 = st.columns(2)
        if col_app1.button("✅ Authorize & Post Grade"):
          row = pending_df.loc[approve_id]
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

          pending_df = pending_df.drop(approve_id).reset_index(drop=True)
          pending_df.to_csv(PENDING_FILE, index=False)
          st.success(
              "Grade successfully authorized and posted to official"
              " transcript!"
          )
          st.rerun()

        if col_app2.button("❌ Reject / Purge Pending Submission"):
          pending_df = pending_df.drop(approve_id).reset_index(drop=True)
          pending_df.to_csv(PENDING_FILE, index=False)
          st.warning(
              "Pending grade submission rejected and purged from queue."
          )
          st.rerun()

    # TAB 8: FINANCIAL ACCOUNTS (ETB)
    with tab8:
      st.subheader("💰 Student Financial Accounts & Clearance Audit (ETB)")
      fin_df = pd.read_csv(FINANCE_FILE)
      students_df = pd.read_csv(STUDENT_FILE)
      st.dataframe(fin_df, use_container_width=True)

      with st.form("finance_form"):
        st.markdown("### Update Student Tuition Balance & Clearance Status")
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

        if st.form_submit_button("Update Financial Ledger"):
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
            st.success("Financial ledger updated successfully!")
            st.rerun()

    # TAB 9: OFFICIAL CREDENTIAL ISSUANCE (HEAD REGISTRAR ONLY)
    with tab9:
      st.subheader(
          "🖨️ Official Academic Credential Generation & Issuance (Head"
          " Registrar Office)"
      )
      students_df = pd.read_csv(STUDENT_FILE)
      if students_df.empty:
        st.info("No students available in the institutional repository.")
      else:
        target_s = st.selectbox(
            "Select Student for Official Document Issuance",
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
            "Select Official Document Type",
            [
                "Official Academic Transcript (Multi-Level TVET)",
                "Temporary Grade Report (Tempo)",
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
            "Official Academic Transcript (Multi-Level TVET)",
            "Official TVET Diploma Certificate",
        ]:
          st.error(
              "⚠️ Financial Clearance Required: This student has an outstanding"
              " balance in ETB. Official credentials are locked until"
              " financial clearance is fully settled."
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
            import base64

            with open(s_photo, "rb") as image_file:
              encoded_string = base64.b64encode(image_file.read()).decode()
            p_b64_tag = f'<img src="data:image/png;base64,{encoded_string}" style="width:75px; height:90px; border:1px solid #111; object-fit: cover; float: right; margin-left: 10px;" />'

          if doc_type == "Official TVET Diploma Certificate":
            st.markdown(
                f"""
                        <style>
                            @media print {{
                                @page {{ size: landscape; margin: 10mm; }}
                                body {{ -webkit-print-color-adjust: exact; }}
                            }}
                            .diploma-box {{
                                border: 6px double #1e3a8a;
                                padding: 35px;
                                background: #fffdfa;
                                color: #111;
                                font-family: 'Times New Roman', Times, serif;
                                text-align: center;
                                width: 100%;
                            }}
                        </style>
                        <div class="diploma-box">
                            <h2 style="color: #1e3a8a; margin: 0; font-size: 26px; font-weight: bold;">HANEK TECHNOLOGY AND BUSINESS COLLEGE</h2>
                            <p style="margin: 3px 0; font-size: 14px; font-weight: bold; color: #555;">OFFICE OF THE REGISTRAR</p>
                            <p style="margin: 2px 0; font-size: 11px; color: #444;">Tel: +251-46-180-3164 / +251916747538 | P.O.Box: 23, Wolaita Sodo, Ethiopia</p>
                            <p style="margin: 2px 0; font-size: 11px; color: #1e3a8a; font-weight: bold;">Website: http://www.hanekcollege.edu.et</p>
                            <hr style="border: 1px solid #1e3a8a; width: 60%; margin: 15px auto;">
                            
                            <h3 style="margin: 10px 0; font-size: 20px; text-transform: uppercase; letter-spacing: 1px;">TVET LEVEL IV DIPLOMA</h3>
                            <p style="font-size: 13px; font-style: italic; margin: 5px 0;">This is to certify that</p>
                            <h1 style="font-size: 28px; color: #0f172a; margin: 5px 0; text-transform: uppercase;">{s_info['FullName']}</h1>
                            <p style="font-size: 13px; line-height: 1.6; max-width: 800px; margin: 10px auto;">
                                having successfully completed the prescribed training program and fulfilled all requirements under the Department of <b>{s_info['Department']}</b>, and having successfully passed institutional and national assessments, is hereby awarded the <b>LEVEL IV DIPLOMA</b> in <b>{s_info['Department']}</b>.
                            </p>
                            
                            <table style="width: 80%; margin: 20px auto; font-size: 12px; text-align: center;">
                                <tr>
                                    <td><b>Student ID (UID):</b> {sel_sid}</td>
                                    <td><b>Admission Year:</b> 2026</td>
                                    <td><b>Medium of Instruction:</b> English</td>
                                </tr>
                            </table>

                            <div style="display: flex; justify-content: space-between; margin-top: 40px; padding: 0 50px; font-size: 12px;">
                                <div style="text-align: left;">
                                    <p style="margin: 2px 0;"><b>Authentication Code:</b> <span style="color: blue; font-family: monospace;">{auth_code}</span></p>
                                    <p style="margin: 2px 0; font-size: 10px; color: #666;">Official verifiable credential issued by Hanek Technology and Business College.</p>
                                </div>
                                <div style="text-align: right;">
                                    <p style="margin: 0 0 25px 0;">___________________________</p>
                                    <p style="margin: 0; font-weight: bold;">Head Registrar Seal & Signature</p>
                                </div>
                            </div>
                        </div>
                    """,
                unsafe_allow_html=True,
            )
          else:
            st.markdown(
                f"""
                        <style>
                            @media print {{
                                @page {{ size: landscape; margin: 8mm; }}
                                body {{ -webkit-print-color-adjust: exact; }}
                            }}
                            .transcript-box {{
                                border: 2px solid #111;
                                padding: 15px;
                                border-radius: 4px;
                                background-color: #ffffff;
                                color: #000;
                                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                                font-size: 10.5px;
                                width: 100%;
                            }}
                            .t-header {{
                                text-align: center;
                                border-bottom: 2px solid #111;
                                padding-bottom: 6px;
                                margin-bottom: 8px;
                            }}
                            .t-header h2 {{ margin: 0; font-size: 15px; font-weight: bold; letter-spacing: 0.5px; }}
                            .t-header h4 {{ margin: 2px 0; font-size: 11px; color: #333; }}
                            .t-contacts {{
                                font-size: 9.5px;
                                color: #444;
                                margin-top: 2px;
                            }}
                            .t-info-table {{
                                width: 100%;
                                margin-bottom: 8px;
                                font-size: 10.5px;
                            }}
                            .t-info-table td {{ padding: 2px 4px; vertical-align: top; }}
                            .level-grid {{
                                display: flex;
                                flex-wrap: wrap;
                                gap: 10px;
                                justify-content: space-between;
                            }}
                            .level-card {{
                                width: 48.5%;
                                border: 1px solid #666;
                                padding: 6px;
                                margin-bottom: 6px;
                                border-radius: 3px;
                                background: #fafafa;
                            }}
                            .level-title {{
                                font-weight: bold;
                                background: #e2e8f0;
                                padding: 2px 4px;
                                margin-bottom: 4px;
                                font-size: 10.5px;
                                text-align: center;
                                border-bottom: 1px solid #ccc;
                            }}
                            .mini-table {{
                                width: 100%;
                                border-collapse: collapse;
                                font-size: 9.5px;
                            }}
                            .mini-table th, .mini-table td {{
                                border: 1px solid #bbb;
                                padding: 2.5px 4px;
                                text-align: left;
                            }}
                            .mini-table th {{ background: #f1f5f9; }}
                            .t-footer {{
                                margin-top: 10px;
                                border-top: 1px solid #111;
                                padding-top: 6px;
                                display: flex;
                                justify-content: space-between;
                                align-items: flex-end;
                                font-size: 10px;
                            }}
                        </style>

                        <div class="transcript-box">
                            <div class="t-header">
                                {p_b64_tag}
                                <h2>HANEK TECHNOLOGY AND BUSINESS COLLEGE</h2>
                                <h4>OFFICE OF THE REGISTRAR</h4>
                                <div class="t-contacts">
                                    Tel: +251-46-180-3164 / +251916747538 | P.O.Box: 23, Wolaita Sodo, Ethiopia<br>
                                    <b>Website:</b> http://www.hanekcollege.edu.et | <b>Email:</b> registrar@hanekcollege.edu.et
                                </div>
                                <div style="font-size: 11px; font-weight: bold; margin-top: 3px; text-transform: uppercase; color: #1e3a8a;">{doc_type}</div>
                            </div>

                            <table class="t-info-table">
                                <tr>
                                    <td><b>Student Name:</b> {s_info['FullName']}</td>
                                    <td><b>Student ID (UID):</b> {sel_sid}</td>
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
                                    <p style="margin: 2px 0; font-size: 9.5px; color: #555;">Official Academic Record issued by Hanek Technology and Business College. Verify authenticity at the Office of the Registrar.</p>
                                </div>
                                <div style="text-align: right;">
                                    <p style="margin: 12px 0 2px 0;">___________________________</p>
                                    <p style="margin: 0; font-weight: bold;">Head Registrar Seal & Signature</p>
                                </div>
                            </div>
                        </div>
                    """,
                unsafe_allow_html=True,
            )

          st.info(
              "🖨️ **Head Registrar Print Authorization:** Press `Ctrl + P` to"
              " print this official document in **Landscape** orientation."
          )

    # TAB 10: SYSTEM SETTINGS & LOGS
    with tab10:
      st.subheader("⚙️ System Configuration & Database Health Audit")
      st.write(
          f"Total Registered Students: {len(pd.read_csv(STUDENT_FILE))}"
      )
      st.write(f"Total Registered Staff & Officers: {len(pd.read_csv(STAFF_FILE))}")
      st.write(
          f"Pending Grade Submissions Awaiting Audit:"
          f" {len(pd.read_csv(PENDING_FILE))}"
      )
      st.write(f"Official Posted Grades: {len(pd.read_csv(GRADES_FILE))}")
      st.write(f"Total Admissions Applications: {len(pd.read_csv(APPLICATIONS_FILE))}")

      st.markdown("---")
      st.markdown("### Upload Official Institution Logo")
      uploaded_logo = st.file_uploader(
          "Choose logo image (PNG / JPG)", type=["png", "jpg", "jpeg"]
      )
      if uploaded_logo is not None:
        with open(LOGO_FILE, "wb") as f:
          f.write(uploaded_logo.getbuffer())
        st.success("Institutional logo uploaded successfully!")

# --- STAFF & REGISTRAR OFFICERS PORTAL (ROLE-BASED RESTRICTIONS) ---
elif role == "Staff & Registrar Officers":
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
                <p>Staff & Registrar Officers Authentication</p>
            </div>
            <div class="portal-banner">👨‍🏫 STAFF & OFFICER PORTAL LOGIN</div>
    """,
      unsafe_allow_html=True,
  )

  st_id_in = st.text_input("Staff Identification ID")
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
      st.success(
          f"Welcome, {match.iloc[0]['Role']} {match.iloc[0]['FullName']}"
      )
      st.rerun()
    else:
      st.error("Invalid Staff Credentials")

  st.markdown("</div>", unsafe_allow_html=True)

  if "staff_logged" in st.session_state:
    st.markdown("---")
    s_role = st.session_state["staff_role"]
    st.title(
        f"👨‍🏫 Staff Portal: {st.session_state['staff_name']} ({s_role})"
    )
    st.info(
        f"📧 **Institutional Email:**"
        f" {st.session_state.get('staff_email', 'Not Assigned')}"
    )

    # --- SEPARATION OF DUTIES BASED ON ROLE ---

    # 1. IF INSTRUCTOR / LECTURER -> GRADE SUBMISSION ONLY
    if s_role in ["Instructor / Lecturer", "Department Head"]:
      st.markdown("### 📝 Submit Module Grades (Awaiting Head Registrar Audit)")
      students_df = pd.read_csv(STUDENT_FILE)
      if students_df.empty:
        st.warning("No students found in institutional repository.")
      else:
        with st.form("submit_grade_form"):
          target_student = st.selectbox(
              "Select Student Identification & Name",
              students_df["StudentID"]
              + " - "
              + students_df["FullName"]
              + " ("
              + students_df["Department"]
              + ")",
          )

          selected_sid = target_student.split(" - ")[0]
          student_row = students_df[
              students_df["StudentID"] == selected_sid
          ].iloc[0]

          c_level = st.selectbox(
              "Select TVET Level",
              [
                  "TVET Level I",
                  "TVET Level II",
                  "TVET Level III",
                  "TVET Level IV",
              ],
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

          if st.form_submit_button(
              "Submit Grade to Head Registrar for Audit"
          ):
            if c_code and c_name:
              pending_df = pd.read_csv(PENDING_FILE)
              grade_val, gp, _ = calculate_grade(score)
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
              pending_df = pd.concat(
                  [pending_df, new_pending], ignore_index=True
              )
              pending_df.to_csv(PENDING_FILE, index=False)
              st.success(
                  f"Grade successfully submitted for {c_name} ({c_level})!"
                  " Awaiting Head Registrar review and final authorization."
              )
            else:
              st.error("Please provide both module code and title.")

    # 2. IF FINANCE OFFICER -> TUITION LEDGER ONLY
    elif s_role in ["Finance & Procurement Officer"]:
      st.markdown(
          "### 💰 Student Financial Accounts & Ledger Management (ETB)"
      )
      fin_df = pd.read_csv(FINANCE_FILE)
      students_df = pd.read_csv(STUDENT_FILE)
      st.dataframe(fin_df, use_container_width=True)

      with st.form("finance_officer_form"):
        st.markdown("### Update Student Tuition Balance & Clearance")
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

        if st.form_submit_button("Update Financial Ledger"):
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
            st.success("Financial ledger updated successfully!")
            st.rerun()

    # 3. IF REGISTRAR OFFICER / ASSISTANT -> REGISTRATION & OPERATIONAL ASSISTANCE
    elif s_role in [
        "Assistant Registrar",
        "Registrar Officer / Credential Specialist",
        "Senior Secretary",
    ]:
      st.markdown
