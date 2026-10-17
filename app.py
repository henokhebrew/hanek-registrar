import base64
import os
import random
import string
import html
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ============================================================
# HANEK TECHNOLOGY AND BUSINESS COLLEGE
# MULTI-CAMPUS STUDENT INFORMATION & REGISTRAR SYSTEM
# ============================================================

st.set_page_config(
    page_title="Hanek Technology and Business College | Registrar SIS",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- FILES & DIRECTORIES --------------------

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

CAMPUSES = [
    "Wolaita Sodo",
    "Basketo Laska",
    "Boloso Bombe",
    "Jinka",
]

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


# -------------------- CSV INITIALIZATION --------------------

def ensure_csv(filename, columns):
    if not os.path.exists(filename):
        pd.DataFrame(columns=columns).to_csv(filename, index=False)
        return

    try:
        df = pd.read_csv(filename)
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        df = pd.DataFrame()

    changed = False

    for column in columns:
        if column not in df.columns:
            df[column] = ""
            changed = True

    if changed or len(df.columns) == 0:
        for column in columns:
            if column not in df.columns:
                df[column] = ""
        df.to_csv(filename, index=False)


def init_csvs():
    ensure_csv(
        STUDENT_FILE,
        [
            "StudentID", "FullName", "Campus", "Department",
            "ProgramLevel", "Modality", "Year", "Password",
            "Photo", "PhotoStatus",
        ],
    )

    ensure_csv(
        GRADES_FILE,
        [
            "StudentID", "FullName", "CourseCode", "CourseName",
            "CreditHour", "Score", "Grade", "Level",
            "Semester", "AcademicYear",
        ],
    )

    ensure_csv(
        PENDING_FILE,
        [
            "PendingID", "StudentID", "FullName", "CourseCode",
            "CourseName", "CreditHour", "Score", "Grade",
            "Level", "Semester", "Instructor",
        ],
    )

    ensure_csv(
        STAFF_FILE,
        [
            "StaffID", "FullName", "Role", "Campus", "Department",
            "InstitutionalEmail", "Password",
        ],
    )

    ensure_csv(
        ADMIN_FILE,
        ["Username", "Password"],
    )

    admin_df = pd.read_csv(ADMIN_FILE)

    if "Username" not in admin_df.columns:
        admin_df = pd.DataFrame(columns=["Username", "Password"])

    if "Password" not in admin_df.columns:
        admin_df["Password"] = ""

    if admin_df.empty:
        admin_df = pd.DataFrame(
            [{"Username": "admin.hanek", "Password": "He,Ma&Eb!3"}]
        )
        admin_df.to_csv(ADMIN_FILE, index=False)
    elif "admin.hanek" not in admin_df["Username"].astype(str).values:
        admin_df = pd.concat(
            [
                admin_df,
                pd.DataFrame(
                    [{"Username": "admin.hanek", "Password": "He,Ma&Eb!3"}]
                ),
            ],
            ignore_index=True,
        )
        admin_df.to_csv(ADMIN_FILE, index=False)

    ensure_csv(
        FINANCE_FILE,
        ["StudentID", "TotalFeeETB", "PaidETB", "Status", "LastUpdated"],
    )

    ensure_csv(DEPT_FILE, ["Department"])
    ensure_csv(PROG_FILE, ["Program"])

    if pd.read_csv(DEPT_FILE).empty:
        pd.DataFrame({"Department": DEFAULT_DEPARTMENTS}).to_csv(
            DEPT_FILE, index=False
        )

    if pd.read_csv(PROG_FILE).empty:
        pd.DataFrame({"Program": DEFAULT_PROGRAMS}).to_csv(
            PROG_FILE, index=False
        )

    ensure_csv(
        ANNOUNCE_FILE,
        ["NoticeID", "Title", "Date", "Category", "Content"],
    )

    ensure_csv(
        APPLICATIONS_FILE,
        [
            "AppID", "FullName", "Phone", "Campus", "Department",
            "ProgramLevel", "Modality", "Status", "DateSubmitted",
        ],
    )


init_csvs()


# -------------------- HELPERS --------------------

def read_csv(filename):
    try:
        return pd.read_csv(filename).fillna("")
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError):
        return pd.DataFrame()


def save_csv(df, filename):
    df.to_csv(filename, index=False)


def get_departments():
    df = read_csv(DEPT_FILE)
    if "Department" in df.columns and not df.empty:
        values = df["Department"].astype(str).tolist()
        values = [v for v in values if v.strip()]
        return values or DEFAULT_DEPARTMENTS
    return DEFAULT_DEPARTMENTS


def get_programs():
    df = read_csv(PROG_FILE)
    if "Program" in df.columns and not df.empty:
        values = df["Program"].astype(str).tolist()
        values = [v for v in values if v.strip()]
        return values or DEFAULT_PROGRAMS
    return DEFAULT_PROGRAMS


def safe_text(value):
    if pd.isna(value):
        return ""
    return html.escape(str(value))


def generate_auth_code():
    letters = "".join(random.choices(string.ascii_uppercase, k=3))
    digits = "".join(random.choices(string.digits, k=5))
    return f"HBC-AUTH-{letters}-{digits}"


def calculate_grade(score):
    score = float(score)

    if score >= 90:
        return "A+", 4.0, 12.0
    if score >= 85:
        return "A", 4.0, 12.0
    if score >= 80:
        return "A-", 3.75, 11.25
    if score >= 75:
        return "B+", 3.25, 9.75
    if score >= 70:
        return "B", 3.0, 9.0
    if score >= 65:
        return "B-", 2.75, 8.25
    if score >= 60:
        return "C+", 2.5, 7.5
    if score >= 50:
        return "C", 2.0, 6.0
    if score >= 40:
        return "D", 1.0, 3.0
    return "F", 0.0, 0.0


def add_footer():
    st.markdown(
        """
        <div class="hanek-footer">
            <div class="footer-eyebrow">INSTITUTIONAL DIGITAL SYSTEM</div>
            <p>Developed by <strong>Ebirawi Henok Loha</strong></p>
            <p>
                📱 Phone: <strong>+251965514327</strong>
                &nbsp; | &nbsp;
                ✉️ Email: <strong>henokebirawi3@gmail.com</strong>
            </p>
            <div class="footer-subtitle">
                Hanek Technology and Business College<br>
                Multi-Campus Registrar &amp; SIS © 2026
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def html_document(markup, height=950):
    """Render complete HTML documents instead of exposing tags as text."""
    components.html(
        markup,
        height=height,
        scrolling=True,
    )


# -------------------- UI STYLING --------------------

st.markdown(
    """
    <style>
        :root {
            --hanek-navy: #10213f;
            --hanek-blue: #173f78;
            --hanek-royal: #2458a6;
            --hanek-gold: #d6a943;
            --hanek-bg: #f3f6fb;
            --hanek-white: #ffffff;
            --hanek-text: #17243b;
            --hanek-muted: #64748b;
            --hanek-border: #dce4ef;
        }

        .stApp {
            background: var(--hanek-bg);
            color: var(--hanek-text);
        }

        .main .block-container {
            max-width: 1600px;
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }

        h1, h2, h3, h4, h5, h6 {
            color: var(--hanek-navy);
            font-family: "Segoe UI", Arial, sans-serif;
            font-weight: 800;
        }

        h1 {
            border-bottom: 3px solid var(--hanek-gold);
            padding-bottom: .35rem;
        }

        .hanek-brand {
            background: linear-gradient(125deg, #10213f, #173f78 62%, #2458a6);
            color: white;
            padding: 28px;
            border-radius: 16px;
            border-bottom: 5px solid var(--hanek-gold);
            margin-bottom: 20px;
            box-shadow: 0 8px 25px rgba(16,33,63,.14);
        }

        .hanek-brand h1,
        .hanek-brand h2,
        .hanek-brand p {
            color: white !important;
            border-bottom: none;
        }

        .hanek-brand h1 {
            font-size: clamp(22px, 3vw, 35px);
            line-height: 1.3;
            margin: 8px 0;
        }

        .hanek-eyebrow, .footer-eyebrow {
            color: var(--hanek-gold);
            font-size: 10px;
            font-weight: 900;
            letter-spacing: 2px;
            text-transform: uppercase;
        }

        .hanek-gold-line {
            width: 85px;
            height: 4px;
            background: var(--hanek-gold);
            border-radius: 8px;
            margin: 12px 0;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #10213f, #142f57);
            border-right: 3px solid var(--hanek-gold);
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span {
            color: white;
        }

        [data-testid="stSidebar"] hr {
            border-color: rgba(214,169,67,.6);
        }

        [data-testid="stSidebar"] input {
            background: white;
            color: #10213f;
            border-radius: 8px;
        }

        [data-testid="stSidebar"] [data-baseweb="select"] > div {
            background: white;
            color: #10213f;
        }

        [data-testid="stSidebar"] [data-baseweb="select"] * {
            color: #10213f;
        }

        .notice-card, .contact-box {
            background: white;
            border: 1px solid var(--hanek-border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 4px 18px rgba(16,33,63,.05);
        }

        .notice-card {
            border-left: 5px solid var(--hanek-gold);
        }

        .notice-card h4, .contact-box h4 {
            color: var(--hanek-blue);
            margin-top: 0;
        }

        .contact-box {
            border-top: 5px solid var(--hanek-gold);
        }

        .stButton > button, .stFormSubmitButton > button {
            background: linear-gradient(135deg, #173f78, #2458a6);
            color: white !important;
            border: 1px solid #173f78;
            border-radius: 9px;
            min-height: 42px;
            font-weight: 700;
        }

        .stButton > button:hover, .stFormSubmitButton > button:hover {
            background: #10213f;
            border-color: var(--hanek-gold);
            color: white !important;
        }

        .stTextInput input, .stTextArea textarea,
        .stNumberInput input, .stDateInput input {
            background: white;
            border-radius: 8px;
            color: var(--hanek-text);
        }

        [data-baseweb="select"] > div {
            border-radius: 8px;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 5px;
            flex-wrap: wrap;
        }

        .stTabs [data-baseweb="tab"] {
            background: #e8edf5;
            border-radius: 8px 8px 0 0;
            padding: 8px 12px;
            font-weight: 700;
        }

        .stTabs [aria-selected="true"] {
            background: var(--hanek-blue);
            color: white !important;
            border-bottom: 3px solid var(--hanek-gold);
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--hanek-border);
            border-radius: 9px;
            overflow: hidden;
            background: white;
        }

        [data-testid="stExpander"] {
            background: white;
            border: 1px solid var(--hanek-border);
            border-radius: 10px;
        }

        [data-testid="stFileUploader"] {
            background: white;
            border: 1px dashed #9aacc5;
            border-radius: 10px;
            padding: 10px;
        }

        .hanek-footer {
            text-align: center;
            padding: 22px 16px;
            margin-top: 28px;
            background: white;
            border-top: 5px solid var(--hanek-gold);
            border-radius: 12px;
            color: var(--hanek-blue);
            line-height: 1.8;
            overflow-wrap: anywhere;
        }

        .hanek-footer strong {
            color: var(--hanek-navy);
        }

        .footer-eyebrow {
            margin-bottom: 8px;
        }

        .footer-subtitle {
            color: var(--hanek-muted);
            font-size: 12px;
        }

        @media (max-width: 768px) {
            .main .block-container {
                padding: 1rem .75rem 1.5rem .75rem;
            }

            .hanek-brand {
                padding: 18px;
                border-radius: 12px;
            }

            .hanek-brand h1 {
                font-size: 23px;
            }

            .notice-card, .contact-box {
                padding: 15px;
            }

            .stTabs [data-baseweb="tab"] {
                padding: 7px;
                font-size: 11px;
            }
        }

        @media print {
            [data-testid="stSidebar"],
            .stButton,
            .stFormSubmitButton,
            header, footer {
                display: none !important;
            }

            .main .block-container {
                max-width: 100% !important;
                padding: 0 !important;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------- SIDEBAR --------------------

st.sidebar.markdown(
    """
    <div style="
        text-align:center;padding:20px 8px 15px;
        border-bottom:2px solid #d6a943;margin-bottom:15px;">
        <div style="font-size:36px;margin-bottom:8px;">🎓</div>
        <h2 style="color:white;font-size:22px;margin:0;">HANEK COLLEGE</h2>
        <p style="color:#d6a943;font-size:10px;font-weight:800;
                  letter-spacing:1.4px;margin:8px 0;">
            TECHNOLOGY &amp; BUSINESS
        </p>
        <p style="color:#e2e8f0;font-size:11px;line-height:1.6;margin:0;">
            Multi-Campus Student Information<br>
            &amp; Registrar Management System
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if os.path.exists(LOGO_FILE):
    st.sidebar.image(LOGO_FILE, use_container_width=True)

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


# -------------------- HOME PORTAL --------------------

if role == "Home / Public Announcements & Contacts":
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            """
            <div class="hanek-brand">
                <div class="hanek-eyebrow">
                    Excellence • Knowledge • Professionalism
                </div>
                <h1>HANEK TECHNOLOGY AND BUSINESS COLLEGE</h1>
                <div class="hanek-gold-line"></div>
                <p style="font-size:17px;font-weight:700;">
                    Official Multi-Campus Registrar &amp; Student Information System
                </p>
                <p style="margin-top:12px;font-size:14px;">
                    Serving Wolaita Sodo, Basketo Laska, Boloso Bombe, and Jinka campuses.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        if os.path.exists(LOGO_FILE):
            st.image(LOGO_FILE, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📢 Public Announcements")

    ann_df = read_csv(ANNOUNCE_FILE)

    if ann_df.empty:
        st.info("No public announcements currently posted.")
    else:
        for _, row in ann_df.iterrows():
            st.markdown(
                f"""
                <div class="notice-card">
                    <h4>{safe_text(row.get('Title', ''))}</h4>
                    <p style="font-size:12px;color:#64748b;">
                        <b>Date:</b> {safe_text(row.get('Date', ''))}
                        | <b>{safe_text(row.get('Category', ''))}</b>
                    </p>
                    <p style="margin:0;">{safe_text(row.get('Content', ''))}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown("### 📞 Institutional Contact Directory")

    st.markdown(
        """
        <div class="contact-box">
            <h4>Office of the Registrar</h4>
            <p><b>Headquarters:</b> Wolaita Sodo, Ethiopia (P.O. Box 23)</p>
            <p><b>Telephone:</b> +251-46-180-3164 / +251916747538</p>
            <p><b>Email:</b> registrar@hanekcollege.edu.et</p>
            <p><b>Website:</b> http://www.hanekcollege.edu.et</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------- ONLINE ADMISSION --------------------

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
            if app_name.strip() and app_phone.strip():
                apps_df = read_csv(APPLICATIONS_FILE)

                new_app = pd.DataFrame([{
                    "AppID": "".join(random.choices(string.ascii_uppercase, k=6)),
                    "FullName": app_name.strip(),
                    "Phone": app_phone.strip(),
                    "Campus": app_campus,
                    "Department": app_dept,
                    "ProgramLevel": app_prog,
                    "Modality": app_mod,
                    "Status": "Pending Review",
                    "DateSubmitted": pd.Timestamp.now().strftime("%Y-%m-%d"),
                }])

                save_csv(pd.concat([apps_df, new_app], ignore_index=True), APPLICATIONS_FILE)
                st.success("Application submitted successfully.")
            else:
                st.error("Please provide the applicant's name and phone number.")


# -------------------- HEAD REGISTRAR PORTAL --------------------

elif role == "Head Registrar & Administration":
    st.sidebar.subheader("🔐 Head Registrar Login")

    username = st.sidebar.text_input("Username", value="admin.hanek")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        admin_df = read_csv(ADMIN_FILE)

        if (
            not admin_df.empty
            and (
                (admin_df["Username"].astype(str) == username)
                & (admin_df["Password"].astype(str) == password)
            ).any()
        ):
            st.session_state["authenticated"] = True
            st.session_state["role"] = "Admin"
            st.success("Logged in successfully.")
            st.rerun()
        else:
            st.sidebar.error("Invalid username or password.")

    if st.session_state.get("role") == "Admin":
        st.title("🛡️ Head Registrar Control Dashboard")

        tabs = st.tabs([
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

        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = tabs

        departments_list = get_departments()
        programs_list = get_programs()

        # ---------------- STUDENT RECORDS ----------------

        with tab1:
            st.subheader("🎓 Student Master Record Management")

            students_df = read_csv(STUDENT_FILE)

            with st.expander("➕ Register New Student Profile"):
                with st.form("add_student_form"):
                    col1, col2 = st.columns(2)

                    with col1:
                        s_id = st.text_input("Student ID")
                        s_name = st.text_input("Full Legal Name")
                        s_campus = st.selectbox("Assigned Campus", CAMPUSES)

                    with col2:
                        s_dept = st.selectbox("Department", departments_list)
                        s_prog = st.selectbox("Program Level", programs_list)
                        s_mod = st.selectbox("Modality", ["Regular", "Extension"])
                        s_pass = st.text_input("Initial Student Password", type="password")

                    if st.form_submit_button("Admit Student"):
                        if not s_id.strip() or not s_name.strip() or not s_pass:
                            st.error("Student ID, name, and password are required.")
                        elif s_id in students_df["StudentID"].astype(str).values:
                            st.error("Student ID already exists.")
                        else:
                            new_row = pd.DataFrame([{
                                "StudentID": s_id.strip(),
                                "FullName": s_name.strip(),
                                "Campus": s_campus,
                                "Department": s_dept,
                                "ProgramLevel": s_prog,
                                "Modality": s_mod,
                                "Year": "1",
                                "Password": s_pass,
                                "Photo": "",
                                "PhotoStatus": "Not Uploaded",
                            }])

                            save_csv(pd.concat([students_df, new_row], ignore_index=True), STUDENT_FILE)
                            st.success("Student admitted successfully.")
                            st.rerun()

            st.markdown("---")
            st.markdown("### Existing Student Database")

            students_df = read_csv(STUDENT_FILE)

            if students_df.empty:
                st.info("No student records found.")
            else:
                display_df = students_df.drop(columns=["Password"], errors="ignore")
                st.dataframe(display_df, use_container_width=True)

                sel_edit = st.selectbox(
                    "Select Student ID to Edit",
                    students_df["StudentID"].astype(str).tolist(),
                )

                st_row = students_df[
                    students_df["StudentID"].astype(str) == sel_edit
                ].iloc[0]

                with st.form("edit_student_form"):
                    e_name = st.text_input("Full Legal Name", value=str(st_row["FullName"]))

                    e_campus = st.selectbox(
                        "Campus",
                        CAMPUSES,
                        index=CAMPUSES.index(st_row["Campus"])
                        if st_row["Campus"] in CAMPUSES else 0,
                    )

                    e_dept = st.selectbox(
                        "Department",
                        departments_list,
                        index=departments_list.index(st_row["Department"])
                        if st_row["Department"] in departments_list else 0,
                    )

                    e_prog = st.selectbox(
                        "Program Level",
                        programs_list,
                        index=programs_list.index(st_row["ProgramLevel"])
                        if st_row["ProgramLevel"] in programs_list else 0,
                    )

                    e_pass = st.text_input(
                        "Change Password (leave blank to keep current)",
                        type="password",
                    )

                    save_btn, delete_btn = st.columns(2)
                    save_record = save_btn.form_submit_button("💾 Save Changes")
                    delete_record = delete_btn.form_submit_button("🗑️ Delete Student")

                    if save_record:
                        students_df.loc[
                            students_df["StudentID"].astype(str) == sel_edit,
                            ["FullName", "Campus", "Department", "ProgramLevel"],
                        ] = [e_name, e_campus, e_dept, e_prog]

                        if e_pass:
                            students_df.loc[
                                students_df["StudentID"].astype(str) == sel_edit,
                                "Password",
                            ] = e_pass

                        save_csv(students_df, STUDENT_FILE)
                        st.success("Student record updated.")
                        st.rerun()

                    if delete_record:
                        students_df = students_df[
                            students_df["StudentID"].astype(str) != sel_edit
                        ]
                        save_csv(students_df, STUDENT_FILE)
                        st.warning("Student record deleted.")
                        st.rerun()

        # ---------------- PHOTO APPROVALS ----------------

        with tab2:
            st.subheader("🖼️ Student Photo Verification")

            students_df = read_csv(STUDENT_FILE)
            pending_photos = students_df[
                students_df["PhotoStatus"].astype(str) == "Pending Approval"
            ]

            if pending_photos.empty:
                st.info("No student photos awaiting approval.")
            else:
                for _, row in pending_photos.iterrows():
                    c1, c2 = st.columns([1, 2])

                    with c1:
                        photo = str(row.get("Photo", ""))
                        if photo and os.path.exists(photo):
                            st.image(photo, width=130)
                        else:
                            st.warning("Photo file missing.")

                    with c2:
                        st.write(f"**Student ID:** {row['StudentID']}")
                        st.write(f"**Name:** {row['FullName']}")
                        st.write(f"**Campus:** {row['Campus']}")

                        if st.button(
                            f"✅ Approve Photo — {row['StudentID']}",
                            key=f"approve_photo_{row['StudentID']}",
                        ):
                            students_df.loc[
                                students_df["StudentID"].astype(str)
                                == str(row["StudentID"]),
                                "PhotoStatus",
                            ] = "Approved"
                            save_csv(students_df, STUDENT_FILE)
                            st.success("Photo approved.")
                            st.rerun()

                    st.markdown("---")

        # ---------------- APPLICANTS ----------------

        with tab3:
            st.subheader("📋 Online Applications")

            apps_df = read_csv(APPLICATIONS_FILE)

            if apps_df.empty:
                st.info("No online applications.")
            else:
                st.dataframe(apps_df, use_container_width=True)

                applicant_ids = apps_df["AppID"].astype(str).tolist()
                sel_app = st.selectbox("Select Application", applicant_ids)

                if st.button("🎓 Admit Applicant"):
                    app_match = apps_df[
                        apps_df["AppID"].astype(str) == sel_app
                    ]

                    if not app_match.empty:
                        app_row = app_match.iloc[0]
                        students_df = read_csv(STUDENT_FILE)

                        new_sid = f"HBC/{random.randint(100, 999)}/26"
                        while new_sid in students_df["StudentID"].astype(str).values:
                            new_sid = f"HBC/{random.randint(100, 999)}/26"

                        new_student = pd.DataFrame([{
                            "StudentID": new_sid,
                            "FullName": app_row["FullName"],
                            "Campus": app_row["Campus"],
                            "Department": app_row["Department"],
                            "ProgramLevel": app_row["ProgramLevel"],
                            "Modality": app_row["Modality"],
                            "Year": "1",
                            "Password": "".join(random.choices(string.ascii_letters + string.digits, k=12)),
                            "Photo": "",
                            "PhotoStatus": "Not Uploaded",
                        }])

                        save_csv(pd.concat([students_df, new_student], ignore_index=True), STUDENT_FILE)

                        apps_df.loc[
                            apps_df["AppID"].astype(str) == sel_app,
                            "Status",
                        ] = "Admitted"
                        save_csv(apps_df, APPLICATIONS_FILE)

                        st.success(
                            f"Applicant admitted. Student ID: {new_sid}. "
                            "Set up a secure process to provide the initial password."
                        )
                        st.rerun()

        # ---------------- STAFF DIRECTORY ----------------

        with tab4:
            st.subheader("👨‍🏫 Staff & Registrar Officers")

            staff_df = read_csv(STAFF_FILE)

            with st.expander("➕ Register Staff Member"):
                with st.form("add_staff"):
                    st_id = st.text_input("Staff ID")
                    st_name = st.text_input("Full Name")
                    st_role = st.selectbox("Role", STAFF_ROLES)
                    st_campus = st.selectbox("Campus", CAMPUSES + ["All Campuses"])
                    st_dept = st.text_input("Department / Unit", value="Office of the Registrar")
                    st_email = st.text_input("Institutional Email")
                    st_pass = st.text_input("Initial Password", type="password")

                    if st.form_submit_button("Save Staff Profile"):
                        if not st_id.strip() or not st_name.strip() or not st_pass:
                            st.error("Staff ID, name, and password are required.")
                        elif st_id in staff_df["StaffID"].astype(str).values:
                            st.error("Staff ID already exists.")
                        else:
                            new_staff = pd.DataFrame([{
                                "StaffID": st_id.strip(),
                                "FullName": st_name.strip(),
                                "Role": st_role,
                                "Campus": st_campus,
                                "Department": st_dept,
                                "InstitutionalEmail": st_email,
                                "Password": st_pass,
                            }])
                            save_csv(pd.concat([staff_df, new_staff], ignore_index=True), STAFF_FILE)
                            st.success("Staff profile saved.")
                            st.rerun()

            staff_df = read_csv(STAFF_FILE)

            if not staff_df.empty:
                st.dataframe(
                    staff_df.drop(columns=["Password"], errors="ignore"),
                    use_container_width=True,
                )

        # ---------------- ANNOUNCEMENTS ----------------

        with tab5:
            st.subheader("📢 Announcements & Notices")

            ann_df = read_csv(ANNOUNCE_FILE)
            if not ann_df.empty:
                st.dataframe(ann_df, use_container_width=True)
            else:
                st.info("No announcements have been published.")

            with st.form("add_ann"):
                a_title = st.text_input("Notice Title")
                a_cat = st.selectbox(
                    "Category",
                    ["General Notice", "Exam Schedule", "Registration Deadline"],
                )
                a_cont = st.text_area("Notice Content")

                if st.form_submit_button("Publish Notice"):
                    if a_title.strip() and a_cont.strip():
                        new_notice = pd.DataFrame([{
                            "NoticeID": "".join(random.choices(string.ascii_uppercase, k=5)),
                            "Title": a_title.strip(),
                            "Date": pd.Timestamp.now().strftime("%Y-%m-%d"),
                            "Category": a_cat,
                            "Content": a_cont.strip(),
                        }])
                        save_csv(pd.concat([ann_df, new_notice], ignore_index=True), ANNOUNCE_FILE)
                        st.success("Notice published.")
                        st.rerun()
                    else:
                        st.error("Enter both a title and content.")

        # ---------------- DEPARTMENTS & PROGRAMS ----------------

        with tab6:
            st.subheader("📚 Departments & Programs")

            col_d, col_p = st.columns(2)

            with col_d:
                st.markdown("#### Departments")
                st.write(get_departments())

                with st.form("add_d"):
                    new_department = st.text_input("New Department")
                    if st.form_submit_button("Add Department"):
                        current = get_departments()
                        if new_department.strip() and new_department not in current:
                            current.append(new_department.strip())
                            save_csv(pd.DataFrame({"Department": current}), DEPT_FILE)
                            st.success("Department added.")
                            st.rerun()
                        else:
                            st.error("Enter a new department name.")

            with col_p:
                st.markdown("#### Programs")
                st.write(get_programs())

                with st.form("add_p"):
                    new_program = st.text_input("New Program Level")
                    if st.form_submit_button("Add Program"):
                        current = get_programs()
                        if new_program.strip() and new_program not in current:
                            current.append(new_program.strip())
                            save_csv(pd.DataFrame({"Program": current}), PROG_FILE)
                            st.success("Program added.")
                            st.rerun()
                        else:
                            st.error("Enter a new program name.")

        # ---------------- GRADE APPROVALS ----------------

        with tab7:
            st.subheader("✅ Pending Grade Submissions")

            pending_df = read_csv(PENDING_FILE)

            if pending_df.empty:
                st.info("No pending grades.")
            else:
                st.dataframe(pending_df, use_container_width=True)
                pending_options = {
                    f"{row['PendingID']} — {row['StudentID']} — {row['CourseName']}": idx
                    for idx, row in pending_df.iterrows()
                }
                selected_pending = st.selectbox(
                    "Select Pending Grade",
                    list(pending_options.keys()),
                )
                idx = pending_options[selected_pending]

                approve_col, reject_col = st.columns(2)

                if approve_col.button("✅ Approve & Post Grade"):
                    row = pending_df.loc[idx]
                    grades_df = read_csv(GRADES_FILE)
                    grade_value, grade_point, _ = calculate_grade(float(row["Score"]))

                    final_grade = pd.DataFrame([{
                        "StudentID": row["StudentID"],
                        "FullName": row["FullName"],
                        "CourseCode": row["CourseCode"],
                        "CourseName": row["CourseName"],
                        "CreditHour": row["CreditHour"],
                        "Score": row["Score"],
                        "Grade": f"{grade_value} ({grade_point})",
                        "Level": row.get("Level", "TVET Level I"),
                        "Semester": row.get("Semester", "Semester I"),
                        "AcademicYear": "2025/2026",
                    }])

                    save_csv(pd.concat([grades_df, final_grade], ignore_index=True), GRADES_FILE)
                    pending_df = pending_df.drop(idx).reset_index(drop=True)
                    save_csv(pending_df, PENDING_FILE)
                    st.success("Grade approved and posted.")
                    st.rerun()

                if reject_col.button("❌ Reject Grade"):
                    pending_df = pending_df.drop(idx).reset_index(drop=True)
                    save_csv(pending_df, PENDING_FILE)
                    st.warning("Pending grade rejected.")
                    st.rerun()

        # ---------------- FINANCIAL ACCOUNTS ----------------

        with tab8:
            st.subheader("💰 Student Financial Accounts (ETB)")

            fin_df = read_csv(FINANCE_FILE)
            students_df = read_csv(STUDENT_FILE)

            if not fin_df.empty:
                st.dataframe(fin_df, use_container_width=True)
            else:
                st.info("No financial accounts have been entered.")

            student_ids = students_df["StudentID"].astype(str).tolist() if not students_df.empty else []

            with st.form("fin_form"):
                if student_ids:
                    f_sid = st.selectbox("Student ID", student_ids)
                else:
                    f_sid = None
                    st.warning("Register a student before adding a financial account.")

                tot_f = st.number_input("Total Fee (ETB)", min_value=0.0, value=15000.0, step=500.0)
                paid_f = st.number_input("Amount Paid (ETB)", min_value=0.0, value=0.0, step=500.0)
                stat = st.selectbox("Clearance Status", ["Pending Clearance", "Fully Cleared"])

                if st.form_submit_button("Update Financial Ledger"):
                    if f_sid:
                        fin_df = read_csv(FINANCE_FILE)
                        updated = False

                        if not fin_df.empty and (fin_df["StudentID"].astype(str) == f_sid).any():
                            mask = fin_df["StudentID"].astype(str) == f_sid
                            fin_df.loc[mask, "TotalFeeETB"] = tot_f
                            fin_df.loc[mask, "PaidETB"] = paid_f
                            fin_df.loc[mask, "Status"] = stat
                            fin_df.loc[mask, "LastUpdated"] = pd.Timestamp.now().strftime("%Y-%m-%d")
                            updated = True

                        if not updated:
                            new_finance = pd.DataFrame([{
                                "StudentID": f_sid,
                                "TotalFeeETB": tot_f,
                                "PaidETB": paid_f,
                                "Status": stat,
                                "LastUpdated": pd.Timestamp.now().strftime("%Y-%m-%d"),
                            }])
                            fin_df = pd.concat([fin_df, new_finance], ignore_index=True)

                        save_csv(fin_df, FINANCE_FILE)
                        st.success("Financial ledger updated.")
                        st.rerun()


        # ---------------- OFFICIAL CREDENTIALS ----------------

        with tab9:
            st.subheader("🖨️ Official Academic Credential Issuance")

            students_df = read_csv(STUDENT_FILE)

            if students_df.empty:
                st.info("Register or admit a student before issuing credentials.")
            else:
                students_df["StudentID"] = students_df["StudentID"].astype(str)
                students_df["FullName"] = students_df["FullName"].astype(str)

                student_choices = {
                    f"{row['StudentID']} — {row['FullName']}": row["StudentID"]
                    for _, row in students_df.iterrows()
                }

                chosen_student = st.selectbox(
                    "Select Student for Credential",
                    list(student_choices.keys()),
                )
                sel_sid = student_choices[chosen_student]

                s_info = students_df[
                    students_df["StudentID"] == sel_sid
                ].iloc[0]

                doc_type = st.selectbox(
                    "Document Type",
                    [
                        "Official Academic Transcript",
                        "Temporary Grade Report",
                        "Official TVET Diploma Certificate",
                    ],
                )

                fin_df = read_csv(FINANCE_FILE)
                finance_match = fin_df[
                    fin_df["StudentID"].astype(str) == sel_sid
                ] if not fin_df.empty else pd.DataFrame()

                is_cleared = (
                    finance_match.empty
                    or str(finance_match.iloc[0].get("Status", "")) == "Fully Cleared"
                )

                restricted_document = doc_type in [
                    "Official Academic Transcript",
                    "Official TVET Diploma Certificate",
                ]

                if not is_cleared and restricted_document:
                    st.error(
                        "Financial clearance is required before issuing this official document."
                    )
                else:
                    grades_df = read_csv(GRADES_FILE)
                    s_grades = grades_df[
                        grades_df["StudentID"].astype(str) == sel_sid
                    ] if not grades_df.empty else pd.DataFrame()

                    # Stable code for this preview; it changes only when the
                    # selected student or document type changes.
                    auth_key = f"auth_{sel_sid}_{doc_type}"
                    if auth_key not in st.session_state:
                        st.session_state[auth_key] = generate_auth_code()
                    auth_code = st.session_state[auth_key]

                    photo_tag = ""
                    photo_path = str(s_info.get("Photo", ""))

                    if photo_path and os.path.exists(photo_path):
                        try:
                            with open(photo_path, "rb") as image_file:
                                encoded = base64.b64encode(image_file.read()).decode("ascii")
                            extension = os.path.splitext(photo_path)[1].lower()
                            mime_type = "image/jpeg" if extension in [".jpg", ".jpeg"] else "image/png"
                            photo_tag = (
                                f'<img src="data:{mime_type};base64,{encoded}" '
                                'style="width:65px;height:80px;border:1px solid #555;'
                                'object-fit:cover;float:right;margin-left:12px;" />'
                            )
                        except OSError:
                            photo_tag = ""

                    if doc_type == "Official TVET Diploma Certificate":
                        credential_html = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <style>
                            * {{ box-sizing: border-box; }}
                            body {{ margin:0; padding:10px; background:#f4f6fa; font-family:Arial,sans-serif; }}
                            .certificate {{
                                width:100%; max-width:1000px; margin:auto; padding:28px;
                                border:7px double #1e3a8a; background:#fffdfa;
                                text-align:center; color:#111; overflow-wrap:anywhere;
                            }}
                            .college {{ color:#1e3a8a; font-size:clamp(18px,3vw,28px); margin:0; }}
                            .office {{ font-size:12px; font-weight:bold; color:#555; margin:5px 0; }}
                            .contact {{ font-size:10px; color:#555; line-height:1.6; }}
                            .rule {{ border:0; border-top:2px solid #1e3a8a; width:60%; margin:14px auto; }}
                            .diploma-title {{ font-size:clamp(18px,3vw,24px); margin:14px 0; color:#1e3a8a; }}
                            .student-name {{ font-size:clamp(20px,4vw,32px); font-weight:bold; margin:10px 0; overflow-wrap:anywhere; }}
                            .description {{ font-size:13px; line-height:1.8; max-width:760px; margin:12px auto; }}
                            .details {{ width:100%; border-collapse:collapse; margin:18px auto; font-size:12px; }}
                            .details td {{ padding:8px; border:1px solid #ddd; }}
                            .signatures {{ display:flex; gap:20px; justify-content:space-between; margin-top:40px; font-size:11px; text-align:center; }}
                            .signatures div {{ flex:1; }}
                            .auth {{ font-family:monospace; color:#1e3a8a; overflow-wrap:anywhere; }}
                            @media(max-width:600px) {{
                                body {{ padding:3px; }}
                                .certificate {{ padding:12px; border-width:4px; }}
                                .details td {{ display:block; width:100%; text-align:left; }}
                                .signatures {{ flex-direction:column; margin-top:25px; }}
                            }}
                            @media print {{
                                body {{ background:white; padding:0; }}
                                .certificate {{ max-width:none; border-width:5px; }}
                            }}
                        </style>
                        </head>
                        <body>
                            <div class="certificate">
                                <h1 class="college">HANEK TECHNOLOGY AND BUSINESS COLLEGE</h1>
                                <div class="office">OFFICE OF THE REGISTRAR</div>
                                <div class="contact">
                                    Tel: +251-46-180-3164 / +251916747538<br>
                                    P.O. Box 23, Wolaita Sodo, Ethiopia
                                </div>
                                <hr class="rule">
                                <h2 class="diploma-title">TVET LEVEL IV DIPLOMA</h2>
                                <p>This is to certify that</p>
                                <div class="student-name">{safe_text(s_info["FullName"])}</div>
                                <div class="description">
                                    having successfully completed the prescribed training program
                                    and fulfilled the requirements under the Department of
                                    <strong>{safe_text(s_info["Department"])}</strong>,
                                    is hereby awarded the Level IV Diploma, subject to official
                                    institutional verification and approval.
                                </div>
                                <table class="details">
                                    <tr>
                                        <td><strong>Student ID:</strong> {safe_text(sel_sid)}</td>
                                        <td><strong>Campus:</strong> {safe_text(s_info["Campus"])}</td>
                                        <td><strong>Medium:</strong> English</td>
                                    </tr>
                                </table>
                                <div class="signatures">
                                    <div>
                                        <p><strong>Authentication Code</strong></p>
                                        <p class="auth">{safe_text(auth_code)}</p>
                                    </div>
                                    <div>
                                        <p>____________________________</p>
                                        <strong>Head Registrar Signature</strong>
                                    </div>
                                </div>
                            </div>
                        </body>
                        </html>
                        """
                        html_document(credential_html, height=720)

                    else:
                        grade_rows = ""

                        if s_grades.empty:
                            grade_rows = """
                                <tr>
                                    <td colspan="6" class="empty">
                                        No authorized modules recorded yet.
                                    </td>
                                </tr>
                            """
                        else:
                            for _, grade_row in s_grades.iterrows():
                                grade_rows += f"""
                                <tr>
                                    <td>{safe_text(grade_row.get('Level', ''))}</td>
                                    <td>{safe_text(grade_row.get('CourseCode', ''))}</td>
                                    <td>{safe_text(grade_row.get('CourseName', ''))}</td>
                                    <td>{safe_text(grade_row.get('CreditHour', ''))}</td>
                                    <td>{safe_text(grade_row.get('Score', ''))}</td>
                                    <td>{safe_text(grade_row.get('Grade', ''))}</td>
                                </tr>
                                """

                        credential_html = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <style>
                            * {{ box-sizing:border-box; }}
                            body {{ margin:0; padding:8px; background:#f4f6fa; font-family:Arial,sans-serif; color:#111; }}
                            .document {{
                                width:100%; max-width:1000px; margin:auto; background:white;
                                border:2px solid #222; padding:16px; overflow-wrap:anywhere;
                            }}
                            .header {{ text-align:center; border-bottom:2px solid #222; padding-bottom:8px; margin-bottom:10px; }}
                            .college {{ font-size:clamp(15px,2.5vw,22px); margin:0; color:#10213f; }}
                            .office {{ font-size:11px; font-weight:bold; margin:5px 0; }}
                            .contact {{ font-size:10px; color:#444; line-height:1.5; }}
                            .doc-title {{ font-size:13px; font-weight:bold; margin-top:8px; color:#1e3a8a; }}
                            .photo {{ float:right; width:65px; height:80px; object-fit:cover; border:1px solid #555; margin-left:10px; }}
                            .student-info {{ width:100%; border-collapse:collapse; margin-bottom:10px; font-size:11px; }}
                            .student-info td {{ padding:5px; border:1px solid #ddd; }}
                            .grades {{ width:100%; border-collapse:collapse; font-size:10px; margin-bottom:12px; table-layout:fixed; }}
                            .grades th {{ background:#e8edf5; }}
                            .grades th,.grades td {{ border:1px solid #aaa; padding:5px 3px; text-align:left; overflow-wrap:anywhere; }}
                            .grades th:nth-child(3), .grades td:nth-child(3) {{ width:35%; }}
                            .empty {{ text-align:center !important; padding:12px !important; }}
                            .bottom {{ display:flex; justify-content:space-between; gap:15px; flex-wrap:wrap; border-top:1px solid #333; padding-top:10px; font-size:10px; }}
                            .auth {{ color:#1e3a8a; font-family:monospace; overflow-wrap:anywhere; }}
                            .disclaimer {{ font-size:9px; color:#555; margin-top:14px; }}
                            @media(max-width:600px) {{
                                body {{ padding:2px; }}
                                .document {{ padding:8px; }}
                                .student-info td {{ display:block; width:100%; }}
                                .grades {{ font-size:8px; }}
                                .grades th,.grades td {{ padding:3px 2px; }}
                                .bottom {{ display:block; line-height:1.8; }}
                            }}
                            @media print {{
                                body {{ background:white; padding:0; }}
                                .document {{ max-width:none; }}
                            }}
                        </style>
                        </head>
                        <body>
                            <div class="document">
                                <div class="header">
                                    {photo_tag}
                                    <h1 class="college">HANEK TECHNOLOGY AND BUSINESS COLLEGE</h1>
                                    <div class="office">OFFICE OF THE REGISTRAR</div>
                                    <div class="contact">
                                        Tel: +251-46-180-3164 / +251916747538<br>
                                        P.O. Box 23, Wolaita Sodo, Ethiopia<br>
                                        Website: www.hanekcollege.edu.et
                                    </div>
                                    <div class="doc-title">{safe_text(doc_type)}</div>
                                </div>

                                <table class="student-info">
                                    <tr>
                                        <td><strong>Student Name:</strong> {safe_text(s_info["FullName"])}</td>
                                        <td><strong>Student ID:</strong> {safe_text(sel_sid)}</td>
                                    </tr>
                                    <tr>
                                        <td><strong>Campus:</strong> {safe_text(s_info["Campus"])}</td>
                                        <td><strong>Department:</strong> {safe_text(s_info["Department"])}</td>
                                    </tr>
                                    <tr>
                                        <td><strong>Program:</strong> {safe_text(s_info["ProgramLevel"])}</td>
                                        <td><strong>Modality:</strong> {safe_text(s_info["Modality"])}</td>
                                    </tr>
                                </table>

                                <table class="grades">
                                    <thead>
                                        <tr>
                                            <th>Level</th>
                                            <th>Code</th>
                                            <th>Module Title</th>
                                            <th>Cr.Hr</th>
                                            <th>Score</th>
                                            <th>Grade</th>
                                        </tr>
                                    </thead>
                                    <tbody>{grade_rows}</tbody>
                                </table>

                                <div class="bottom">
                                    <div>
                                        <strong>Authentication Code:</strong>
                                        <span class="auth">{safe_text(auth_code)}</span>
                                    </div>
                                    <div><strong>Head Registrar:</strong> ____________________</div>
                                </div>

                                <div class="disclaimer">
                                    This preview is generated by the institutional information system.
                                    Official validity depends on authorized institutional approval and signature.
                                </div>
                            </div>
                        </body>
                        </html>
                        """

                        html_document(credential_html, height=950)

                    st.caption(
                        "Credential preview is rendered as HTML. "
                        "For printing or saving as PDF, use your browser's print options."
                    )

        # ---------------- SYSTEM CONFIGURATION ----------------

        with tab10:
            st.subheader("⚙️ System Configuration & Health")

            students_count = len(read_csv(STUDENT_FILE))
            staff_count = len(read_csv(STAFF_FILE))
            pending_count = len(read_csv(PENDING_FILE))

            metric1, metric2, metric3 = st.columns(3)
            metric1.metric("Total Students", students_count)
            metric2.metric("Total Staff", staff_count)
            metric3.metric("Pending Grades", pending_count)

            st.markdown("---")
            st.markdown("### 🖼️ Upload Institutional Logo")

            uploaded_logo = st.file_uploader(
                "Choose institutional logo",
                type=["png", "jpg", "jpeg"],
                key="institution_logo",
            )

            if uploaded_logo is not None:
                try:
                    with open(LOGO_FILE, "wb") as logo_file:
                        logo_file.write(uploaded_logo.getbuffer())
                    st.success("Institutional logo saved.")
                    st.rerun()
                except OSError as exc:
                    st.error(f"Could not save logo: {exc}")

            st.markdown("---")
            st.markdown("### System Data Files")

            data_files = [
                STUDENT_FILE,
                GRADES_FILE,
                PENDING_FILE,
                STAFF_FILE,
                FINANCE_FILE,
                DEPT_FILE,
                PROG_FILE,
                ANNOUNCE_FILE,
                APPLICATIONS_FILE,
            ]

            for filename in data_files:
                if os.path.exists(filename):
                    st.write(f"✅ {filename}")
                else:
                    st.warning(f"Missing file: {filename}")


# -------------------- STAFF PORTAL --------------------

elif role == "Staff & Registrar Officers":
    st.title("👨‍🏫 Staff & Registrar Officers Portal")

    staff_id = st.text_input("Staff ID")
    staff_password = st.text_input("Password", type="password")

    if st.button("Staff Login"):
        staff_df = read_csv(STAFF_FILE)

        match = staff_df[
            (staff_df["StaffID"].astype(str) == staff_id)
            & (staff_df["Password"].astype(str) == staff_password)
        ]

        if not match.empty:
            staff_row = match.iloc[0]
            st.session_state["staff_logged"] = str(staff_row["StaffID"])
            st.session_state["staff_name"] = str(staff_row["FullName"])
            st.session_state["staff_role"] = str(staff_row["Role"])
            st.success(f"Welcome, {staff_row['FullName']}.")
            st.rerun()
        else:
            st.error("Invalid staff ID or password.")

    if st.session_state.get("staff_logged"):
        staff_role = st.session_state.get("staff_role", "")
        st.info(f"Logged in as: {staff_role}")

        if st.button("Staff Logout"):
            for key in ["staff_logged", "staff_name", "staff_role"]:
                st.session_state.pop(key, None)
            st.rerun()

        if staff_role in ["Instructor / Lecturer", "Department Head"]:
            st.subheader("Submit Module Grades")

            students_df = read_csv(STUDENT_FILE)

            if students_df.empty:
                st.info("No students are registered yet.")
            else:
                student_options = {
                    f"{row['StudentID']} — {row['FullName']}": row
                    for _, row in students_df.iterrows()
                }

                with st.form("grade_sub"):
                    chosen = st.selectbox("Student", list(student_options.keys()))
                    selected_student = student_options[chosen]

                    level = st.selectbox(
                        "Level",
                        [
                            "TVET Level I",
                            "TVET Level II",
                            "TVET Level III",
                            "TVET Level IV",
                        ],
                    )

                    course_code = st.text_input("Course Code")
                    course_name = st.text_input("Course Name")
                    credit_hour = st.number_input(
                        "Credit Hours",
                        min_value=1,
                        max_value=30,
                        value=3,
                    )
                    score = st.number_input(
                        "Score",
                        min_value=0.0,
                        max_value=100.0,
                        value=75.0,
                    )

                    if st.form_submit_button("Submit Grade"):
                        if not course_code.strip() or not course_name.strip():
                            st.error("Course code and course name are required.")
                        else:
                            pending_df = read_csv(PENDING_FILE)
                            grade_value, grade_point, _ = calculate_grade(score)

                            new_pending = pd.DataFrame([{
                                "PendingID": "".join(random.choices(string.ascii_uppercase, k=5)),
                                "StudentID": selected_student["StudentID"],
                                "FullName": selected_student["FullName"],
                                "CourseCode": course_code.strip(),
                                "CourseName": course_name.strip(),
                                "CreditHour": credit_hour,
                                "Score": score,
                                "Grade": f"{grade_value} ({grade_point})",
                                "Level": level,
                                "Semester": "Semester I",
                                "Instructor": st.session_state.get("staff_name", ""),
                            }])

                            save_csv(pd.concat([pending_df, new_pending], ignore_index=True), PENDING_FILE)
                            st.success("Grade submitted for Head Registrar approval.")


# -------------------- STUDENT PORTAL --------------------

elif role == "Student Portal":
    st.title("🎓 Student Portal")

    student_id = st.text_input("Student ID")
    student_password = st.text_input("Password", type="password")

    if st.button("Student Login"):
        students_df = read_csv(STUDENT_FILE)

        match = students_df[
            (students_df["StudentID"].astype(str) == student_id)
            & (students_df["Password"].astype(str) == student_password)
        ]

        if not match.empty:
            st.session_state["student_logged"] = student_id
            st.success("Student login successful.")
            st.rerun()
        else:
            st.error("Invalid student ID or password.")

    if st.session_state.get("student_logged"):
        current_student_id = st.session_state["student_logged"]
        students_df = read_csv(STUDENT_FILE)

        student_match = students_df[
            students_df["StudentID"].astype(str) == str(current_student_id)
        ]

        if student_match.empty:
            st.session_state.pop("student_logged", None)
            st.error("Student record not found. Please log in again.")
            st.stop()

        student_info = student_match.iloc[0]
        st.subheader(f"Welcome, {student_info['FullName']}")

        if st.button("Student Logout"):
            st.session_state.pop("student_logged", None)
            st.rerun()

        profile_tab, grades_tab = st.tabs(["My Profile & Photo", "My Grades"])

        with profile_tab:
            photo_col, details_col = st.columns([1, 2])

            with photo_col:
                st.markdown("### Profile Photograph")
                photo_path = str(student_info.get("Photo", ""))
                photo_status = str(student_info.get("PhotoStatus", "Not Uploaded"))

                if photo_path and os.path.exists(photo_path):
                    st.image(photo_path, width=140)
                else:
                    st.info("No profile photo uploaded.")

                st.write(f"**Photo Status:** {photo_status}")

                uploaded_photo = st.file_uploader(
                    "Upload Passport Photo",
                    type=["png", "jpg", "jpeg"],
                    key=f"photo_upload_{current_student_id}",
                )

                if uploaded_photo is not None:
                    extension = os.path.splitext(uploaded_photo.name)[1].lower()
                    extension = extension if extension in [".png", ".jpg", ".jpeg"] else ".png"

                    saved_photo = os.path.join(
                        PHOTO_DIR,
                        f"{current_student_id}{extension}",
                    )

                    try:
                        with open(saved_photo, "wb") as photo_file:
                            photo_file.write(uploaded_photo.getbuffer())

                        students_df.loc[
                            students_df["StudentID"].astype(str) == str(current_student_id),
                            ["Photo", "PhotoStatus"],
                        ] = [saved_photo, "Pending Approval"]

                        save_csv(students_df, STUDENT_FILE)
                        st.success("Photo uploaded and sent for approval.")
                        st.rerun()
                    except OSError as exc:
                        st.error(f"Unable to save photo: {exc}")

            with details_col:
                st.markdown("### Student Information")
                st.write(f"**Student ID:** {student_info['StudentID']}")
                st.write(f"**Campus:** {student_info['Campus']}")
                st.write(f"**Department:** {student_info['Department']}")
                st.write(f"**Program:** {student_info['ProgramLevel']}")
                st.write(f"**Modality:** {student_info['Modality']}")

        with grades_tab:
            grades_df = read_csv(GRADES_FILE)

            my_grades = grades_df[
                grades_df["StudentID"].astype(str) == str(current_student_id)
            ] if not grades_df.empty else pd.DataFrame()

            if my_grades.empty:
                st.info("No authorized grades have been posted yet.")
            else:
                st.dataframe(my_grades, use_container_width=True)


# -------------------- GLOBAL FOOTER --------------------

st.markdown("---")
add_footer()
