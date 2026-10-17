# Hanek Technology and Business College
# Integrated Multi-Campus Student Information and Registrar System
# Streamlit application — single-file implementation
#
# IMPORTANT:
# 1. Install the packages listed in requirements.txt.
# 2. Configure a persistent database and secure secrets before production use.
# 3. This application is a foundation, not a guarantee of compliance with every
#    university's regulations or Ethiopian higher-education requirements.
# 4. Back up existing CSV files before migrating existing records.

import os
import re
import hmac
import html
import json
import secrets
import hashlib
import sqlite3
import logging
from pathlib import Path
from datetime import datetime, date
from contextlib import contextmanager

import pandas as pd
import streamlit as st

# ============================================================
# 1. APPLICATION CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Hanek Technology and Business College | Academic Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_NAME = "Hanek Technology and Business College"
APP_SHORT = "HANEK COLLEGE"
APP_VERSION = "2.0.0"
CURRENT_YEAR = date.today().year

DATA_DIR = Path(os.getenv("HANEK_DATA_DIR", "hanek_data"))
UPLOAD_DIR = DATA_DIR / "student_photos"
DATABASE_PATH = DATA_DIR / "hanek_registrar.db"
LOG_PATH = DATA_DIR / "audit.log"

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

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
]

MODALITIES = ["Regular", "Extension", "Distance Learning", "Online"]
SEMESTERS = ["Semester I", "Semester II", "Summer"]
APPLICATION_STATUSES = [
    "Pending Review",
    "Under Review",
    "Admitted",
    "Rejected",
    "Waitlisted",
]
NOTICE_CATEGORIES = [
    "General Notice",
    "Academic Calendar",
    "Examination",
    "Registration Deadline",
    "Scholarship",
    "Graduation",
]
STAFF_ROLES = [
    "College President",
    "Vice President for Academic Affairs",
    "Quality Assurance Director",
    "College Dean",
    "Vice Dean",
    "Department Head",
    "Head Registrar",
    "Assistant Registrar",
    "Registrar Officer",
    "Admissions Officer",
    "Examination Officer",
    "Instructor / Lecturer",
    "Department Finance Officer",
    "Finance Officer",
    "Human Resources Officer",
    "IT / Systems Administrator",
    "Library Officer",
]

# Password hashing uses PBKDF2. Do not store raw passwords.
PBKDF2_ITERATIONS = 310_000
MAX_UPLOAD_MB = 5

# ============================================================
# 2. LOGGING AND SESSION STATE
# ============================================================

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

for key, value in {
    "authenticated": False,
    "username": "",
    "display_name": "",
    "role": "",
    "campus": "",
    "department": "",
    "login_attempts": 0,
    "login_locked_until": 0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = value


def audit(action, detail=""):
    """Record an auditable application event without logging passwords."""
    username = str(st.session_state.get("username", "anonymous"))
    logging.info(
        "user=%s action=%s detail=%s",
        username,
        action,
        str(detail).replace("\n", " ")[:500],
    )


def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return (
        f"pbkdf2_sha256${PBKDF2_ITERATIONS}$"
        f"{salt.hex()}${digest.hex()}"
    )


def verify_password(password, stored):
    """Verify a hashed password; support legacy plaintext only for migration."""
    if not isinstance(stored, str) or not stored:
        return False

    if not stored.startswith("pbkdf2_sha256$"):
        # Legacy credentials are accepted only to permit a controlled upgrade.
        return hmac.compare_digest(password, stored)

    try:
        _, iterations, salt_hex, digest_hex = stored.split("$", 3)
        calculated = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
        return hmac.compare_digest(calculated.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def safe_text(value):
    if value is None:
        return ""
    return html.escape(str(value))


def valid_email(value):
    return bool(
        re.fullmatch(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            value.strip(),
        )
    )


def make_id(prefix):
    return f"{prefix}-{secrets.token_hex(5).upper()}"


def now_string():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def academic_year():
    today = date.today()
    if today.month >= 9:
        return f"{today.year}/{today.year + 1}"
    return f"{today.year - 1}/{today.year}"


def calculate_grade(score):
    score = float(score)
    if not 0 <= score <= 100:
        raise ValueError("The score must be between 0 and 100.")

    if score >= 90:
        return "A+", 4.0
    if score >= 85:
        return "A", 4.0
    if score >= 80:
        return "A-", 3.75
    if score >= 75:
        return "B+", 3.5
    if score >= 70:
        return "B", 3.0
    if score >= 65:
        return "B-", 2.75
    if score >= 60:
        return "C+", 2.5
    if score >= 50:
        return "C", 2.0
    if score >= 40:
        return "D", 1.0
    return "F", 0.0


# ============================================================
# 3. DATABASE
# ============================================================

@contextmanager
def db_connection():
    conn = sqlite3.connect(str(DATABASE_PATH), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    with db_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                campus TEXT NOT NULL DEFAULT 'All Campuses',
                department TEXT NOT NULL DEFAULT '',
                email TEXT NOT NULL DEFAULT '',
                active INTEGER NOT NULL DEFAULT 1,
                must_change_password INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                sex TEXT NOT NULL DEFAULT '',
                date_of_birth TEXT NOT NULL DEFAULT '',
                phone TEXT NOT NULL DEFAULT '',
                email TEXT NOT NULL DEFAULT '',
                address TEXT NOT NULL DEFAULT '',
                campus TEXT NOT NULL,
                department TEXT NOT NULL,
                program TEXT NOT NULL,
                modality TEXT NOT NULL,
                admission_year INTEGER NOT NULL,
                study_year INTEGER NOT NULL DEFAULT 1,
                semester TEXT NOT NULL DEFAULT 'Semester I',
                status TEXT NOT NULL DEFAULT 'Active',
                photo_path TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS applications (
                application_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL DEFAULT '',
                campus TEXT NOT NULL,
                department TEXT NOT NULL,
                program TEXT NOT NULL,
                modality TEXT NOT NULL,
                qualification TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Pending Review',
                submitted_at TEXT NOT NULL,
                reviewed_by TEXT NOT NULL DEFAULT '',
                review_note TEXT NOT NULL DEFAULT '',
                student_id TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS courses (
                course_code TEXT PRIMARY KEY,
                course_name TEXT NOT NULL,
                department TEXT NOT NULL,
                program TEXT NOT NULL,
                level TEXT NOT NULL,
                credit_hours REAL NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS enrollments (
                enrollment_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                course_code TEXT NOT NULL,
                academic_year TEXT NOT NULL,
                semester TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(student_id, course_code, academic_year, semester),
                FOREIGN KEY(student_id) REFERENCES students(student_id),
                FOREIGN KEY(course_code) REFERENCES courses(course_code)
            );

            CREATE TABLE IF NOT EXISTS grades (
                grade_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                course_code TEXT NOT NULL,
                course_name TEXT NOT NULL,
                credit_hours REAL NOT NULL,
                score REAL NOT NULL,
                letter_grade TEXT NOT NULL,
                grade_point REAL NOT NULL,
                academic_year TEXT NOT NULL,
                semester TEXT NOT NULL,
                instructor TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                submitted_at TEXT NOT NULL,
                approved_by TEXT NOT NULL DEFAULT '',
                approved_at TEXT NOT NULL DEFAULT '',
                FOREIGN KEY(student_id) REFERENCES students(student_id)
            );

            CREATE TABLE IF NOT EXISTS finance (
                finance_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL UNIQUE,
                total_fee REAL NOT NULL DEFAULT 0,
                amount_paid REAL NOT NULL DEFAULT 0,
                last_updated TEXT NOT NULL,
                notes TEXT NOT NULL DEFAULT '',
                FOREIGN KEY(student_id) REFERENCES students(student_id)
            );

            CREATE TABLE IF NOT EXISTS payments (
                payment_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                amount REAL NOT NULL,
                payment_method TEXT NOT NULL,
                receipt_number TEXT NOT NULL UNIQUE,
                received_by TEXT NOT NULL,
                payment_date TEXT NOT NULL,
                notes TEXT NOT NULL DEFAULT '',
                FOREIGN KEY(student_id) REFERENCES students(student_id)
            );

            CREATE TABLE IF NOT EXISTS announcements (
                notice_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                published INTEGER NOT NULL DEFAULT 1,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS credentials (
                credential_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                document_type TEXT NOT NULL,
                verification_code TEXT NOT NULL UNIQUE,
                issued_by TEXT NOT NULL,
                issued_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Issued',
                FOREIGN KEY(student_id) REFERENCES students(student_id)
            );

            CREATE TABLE IF NOT EXISTS audit_events (
                event_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                event_time TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_students_campus
                ON students(campus);
            CREATE INDEX IF NOT EXISTS idx_students_department
                ON students(department);
            CREATE INDEX IF NOT EXISTS idx_grades_student
                ON grades(student_id);
            CREATE INDEX IF NOT EXISTS idx_applications_status
                ON applications(status);
            """
        )

        # Initial bootstrap account. Change the password immediately.
        admin = conn.execute(
            "SELECT username FROM users WHERE username = ?",
            ("admin",),
        ).fetchone()

        if not admin:
            bootstrap_password = os.getenv("HANEK_BOOTSTRAP_PASSWORD", "")
            if not bootstrap_password:
                bootstrap_password = secrets.token_urlsafe(18)
                logging.warning(
                    "A one-time administrator bootstrap password was "
                    "generated. Configure HANEK_BOOTSTRAP_PASSWORD "
                    "as a deployment secret to set a known password."
                )

            conn.execute(
                """
                INSERT INTO users (
                    username, password_hash, full_name, role,
                    campus, department, email, active,
                    must_change_password, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, 1, ?)
                """,
                (
                    "admin",
                    hash_password(bootstrap_password),
                    "System Administrator",
                    "System Administrator",
                    "All Campuses",
                    "Office of the Registrar",
                    "",
                    now_string(),
                ),
            )

            # Do not display or write bootstrap passwords into application
            # pages or ordinary logs. Set the environment secret securely.
            st.session_state["_bootstrap_created"] = True

        for key, value in {
            "institution_name": APP_NAME,
            "institution_address": "Wolaita Sodo, Ethiopia",
            "po_box": "23",
            "telephone": "+251-46-180-3164",
            "email": "",
            "website": "",
        }.items():
            conn.execute(
                """
                INSERT OR IGNORE INTO settings(setting_key, setting_value)
                VALUES (?, ?)
                """,
                (key, value),
            )


init_database()


def log_event(action, details=""):
    username = str(st.session_state.get("username", "anonymous"))
    with db_connection() as conn:
        conn.execute(
            """
            INSERT INTO audit_events
                (event_id, username, action, details, event_time)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                make_id("AUD"),
                username,
                action,
                str(details)[:500],
                now_string(),
            ),
        )
    audit(action, details)


def query_df(sql, params=()):
    with db_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)


def query_one(sql, params=()):
    with db_connection() as conn:
        return conn.execute(sql, params).fetchone()


def execute(sql, params=()):
    with db_connection() as conn:
        conn.execute(sql, params)


def get_setting(key, default=""):
    row = query_one(
        "SELECT setting_value FROM settings WHERE setting_key = ?",
        (key,),
    )
    return row["setting_value"] if row else default


def set_setting(key, value):
    execute(
        """
        INSERT INTO settings(setting_key, setting_value)
        VALUES (?, ?)
        ON CONFLICT(setting_key)
        DO UPDATE SET setting_value = excluded.setting_value
        """,
        (key, str(value)),
    )


def get_departments():
    defaults = DEFAULT_DEPARTMENTS
    row = query_one(
        "SELECT setting_value FROM settings WHERE setting_key = ?",
        ("departments",),
    )
    if row:
        try:
            values = json.loads(row["setting_value"])
            if isinstance(values, list) and values:
                return values
        except (json.JSONDecodeError, TypeError):
            pass
    return defaults


def get_programs():
    row = query_one(
        "SELECT setting_value FROM settings WHERE setting_key = ?",
        ("programs",),
    )
    if row:
        try:
            values = json.loads(row["setting_value"])
            if isinstance(values, list) and values:
                return values
        except (json.JSONDecodeError, TypeError):
            pass
    return DEFAULT_PROGRAMS


# ============================================================
# 4. PRESENTATION AND ACCESS CONTROL
# ============================================================

st.markdown(
    """
    <style>
    :root { color-scheme: light; }
    .stApp {
        background: linear-gradient(180deg, #f5f8fc 0%, #edf3fa 100%);
        color: #17243b;
    }
    h1, h2, h3 {
        color: #102c55 !important;
        letter-spacing: -0.3px;
    }
    [data-testid="stSidebar"] {
        background: #102c55;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #17243b;
    }
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #dce5f0;
        padding: 16px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(16,44,85,.05);
    }
    div.stButton > button, div.stFormSubmitButton > button {
        border-radius: 9px;
        font-weight: 650;
        min-height: 42px;
    }
    div[data-testid="stForm"] {
        background: rgba(255,255,255,.88);
        border: 1px solid #dce5f0;
        border-radius: 14px;
        padding: 18px;
    }
    .hero {
        padding: 28px;
        border-radius: 18px;
        background: linear-gradient(115deg, #102c55, #1d5da8);
        color: white;
        margin-bottom: 18px;
        box-shadow: 0 12px 30px rgba(16,44,85,.15);
    }
    .hero h1, .hero h2, .hero p { color: white !important; }
    .small-muted { color: #64748b; font-size: .88rem; }
    .notice {
        background: white;
        padding: 18px;
        margin: 10px 0;
        border-radius: 12px;
        border-left: 5px solid #1d5da8;
        box-shadow: 0 4px 12px rgba(16,44,85,.04);
    }
    @media print {
        [data-testid="stSidebar"], header, footer,
        .stButton, .stFormSubmitButton {
            display: none !important;
        }
        .stApp { background: white !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def is_logged_in():
    return bool(
        st.session_state.get("authenticated")
        and st.session_state.get("username")
    )


def has_role(*allowed_roles):
    return is_logged_in() and (
        st.session_state.get("role") in allowed_roles
        or st.session_state.get("role") == "System Administrator"
    )


def campus_allowed(campus):
    user_campus = st.session_state.get("campus", "All Campuses")
    return user_campus == "All Campuses" or user_campus == campus


def login_form():
    st.markdown(
        f"""
        <div class="hero">
            <h1>🎓 {safe_text(APP_NAME)}</h1>
            <p>Secure Academic, Admissions and Registrar Portal</p>
            <p>Student records • Academic results • Institutional services</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Institutional Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button(
            "Sign In Securely",
            use_container_width=True,
        )

    if not submitted:
        return

    if st.session_state.get("login_locked_until", 0) > datetime.now().timestamp():
        st.error("Access is temporarily restricted. Please try again later.")
        return

    row = query_one(
        """
        SELECT username, password_hash, full_name, role, campus,
               department, active, must_change_password
        FROM users WHERE username = ?
        """,
        (username.strip(),),
    )

    if (
        row
        and row["active"] == 1
        and verify_password(password, row["password_hash"])
    ):
        # Upgrade any legacy plaintext password on successful login.
        if not row["password_hash"].startswith("pbkdf2_sha256$"):
            execute(
                "UPDATE users SET password_hash = ?, "
                "must_change_password = 1 WHERE username = ?",
                (hash_password(password), username.strip()),
            )

        st.session_state["authenticated"] = True
        st.session_state["username"] = row["username"]
        st.session_state["display_name"] = row["full_name"]
        st.session_state["role"] = row["role"]
        st.session_state["campus"] = row["campus"]
        st.session_state["department"] = row["department"]
        st.session_state["login_attempts"] = 0
        log_event("LOGIN_SUCCESS")
        st.rerun()
    else:
        attempts = int(st.session_state.get("login_attempts", 0)) + 1
        st.session_state["login_attempts"] = attempts
        if attempts >= 5:
            st.session_state["login_locked_until"] = (
                datetime.now().timestamp() + 300
            )
            st.session_state["login_attempts"] = 0
        log_event("LOGIN_FAILURE", "Invalid credentials")
        st.error("The supplied credentials are invalid or the account is inactive.")


def logout():
    log_event("LOGOUT")
    for key in [
        "authenticated",
        "username",
        "display_name",
        "role",
        "campus",
        "department",
        "student_view_id",
    ]:
        st.session_state.pop(key, None)
    st.rerun()


# ============================================================
# 5. REUSABLE DATA FUNCTIONS
# ============================================================

def get_student(student_id):
    return query_one(
        "SELECT * FROM students WHERE student_id = ?",
        (student_id,),
    )


def student_options(campus_filter=True):
    sql = """
        SELECT student_id, full_name, campus
        FROM students WHERE status != 'Withdrawn'
    """
    params = []
    if campus_filter and st.session_state.get("campus") != "All Campuses":
        sql += " AND campus = ?"
        params.append(st.session_state["campus"])
    sql += " ORDER BY full_name"

    df = query_df(sql, tuple(params))
    return {
        f"{r.student_id} — {r.full_name} ({r.campus})": r.student_id
        for r in df.itertuples()
    }


def register_student(
    student_id,
    full_name,
    campus,
    department,
    program,
    modality,
    admission_year,
    phone="",
    email="",
    sex="",
    date_of_birth="",
    address="",
):
    execute(
        """
        INSERT INTO students (
            student_id, full_name, sex, date_of_birth, phone, email,
            address, campus, department, program, modality,
            admission_year, study_year, semester, status,
            photo_path, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1,
                  'Semester I', 'Active', '', ?)
        """,
        (
            student_id.strip(),
            full_name.strip(),
            sex,
            date_of_birth,
            phone.strip(),
            email.strip(),
            address.strip(),
            campus,
            department,
            program,
            modality,
            int(admission_year),
            now_string(),
        ),
    )


def current_balance(student_id):
    row = query_one(
        """
        SELECT total_fee, amount_paid FROM finance
        WHERE student_id = ?
        """,
        (student_id,),
    )
    if not row:
        return None
    return max(0.0, float(row["total_fee"]) - float(row["amount_paid"]))


def grade_summary(student_id):
    df = query_df(
        """
        SELECT credit_hours, grade_point, score
        FROM grades
        WHERE student_id = ? AND status = 'Approved'
        """,
        (student_id,),
    )
    if df.empty:
        return 0.0, 0, 0.0

    credits = pd.to_numeric(df["credit_hours"], errors="coerce").fillna(0)
    points = pd.to_numeric(df["grade_point"], errors="coerce").fillna(0)
    total_credits = float(credits.sum())
    quality_points = float((credits * points).sum())
    cgpa = quality_points / total_credits if total_credits > 0 else 0.0
    return cgpa, len(df), total_credits


def download_df(df, filename, label="Download CSV"):
    st.download_button(
        label,
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# 6. PUBLIC PORTAL
# ============================================================

def render_public_portal():
    st.markdown(
        f"""
        <div class="hero">
            <h1>🎓 {safe_text(get_setting('institution_name', APP_NAME))}</h1>
            <p><strong>Official Multi-Campus Academic and Student Services Portal</strong></p>
            <p>Advancing professional competence, academic integrity and lifelong learning.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Institutional Overview")
    st.write(
        "The institutional portal provides access to admissions information, "
        "academic notices and student services across the college's campuses. "
        "Applicants and students should consult the Registrar for official "
        "admission requirements, academic regulations and credential verification."
    )

    campus_cols = st.columns(4)
    for col, campus in zip(campus_cols, CAMPUSES):
        with col:
            st.markdown(f"**📍 {campus} Campus**")

    st.markdown("---")
    st.subheader("Public Announcements")

    notices = query_df(
        """
        SELECT title, category, content, created_at
        FROM announcements WHERE published = 1
        ORDER BY created_at DESC
        """
    )
    if notices.empty:
        st.info("No public announcements have been published.")
    else:
        for item in notices.itertuples():
            st.markdown(
                f"""
                <div class="notice">
                    <strong>{safe_text(item.title)}</strong>
                    <div class="small-muted">
                        {safe_text(item.category)} · {safe_text(item.created_at)}
                    </div>
                    <p>{safe_text(item.content)}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.subheader("Online Admission Application")

    with st.form("public_application", clear_on_submit=True):
        a1, a2 = st.columns(2)
        with a1:
            app_name = st.text_input("Full Legal Name *")
            app_phone = st.text_input("Telephone Number *")
            app_email = st.text_input("Email Address")
            app_campus = st.selectbox("Preferred Campus", CAMPUSES)
        with a2:
            app_dept = st.selectbox("Department", get_departments())
            app_program = st.selectbox("Program", get_programs())
            app_modality = st.selectbox("Study Modality", MODALITIES)
            qualification = st.text_input("Previous Qualification")

        consent = st.checkbox(
            "I confirm that the information supplied is accurate and may "
            "be used for admissions processing."
        )
        submit_app = st.form_submit_button(
            "Submit Admission Application",
            use_container_width=True,
        )

    if submit_app:
        if not app_name.strip() or not app_phone.strip():
            st.error("The full legal name and telephone number are required.")
        elif app_email.strip() and not valid_email(app_email):
            st.error("Please provide a valid email address.")
        elif not consent:
            st.error("Please confirm the accuracy of the submitted information.")
        else:
            app_id = make_id("APP")
            execute(
                """
                INSERT INTO applications (
                    application_id, full_name, phone, email, campus,
                    department, program, modality, qualification,
                    status, submitted_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending Review', ?)
                """,
                (
                    app_id,
                    app_name.strip(),
                    app_phone.strip(),
                    app_email.strip(),
                    app_campus,
                    app_dept,
                    app_program,
                    app_modality,
                    qualification.strip(),
                    now_string(),
                ),
            )
            log_event("APPLICATION_SUBMITTED", app_id)
            st.success(
                f"Your application has been recorded. Reference number: {app_id}. "
                "Retain this reference for future correspondence."
            )

    st.markdown("---")
    st.subheader("Institutional Contact Information")
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Address:** {get_setting('institution_address')}")
        st.write(f"**P.O. Box:** {get_setting('po_box')}")
        st.write(f"**Telephone:** {get_setting('telephone')}")
    with c2:
        st.write(f"**Email:** {get_setting('email') or 'Contact the Registrar'}")
        st.write(f"**Website:** {get_setting('website') or 'Not configured'}")

    st.caption(
        "Official admissions decisions and academic credentials are subject "
        "to institutional verification and applicable regulations."
    )


# ============================================================
# 7. ADMINISTRATOR DASHBOARD
# ============================================================

def render_admin_dashboard():
    st.title("Institutional Administration Dashboard")
    st.caption(
        f"Academic Year: {academic_year()} | "
        f"Campus Scope: {st.session_state['campus']}"
    )

    total_students = query_one("SELECT COUNT(*) AS n FROM students")["n"]
    active_students = query_one(
        "SELECT COUNT(*) AS n FROM students WHERE status = 'Active'"
    )["n"]
    pending_apps = query_one(
        "SELECT COUNT(*) AS n FROM applications "
        "WHERE status IN ('Pending Review', 'Under Review')"
    )["n"]
    pending_grades = query_one(
        "SELECT COUNT(*) AS n FROM grades WHERE status = 'Pending'"
    )["n"]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Students", f"{total_students:,}")
    m2.metric("Active Students", f"{active_students:,}")
    m3.metric("Applications Awaiting Review", f"{pending_apps:,}")
    m4.metric("Grades Awaiting Approval", f"{pending_grades:,}")

    tabs = st.tabs(
        [
            "Student Records",
            "Admissions",
            "Staff Accounts",
            "Courses",
            "Grade Management",
            "Finance",
            "Announcements",
            "Credentials",
            "Reports",
            "System Settings",
        ]
    )

    # ---------------- STUDENT RECORDS ----------------
    with tabs[0]:
        st.subheader("Student Records Management")
        search = st.text_input(
            "Search by student ID, name, department or campus",
            key="admin_student_search",
        )
        students = query_df(
            """
            SELECT student_id AS 'Student ID',
                   full_name AS 'Full Name',
                   campus AS Campus,
                   department AS Department,
                   program AS Program,
                   modality AS Modality,
                   admission_year AS 'Admission Year',
                   study_year AS 'Study Year',
                   status AS Status
            FROM students ORDER BY created_at DESC
            """
        )
        if search.strip():
            mask = students.astype(str).apply(
                lambda col: col.str.contains(
                    search.strip(), case=False, na=False
                )
            ).any(axis=1)
            students = students[mask]

        if not students.empty:
            st.dataframe(students, use_container_width=True, hide_index=True)
            download_df(students, "hanek_student_records.csv")
        else:
            st.info("No matching student records were found.")

        with st.expander("Register a New Student", expanded=False):
            with st.form("register_student_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    sid = st.text_input("Student Identification Number *")
                    name = st.text_input("Full Legal Name *")
                    sex = st.selectbox(
                        "Sex",
                        ["Not Specified", "Female", "Male"],
                    )
                    dob = st.text_input("Date of Birth (YYYY-MM-DD)")
                    phone = st.text_input("Telephone Number")
                    email = st.text_input("Email Address")
                with c2:
                    campus = st.selectbox("Campus", CAMPUSES)
                    dept = st.selectbox("Department", get_departments())
                    program = st.selectbox("Program", get_programs())
                    modality = st.selectbox("Study Modality", MODALITIES)
                    adm_year = st.number_input(
                        "Admission Year",
                        min_value=1990,
                        max_value=CURRENT_YEAR + 2,
                        value=CURRENT_YEAR,
                    )
                    address = st.text_input("Postal / Residential Address")

                submit_student = st.form_submit_button(
                    "Create Student Record",
                    use_container_width=True,
                )

            if submit_student:
                if not sid.strip() or not name.strip():
                    st.error("The student ID and full legal name are required.")
                elif email.strip() and not valid_email(email):
                    st.error("Enter a valid email address.")
                elif get_student(sid.strip()):
                    st.error("This student identification number already exists.")
                else:
                    try:
                        register_student(
                            sid, name, campus, dept, program, modality,
                            adm_year, phone, email,
                            "" if sex == "Not Specified" else sex,
                            dob, address,
                        )
                        log_event("STUDENT_CREATED", sid)
                        st.success("The student record has been created.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("The student record could not be saved.")

        with st.expander("Update Student Status", expanded=False):
            ids = student_options()
            if ids:
                selected = st.selectbox(
                    "Select Student",
                    list(ids.keys()),
                    key="update_student_status_select",
                )
                selected_id = ids[selected]
                existing = get_student(selected_id)
                status_choices = [
                    "Active", "Graduated", "Suspended", "Withdrawn", "Deferred"
                ]
                with st.form("update_student_status_form"):
                    new_status = st.selectbox(
                        "New Status",
                        status_choices,
                        index=(
                            status_choices.index(existing["status"])
                            if existing["status"] in status_choices
                            else 0
                        ),
                    )
                    new_year = st.number_input(
                        "Current Study Year",
                        min_value=1,
                        max_value=10,
                        value=int(existing["study_year"]),
                    )
                    save_status = st.form_submit_button("Save Changes")
                if save_status:
                    execute(
                        """
                        UPDATE students SET status = ?, study_year = ?
                        WHERE student_id = ?
                        """,
                        (new_status, int(new_year), selected_id),
                    )
                    log_event("STUDENT_UPDATED", selected_id)
                    st.success("Student information has been updated.")
                    st.rerun()
            else:
                st.info("No students are available for modification.")

    # ---------------- ADMISSIONS ----------------
    with tabs[1]:
        st.subheader("Admissions and Application Review")
        apps = query_df(
            """
            SELECT application_id AS 'Application Reference',
                   full_name AS 'Applicant Name',
                   phone AS Telephone,
                   email AS Email,
                   campus AS Campus,
                   department AS Department,
                   program AS Program,
                   modality AS Modality,
                   status AS Status,
                   submitted_at AS 'Submitted At'
            FROM applications ORDER BY submitted_at DESC
            """
        )
        st.dataframe(apps, use_container_width=True, hide_index=True)
        download_df(apps, "hanek_admissions.csv")

        pending = query_df(
            """
            SELECT application_id, full_name, phone, email, campus,
                   department, program, modality, qualification, status
            FROM applications
            WHERE status IN ('Pending Review', 'Under Review', 'Waitlisted')
            ORDER BY submitted_at
            """
        )
        if not pending.empty:
            app_map = {
                f"{r.application_id} — {r.full_name}": r.application_id
                for r in pending.itertuples()
            }
            selected_label = st.selectbox(
                "Select an Application for Review",
                list(app_map.keys()),
            )
            selected_app = app_map[selected_label]
            app_row = query_one(
                "SELECT * FROM applications WHERE application_id = ?",
                (selected_app,),
            )
            with st.form("application_review_form"):
                review_status = st.selectbox(
                    "Decision",
                    ["Under Review", "Admitted", "Rejected", "Waitlisted"],
                )
                review_note = st.text_area("Review Notes")
                review_submit = st.form_submit_button("Save Review Decision")
            if review_submit:
                execute(
                    """
                    UPDATE applications
                    SET status = ?, reviewed_by = ?, review_note = ?
                    WHERE application_id = ?
                    """,
                    (
                        review_status,
                        st.session_state["username"],
                        review_note.strip(),
                        selected_app,
                    ),
                )
                log_event("APPLICATION_REVIEWED", selected_app)

                if review_status == "Admitted":
                    st.info(
                        "The application is marked as admitted. Create the "
                        "official student record in Student Records after "
                        "confirming the admission documents."
                    )
                else:
                    st.success("The application decision has been saved.")
                st.rerun()
        else:
            st.info("There are no applications awaiting review.")

    # ---------------- STAFF ACCOUNTS ----------------
    with tabs[2]:
        st.subheader("Staff Directory and Access Management")
        staff = query_df(
            """
            SELECT username AS Username, full_name AS 'Full Name',
                   role AS Role, campus AS Campus,
                   department AS Department, email AS Email,
                   active AS Active
            FROM users ORDER BY full_name
            """
        )
        st.dataframe(staff, use_container_width=True, hide_index=True)

        with st.expander("Create Staff Account"):
            with st.form("create_staff_account_form", clear_on_submit=True):
                staff_user = st.text_input("Username *")
                staff_name = st.text_input("Full Name *")
                staff_email = st.text_input("Institutional Email")
                staff_role = st.selectbox("Institutional Role", STAFF_ROLES)
                staff_campus = st.selectbox(
                    "Authorized Campus",
                    ["All Campuses"] + CAMPUSES,
                )
                staff_dept = st.selectbox(
                    "Department / Unit",
                    get_departments() + ["Office of the Registrar", "Finance"],
                )
                staff_temp_password = st.text_input(
                    "Temporary Password *", type="password"
                )
                create_staff = st.form_submit_button("Create Staff Account")

            if create_staff:
                if (
                    not staff_user.strip()
                    or not staff_name.strip()
                    or len(staff_temp_password) < 12
                ):
                    st.error(
                        "Provide a username, full name and temporary password "
                        "of at least 12 characters."
                    )
                elif staff_email.strip() and not valid_email(staff_email):
                    st.error("Enter a valid institutional email address.")
                elif query_one(
                    "SELECT username FROM users WHERE username = ?",
                    (staff_user.strip(),),
                ):
                    st.error("This username is already in use.")
                else:
                    execute(
                        """
                        INSERT INTO users (
                            username, password_hash, full_name, role,
                            campus, department, email, active,
                            must_change_password, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, 1, ?)
                        """,
                        (
                            staff_user.strip(),
                            hash_password(staff_temp_password),
                            staff_name.strip(),
                            staff_role,
                            staff_campus,
                            staff_dept,
                            staff_email.strip(),
                            now_string(),
                        ),
                    )
                    log_event("STAFF_ACCOUNT_CREATED", staff_user)
                    st.success("The staff account has been created.")
                    st.rerun()

        with st.expander("Activate, Deactivate or Reset an Account"):
            user_list = query_df(
                "SELECT username, full_name FROM users ORDER BY username"
            )
            if not user_list.empty:
                user_options = {
                    f"{r.username} — {r.full_name}": r.username
                    for r in user_list.itertuples()
                }
                target_label = st.selectbox(
                    "Select Account", list(user_options.keys())
                )
                target_user = user_options[target_label]
                account = query_one(
                    "SELECT * FROM users WHERE username = ?",
                    (target_user,),
                )
                with st.form("account_admin_form"):
                    active_state = st.selectbox(
                        "Account Status",
                        ["Active", "Inactive"],
                        index=0 if account["active"] else 1,
                    )
                    reset_password = st.text_input(
                        "New Temporary Password (optional)",
                        type="password",
                    )
                    apply_account_change = st.form_submit_button("Apply Changes")
                if apply_account_change:
                    execute(
                        """
                        UPDATE users SET active = ? WHERE username = ?
                        """,
                        (1 if active_state == "Active" else 0, target_user),
                    )
                    if reset_password:
                        if len(reset_password) < 12:
                            st.error(
                                "The new temporary password must contain at "
                                "least 12 characters."
                            )
                        else:
                            execute(
                                """
                                UPDATE users
                                SET password_hash = ?, must_change_password = 1
                                WHERE username = ?
                                """,
                                (hash_password(reset_password), target_user),
                            )
                    log_event("STAFF_ACCOUNT_UPDATED", target_user)
                    st.success("Account settings have been updated.")
                    st.rerun()

    # ---------------- COURSES ----------------
    with tabs[3]:
        st.subheader("Course Catalogue and Curriculum")
        course_df = query_df(
            """
            SELECT course_code AS 'Course Code',
                   course_name AS 'Course Name',
                   department AS Department,
                   program AS Program,
                   level AS Level,
                   credit_hours AS 'Credit Hours',
                   active AS Active
            FROM courses ORDER BY department, course_name
            """
        )
        st.dataframe(course_df, use_container_width=True, hide_index=True)
        download_df(course_df, "hanek_course_catalogue.csv")

        with st.expander("Add a Course"):
            with st.form("add_course_form", clear_on_submit=True):
                cc1, cc2 = st.columns(2)
                with cc1:
                    course_code = st.text_input("Course Code *")
                    course_name = st.text_input("Course Title *")
                    course_credits = st.number_input(
                        "Credit Hours", min_value=0.5, max_value=30.0, value=3.0
                    )
                with cc2:
                    course_dept = st.selectbox(
                        "Department", get_departments()
                    )
                    course_program = st.selectbox(
                        "Program", get_programs()
                    )
                    course_level = st.selectbox(
                        "Level",
                        [
                            "TVET Level I", "TVET Level II",
                            "TVET Level III", "TVET Level IV",
                            "Year I", "Year II", "Year III", "Year IV",
                        ],
                    )
                add_course = st.form_submit_button("Save Course")

            if add_course:
                if not course_code.strip() or not course_name.strip():
                    st.error("Course code and course title are required.")
                elif query_one(
                    "SELECT course_code FROM courses WHERE course_code = ?",
                    (course_code.strip().upper(),),
                ):
                    st.error("This course code already exists.")
                else:
                    execute(
                        """
                        INSERT INTO courses (
                            course_code, course_name, department, program,
                            level, credit_hours
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            course_code.strip().upper(),
                            course_name.strip(),
                            course_dept,
                            course_program,
                            course_level,
                            float(course_credits),
                        ),
                    )
                    log_event("COURSE_CREATED", course_code)
                    st.success("The course has been added.")
                    st.rerun()

    # ---------------- GRADES ----------------
    with tabs[4]:
        st.subheader("Assessment, Grade Approval and Academic Records")
        grades = query_df(
            """
            SELECT grade_id AS 'Grade Reference',
                   student_id AS 'Student ID',
                   course_code AS 'Course Code',
                   course_name AS 'Course Name',
                   credit_hours AS 'Credit Hours',
                   score AS Score,
                   letter_grade AS Grade,
                   grade_point AS 'Grade Point',
                   academic_year AS 'Academic Year',
                   semester AS Semester,
                   instructor AS Instructor,
                   status AS Status
            FROM grades ORDER BY submitted_at DESC
            """
        )
        st.dataframe(grades, use_container_width=True, hide_index=True)
        download_df(grades, "hanek_grade_records.csv")

        pending = query_df(
            "SELECT grade_id, student_id, course_code, course_name, score, "
            "status FROM grades WHERE status = 'Pending' "
            "ORDER BY submitted_at"
        )
        if not pending.empty:
            grade_options = {
                f"{r.grade_id} — {r.student_id} — {r.course_code} "
                f"({r.score})": r.grade_id
                for r in pending.itertuples()
            }
            selected_grade_label = st.selectbox(
                "Select a Grade Submission for Review",
                list(grade_options.keys()),
            )
            selected_grade = grade_options[selected_grade_label]
            grade_decision = st.radio(
                "Review Decision",
                ["Approve", "Reject"],
                horizontal=True,
            )
            if st.button("Confirm Grade Decision", type="primary"):
                execute(
                    """
                    UPDATE grades
                    SET status = ?, approved_by = ?, approved_at = ?
                    WHERE grade_id = ? AND status = 'Pending'
                    """,
                    (
                        "Approved" if grade_decision == "Approve" else "Rejected",
                        st.session_state["username"],
                        now_string(),
                        selected_grade,
                    ),
                )
                log_event("GRADE_REVIEWED", selected_grade)
                st.success("The grade review decision has been recorded.")
                st.rerun()
        else:
            st.info("No grade submissions are awaiting review.")

    # ---------------- FINANCE ----------------
    with tabs[5]:
        st.subheader("Student Accounts, Payments and Financial Clearance")
        finance_df = query_df(
            """
            SELECT f.student_id AS 'Student ID',
                   s.full_name AS 'Student Name',
                   s.campus AS Campus,
                   f.total_fee AS 'Total Fee (ETB)',
                   f.amount_paid AS 'Amount Paid (ETB)',
                   MAX(f.total_fee - f.amount_paid, 0)
                       AS 'Outstanding Balance (ETB)',
                   f.last_updated AS 'Last Updated'
            FROM finance f JOIN students s ON s.student_id = f.student_id
            ORDER BY s.full_name
            """
        )
        st.dataframe(finance_df, use_container_width=True, hide_index=True)
        download_df(finance_df, "hanek_financial_accounts.csv")

        ids = student_options()
        if ids:
            with st.expander("Set or Update a Student Fee Account"):
                with st.form("finance_account_form"):
                    selected_finance_label = st.selectbox(
                        "Student", list(ids.keys())
                    )
                    total_fee = st.number_input(
                        "Total Approved Fee (ETB)",
                        min_value=0.0,
                        value=15000.0,
                        step=500.0,
                    )
                    finance_notes = st.text_area("Administrative Notes")
                    save_fee = st.form_submit_button("Save Fee Account")
                if save_fee:
                    selected_finance_id = ids[selected_finance_label]
                    execute(
                        """
                        INSERT INTO finance (
                            finance_id, student_id, total_fee,
                            amount_paid, last_updated, notes
                        ) VALUES (?, ?, ?, 0, ?, ?)
                        ON CONFLICT(student_id) DO UPDATE SET
                            total_fee = excluded.total_fee,
                            last_updated = excluded.last_updated,
                            notes = excluded.notes
                        """,
                        (
                            make_id("FIN"),
                            selected_finance_id,
                            float(total_fee),
                            now_string(),
                            finance_notes.strip(),
                        ),
                    )
                    log_event("FINANCE_ACCOUNT_UPDATED", selected_finance_id)
                    st.success("The fee account has been updated.")
                    st.rerun()

            with st.expander("Record a Payment"):
                with st.form("record_payment_form", clear_on_submit=True):
                    payment_student_label = st.selectbox(
                        "Student", list(ids.keys()), key="payment_student"
                    )
                    payment_amount = st.number_input(
                        "Payment Amount (ETB)",
                        min_value=0.01,
                        value=1000.0,
                        step=100.0,
                    )
                    payment_method = st.selectbox(
                        "Payment Method",
                        ["Bank Transfer", "Cash", "Mobile Payment", "Other"],
                    )
                    receipt_number = st.text_input("Unique Receipt Number")
                    payment_notes = st.text_area("Payment Notes")
                    record_payment = st.form_submit_button("Record Payment")

                if record_payment:
                    sid = ids[payment_student_label]
                    balance = current_balance(sid)
                    if balance is None:
                        st.error(
                            "Create a fee account for this student before "
                            "recording payments."
                        )
                    elif payment_amount > balance:
                        st.error(
                            "The payment exceeds the recorded outstanding balance."
                        )
                    elif not receipt_number.strip():
                        st.error("A receipt number is required.")
                    elif query_one(
                        "SELECT payment_id FROM payments WHERE receipt_number = ?",
                        (receipt_number.strip(),),
                    ):
                        st.error("This receipt number has already been recorded.")
                    else:
                        with db_connection() as conn:
                            conn.execute(
                                """
                                INSERT INTO payments (
                                    payment_id, student_id, amount,
                                    payment_method, receipt_number,
                                    received_by, payment_date, notes
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    make_id("PAY"),
                                    sid,
                                    float(payment_amount),
                                    payment_method,
                                    receipt_number.strip(),
                                    st.session_state["username"],
                                    now_string(),
                                    payment_notes.strip(),
                                ),
                            )
                            conn.execute(
                                """
                                UPDATE finance
                                SET amount_paid = amount_paid + ?,
                                    last_updated = ?
                                WHERE student_id = ?
                                """,
                                (float(payment_amount), now_string(), sid),
                            )
                        log_event("PAYMENT_RECORDED", receipt_number)
                        st.success("The payment has been recorded.")
                        st.rerun()

        payments = query_df(
            """
            SELECT payment_id AS 'Payment Reference',
                   student_id AS 'Student ID',
                   amount AS 'Amount (ETB)',
                   payment_method AS 'Method',
                   receipt_number AS 'Receipt Number',
                   received_by AS 'Received By',
                   payment_date AS 'Payment Date'
            FROM payments ORDER BY payment_date DESC
            """
        )
        st.markdown("#### Payment Register")
        st.dataframe(payments, use_container_width=True, hide_index=True)

    # ---------------- ANNOUNCEMENTS ----------------
    with tabs[6]:
        st.subheader("Academic Notices and Institutional Communication")
        notices = query_df(
            """
            SELECT notice_id AS 'Notice ID', title AS Title,
                   category AS Category, content AS Content,
                   published AS Published, created_by AS 'Created By',
                   created_at AS 'Created At'
            FROM announcements ORDER BY created_at DESC
            """
        )
        st.dataframe(notices, use_container_width=True, hide_index=True)

        with st.expander("Publish an Announcement"):
            with st.form("publish_notice_form", clear_on_submit=True):
                notice_title = st.text_input("Announcement Title")
                notice_category = st.selectbox(
                    "Category", NOTICE_CATEGORIES
                )
                notice_content = st.text_area("Announcement Content")
                publish_notice = st.checkbox(
                    "Publish immediately", value=True
                )
                save_notice = st.form_submit_button("Save Announcement")
            if save_notice:
                if not notice_title.strip() or not notice_content.strip():
                    st.error("A title and announcement content are required.")
                else:
                    execute(
                        """
                        INSERT INTO announcements (
                            notice_id, title, category, content,
                            published, created_by, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            make_id("NOT"),
                            notice_title.strip(),
                            notice_category,
                            notice_content.strip(),
                            1 if publish_notice else 0,
                            st.session_state["username"],
                            now_string(),
                        ),
                    )
                    log_event("ANNOUNCEMENT_CREATED", notice_title)
                    st.success("The announcement has been saved.")
                    st.rerun()

    # ---------------- CREDENTIALS ----------------
    with tabs[7]:
        st.subheader("Official Academic Credential Register")
        st.warning(
            "Issue official credentials only after verifying the student's "
            "academic record, programme requirements and applicable financial "
            "and institutional clearance rules."
        )

        ids = student_options()
        if ids:
            credential_student_label = st.selectbox(
                "Student", list(ids.keys()), key="credential_student"
            )
            credential_sid = ids[credential_student_label]
            s = get_student(credential_sid)
            cgpa, modules, credits = grade_summary(credential_sid)
            balance = current_balance(credential_sid)

            c1, c2, c3 = st.columns(3)
            c1.metric("Approved Course Records", modules)
            c2.metric("Credit Hours", f"{credits:.1f}")
            c3.metric("Cumulative GPA", f"{cgpa:.2f}")

            if balance is None:
                st.warning(
                    "No financial account exists. Clearance must be verified "
                    "manually before issuing a credential."
                )
            else:
                st.metric("Outstanding Balance (ETB)", f"{balance:,.2f}")

            with st.form("issue_credential_form"):
                document_type = st.selectbox(
                    "Document Type",
                    [
                        "Academic Transcript",
                        "Statement of Results",
                        "Enrollment Verification",
                        "Graduation Credential",
                        "Certificate of Good Standing",
                    ],
                )
                clearance_confirmed = st.checkbox(
                    "I have verified the academic and administrative "
                    "requirements for this document."
                )
                issue_document = st.form_submit_button(
                    "Generate Credential Record"
                )

            if issue_document:
                if not clearance_confirmed:
                    st.error("Confirm the required checks before proceeding.")
                elif document_type in [
                    "Graduation Credential", "Academic Transcript"
                ] and balance is None:
                    st.error(
                        "A financial account is missing. Verify clearance "
                        "and establish the account before proceeding."
                    )
                elif document_type == "Graduation Credential" and (
                    balance is not None and balance > 0
                ):
                    st.error(
                        "The outstanding balance must be resolved according "
                        "to institutional policy before issuing this document."
                    )
                else:
                    verification_code = (
                        "HBC-" + secrets.token_hex(8).upper()
                    )
                    credential_id = make_id("CRD")
                    execute(
                        """
                        INSERT INTO credentials (
                            credential_id, student_id, document_type,
                            verification_code, issued_by, issued_at, status
                        ) VALUES (?, ?, ?, ?, ?, ?, 'Issued')
                        """,
                        (
                            credential_id,
                            credential_sid,
                            document_type,
                            verification_code,
                            st.session_state["username"],
                            now_string(),
                        ),
                    )
                    log_event("CREDENTIAL_ISSUED", credential_id)
                    st.success(
                        "The credential register entry has been created. "
                        "Review the student information and institutional "
                        "approval before releasing an official document."
                    )
                    st.code(verification_code)

            if st.button("Preview Academic Record"):
                student_grades = query_df(
                    """
                    SELECT course_code AS 'Course Code',
                           course_name AS 'Course Title',
                           credit_hours AS 'Credit Hours',
                           score AS Score,
                           letter_grade AS Grade,
                           grade_point AS 'Grade Point',
                           academic_year AS 'Academic Year',
                           semester AS Semester
                    FROM grades
                    WHERE student_id = ? AND status = 'Approved'
                    ORDER BY academic_year, semester, course_code
                    """,
                    (credential_sid,),
                )
                st.markdown(f"### {safe_text(APP_NAME)}")
                st.markdown("**OFFICE OF THE REGISTRAR**")
                st.write(f"**Student:** {s['full_name']}")
                st.write(f"**Student ID:** {s['student_id']}")
                st.write(f"**Campus:** {s['campus']}")
                st.write(f"**Department:** {s['department']}")
                st.write(f"**Programme:** {s['program']}")
                st.write(f"**Admission Year:** {s['admission_year']}")
                st.dataframe(
                    student_grades,
                    use_container_width=True,
                    hide_index=True,
                )
                st.info(
                    "This is a preview generated from records in the system. "
                    "It is not, by itself, an authenticated academic transcript "
                    "or graduation certificate."
                )
        else:
            st.info("Student records must be created before credentials can be issued.")

        credentials = query_df(
            """
            SELECT credential_id AS 'Credential ID',
                   student_id AS 'Student ID',
                   document_type AS 'Document Type',
                   verification_code AS 'Verification Code',
                   issued_by AS 'Issued By',
                   issued_at AS 'Issued At',
                   status AS Status
            FROM credentials ORDER BY issued_at DESC
            """
        )
        st.markdown("#### Credential Issuance Register")
        st.dataframe(credentials, use_container_width=True, hide_index=True)

    # ---------------- REPORTS ----------------
    with tabs[8]:
        st.subheader("Institutional Reports and Analytics")

        campus_report = query_df(
            """
            SELECT campus AS Campus,
                   COUNT(*) AS 'Total Students',
                   SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END)
                       AS 'Active Students',
                   SUM(CASE WHEN status = 'Graduated' THEN 1 ELSE 0 END)
                       AS Graduates
            FROM students GROUP BY campus ORDER BY campus
            """
        )
        st.markdown("#### Student Enrolment by Campus")
        st.dataframe(campus_report, use_container_width=True, hide_index=True)
        download_df(campus_report, "hanek_campus_enrolment_report.csv")

        department_report = query_df(
            """
            SELECT department AS Department, COUNT(*) AS 'Student Count'
            FROM students GROUP BY department ORDER BY department
            """
        )
        st.markdown("#### Student Enrolment by Department")
        st.dataframe(
            department_report, use_container_width=True, hide_index=True
        )
        download_df(
            department_report,
            "hanek_department_enrolment_report.csv",
        )

        grade_report = query_df(
            """
            SELECT academic_year AS 'Academic Year',
                   semester AS Semester,
                   COUNT(*) AS 'Approved Grade Records',
                   AVG(score) AS 'Average Score'
            FROM grades WHERE status = 'Approved'
            GROUP BY academic_year, semester
            ORDER BY academic_year, semester
            """
        )
        st.markdown("#### Academic Performance Summary")
        st.dataframe(grade_report, use_container_width=True, hide_index=True)
        download_df(grade_report, "hanek_academic_performance.csv")

        if not campus_report.empty:
            st.bar_chart(
                campus_report.set_index("Campus")["Total Students"]
            )
        if not department_report.empty:
            st.bar_chart(
                department_report.set_index("Department")["Student Count"]
            )

    # ---------------- SYSTEM SETTINGS ----------------
    with tabs[9]:
        st.subheader("Institutional Configuration and Audit")

        with st.form("institution_settings_form"):
            institution_name = st.text_input(
                "Institution Name",
                value=get_setting("institution_name", APP_NAME),
            )
            institution_address = st.text_input(
                "Institutional Address",
                value=get_setting("institution_address", "Wolaita Sodo, Ethiopia"),
            )
            po_box = st.text_input(
                "P.O. Box", value=get_setting("po_box", "23")
            )
            telephone = st.text_input(
                "Telephone", value=get_setting("telephone", "")
            )
            institutional_email = st.text_input(
                "Institutional Email", value=get_setting("email", "")
            )
            website = st.text_input(
                "Institutional Website", value=get_setting("website", "")
            )
            save_settings = st.form_submit_button("Save Institutional Settings")

        if save_settings:
            if institutional_email.strip() and not valid_email(institutional_email):
                st.error("Enter a valid institutional email address.")
            else:
                for key, value in {
                    "institution_name": institution_name,
                    "institution_address": institution_address,
                    "po_box": po_box,
                    "telephone": telephone,
                    "email": institutional_email,
                    "website": website,
                }.items():
                    set_setting(key, value)
                log_event("INSTITUTION_SETTINGS_UPDATED")
                st.success("Institutional settings have been saved.")
                st.rerun()

        st.markdown("#### Department and Programme Configuration")
        with st.form("academic_configuration_form"):
            dept_text = st.text_area(
                "Departments — one per line",
                value="\n".join(get_departments()),
            )
            program_text = st.text_area(
                "Programmes — one per line",
                value="\n".join(get_programs()),
            )
            save_academic_config = st.form_submit_button(
                "Save Academic Configuration"
            )

        if save_academic_config:
            departments = list(dict.fromkeys(
                line.strip() for line in dept_text.splitlines() if line.strip()
            ))
            programs = list(dict.fromkeys(
                line.strip() for line in program_text.splitlines() if line.strip()
            ))
            if not departments or not programs:
                st.error("At least one department and programme are required.")
            else:
                set_setting("departments", json.dumps(departments))
                set_setting("programs", json.dumps(programs))
                log_event("ACADEMIC_CONFIGURATION_UPDATED")
                st.success("Academic configuration has been saved.")
                st.rerun()

        st.markdown("#### Change Your Password")
        with st.form("admin_change_password_form"):
            current_password = st.text_input(
                "Current Password", type="password"
            )
            new_password = st.text_input(
                "New Password", type="password"
            )
            confirm_password = st.text_input(
                "Confirm New Password", type="password"
            )
            change_password = st.form_submit_button("Update Password")

        if change_password:
            account = query_one(
                "SELECT password_hash FROM users WHERE username = ?",
                (st.session_state["username"],),
            )
            if not account or not verify_password(
                current_password, account["password_hash"]
            ):
                st.error("The current password is incorrect.")
            elif len(new_password) < 12:
                st.error("The new password must contain at least 12 characters.")
            elif new_password != confirm_password:
                st.error("The password confirmation does not match.")
            else:
                execute(
                    """
                    UPDATE users SET password_hash = ?,
                    must_change_password = 0 WHERE username = ?
                    """,
                    (
                        hash_password(new_password),
                        st.session_state["username"],
                    ),
                )
                log_event("PASSWORD_CHANGED")
                st.success("Your password has been changed.")
                st.rerun()

        st.markdown("#### Audit Trail")
        audit_df = query_df(
            """
            SELECT event_time AS 'Event Time',
                   username AS Username,
                   action AS Action,
                   details AS Details
            FROM audit_events ORDER BY event_time DESC LIMIT 500
            """
        )
        st.dataframe(audit_df, use_container_width=True, hide_index=True)
        download_df(audit_df, "hanek_audit_trail.csv")


# ============================================================
# 8. STAFF PORTAL
# ============================================================

def render_staff_portal():
    st.title("Academic and Administrative Staff Portal")
    role = st.session_state["role"]
    st.caption(
        f"Signed in as {st.session_state['display_name']} · "
        f"{role} · {st.session_state['campus']}"
    )

    if role in [
        "Instructor / Lecturer",
        "Department Head",
        "Examination Officer",
    ]:
        tab_submit, tab_results = st.tabs(
            ["Grade Submission", "Grade Submission History"]
        )

        with tab_submit:
            courses = query_df(
                """
                SELECT course_code, course_name, credit_hours, department
                FROM courses WHERE active = 1 ORDER BY course_name
                """
            )
            ids = student_options()
            if courses.empty:
                st.info(
                    "The course catalogue is empty. Contact the Registrar "
                    "to establish the approved curriculum."
                )
            elif ids:
                with st.form("staff_grade_submission_form"):
                    student_label = st.selectbox(
                        "Student", list(ids.keys())
                    )
                    course_options = {
                        f"{r.course_code} — {r.course_name} "
                        f"({r.credit_hours} credits)": r.course_code
                        for r in courses.itertuples()
                    }
                    course_label = st.selectbox(
                        "Course", list(course_options.keys())
                    )
                    year = st.text_input(
                        "Academic Year", value=academic_year()
                    )
                    semester = st.selectbox("Semester", SEMESTERS)
                    score = st.number_input(
                        "Final Assessment Score",
                        min_value=0.0,
                        max_value=100.0,
                        value=75.0,
                        step=0.5,
                    )
                    submit_grade = st.form_submit_button(
                        "Submit Grade for Review"
                    )

                if submit_grade:
                    sid = ids[student_label]
                    course_code = course_options[course_label]
                    course = courses[
                        courses["course_code"] == course_code
                    ].iloc[0]
                    student = get_student(sid)

                    if (
                        role == "Instructor / Lecturer"
                        and st.session_state["department"]
                        and st.session_state["department"] not in [
                            student["department"], "All Departments"
                        ]
                    ):
                        st.error(
                            "Your account is not authorized to submit grades "
                            "for this student's department."
                        )
                    else:
                        letter, point = calculate_grade(score)
                        try:
                            execute(
                                """
                                INSERT INTO grades (
                                    grade_id, student_id, course_code,
                                    course_name, credit_hours, score,
                                    letter_grade, grade_point, academic_year,
                                    semester, instructor, status, submitted_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', ?)
                                """,
                                (
                                    make_id("GRD"),
                                    sid,
                                    course_code,
                                    course["course_name"],
                                    float(course["credit_hours"]),
                                    float(score),
                                    letter,
                                    point,
                                    year.strip(),
                                    semester,
                                    st.session_state["display_name"],
                                    now_string(),
                                ),
                            )
                            log_event("GRADE_SUBMITTED", f"{sid}:{course_code}")
                            st.success(
                                f"Grade {letter} submitted for administrative review."
                            )
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error(
                                "The grade could not be saved. Verify the "
                                "student and course records."
                            )

        with tab_results:
            history = query_df(
                """
                SELECT grade_id AS 'Grade Reference',
                       student_id AS 'Student ID',
                       course_code AS 'Course Code',
                       score AS Score,
                       letter_grade AS Grade,
                       status AS Status,
                       submitted_at AS 'Submitted At'
                FROM grades WHERE instructor = ?
                ORDER BY submitted_at DESC
                """,
                (st.session_state["display_name"],),
            )
            st.dataframe(history, use_container_width=True, hide_index=True)

    elif role in [
        "Admissions Officer",
        "Assistant Registrar",
        "Registrar Officer",
        "Head Registrar",
    ]:
        st.subheader("Admissions and Registrar Work Queue")
        apps = query_df(
            """
            SELECT application_id AS Reference, full_name AS Applicant,
                   campus AS Campus, department AS Department,
                   program AS Programme, status AS Status,
                   submitted_at AS 'Submitted At'
            FROM applications ORDER BY submitted_at DESC
            """
        )
        st.dataframe(apps, use_container_width=True, hide_index=True)
        st.info(
            "For admission decisions and official record creation, "
            "use the authorized institutional workflow."
        )
    else:
        st.info(
            "Your account does not have a specialized workspace configured. "
            "Contact the system administrator if additional access is required."
        )


# ============================================================
# 9. STUDENT PORTAL
# ============================================================

def render_student_portal():
    st.title("Student Self-Service Portal")

    # Student accounts must be explicitly provisioned by authorized staff.
    # A staff login does not confer student privileges.
    student_id = st.session_state.get("student_view_id", "")

    if not student_id:
        st.info(
            "Student self-service access must be linked to a verified student "
            "account by the Registrar. This deployment does not yet provide "
            "a separate student password provisioning workflow."
        )
        return

    student = get_student(student_id)
    if not student:
        st.error("The linked student record could not be found.")
        return

    st.subheader(f"Welcome, {student['full_name']}")
    st.caption(
        f"Student ID: {student['student_id']} · "
        f"Campus: {student['campus']}"
    )

    profile_tab, grades_tab, finance_tab = st.tabs(
        ["Student Profile", "Academic Results", "Financial Summary"]
    )

    with profile_tab:
        p1, p2 = st.columns(2)
        with p1:
            st.markdown("#### Personal and Academic Information")
            st.write(f"**Full Name:** {student['full_name']}")
            st.write(f"**Student ID:** {student['student_id']}")
            st.write(f"**Campus:** {student['campus']}")
            st.write(f"**Department:** {student['department']}")
            st.write(f"**Programme:** {student['program']}")
            st.write(f"**Modality:** {student['modality']}")
            st.write(f"**Status:** {student['status']}")
        with p2:
            st.markdown("#### Profile Photograph")
            if student["photo_path"] and Path(student["photo_path"]).is_file():
                st.image(student["photo_path"], width=160)
            else:
                st.info("No approved profile photograph is available.")

            upload = st.file_uploader(
                "Submit a Passport Photograph for Review",
                type=["png", "jpg", "jpeg"],
                key="student_photo_upload",
            )
            if upload is not None:
                if upload.size > MAX_UPLOAD_MB * 1024 * 1024:
                    st.error(f"The image must not exceed {MAX_UPLOAD_MB} MB.")
                else:
                    try:
                        from PIL import Image
                        import io

                        img = Image.open(io.BytesIO(upload.getvalue())).convert("RGB")
                        target = UPLOAD_DIR / f"{student_id.replace('/', '_')}.jpg"
                        img.save(target, format="JPEG", quality=90)
                        execute(
                            "UPDATE students SET photo_path = ? WHERE student_id = ?",
                            (str(target), student_id),
                        )
                        log_event("STUDENT_PHOTO_UPDATED", student_id)
                        st.success(
                            "The photograph has been saved. Administrative "
                            "verification is required before official use."
                        )
                        st.rerun()
                    except Exception:
                        st.error("The uploaded image could not be processed.")

    with grades_tab:
        cgpa, count, credits = grade_summary(student_id)
        g1, g2, g3 = st.columns(3)
        g1.metric("Cumulative GPA", f"{cgpa:.2f}")
        g2.metric("Approved Course Records", count)
        g3.metric("Credit Hours", f"{credits:.1f}")

        my_grades = query_df(
            """
            SELECT course_code AS 'Course Code',
                   course_name AS 'Course Title',
                   credit_hours AS 'Credit Hours',
                   score AS Score,
                   letter_grade AS Grade,
                   grade_point AS 'Grade Point',
                   academic_year AS 'Academic Year',
                   semester AS Semester
            FROM grades
            WHERE student_id = ? AND status = 'Approved'
            ORDER BY academic_year, semester
            """,
            (student_id,),
        )
        st.dataframe(my_grades, use_container_width=True, hide_index=True)
        download_df(my_grades, f"{student_id}_academic_results.csv")

    with finance_tab:
        balance = current_balance(student_id)
        if balance is None:
            st.info("No financial account has been recorded.")
        else:
            fin = query_one(
                "SELECT total_fee, amount_paid FROM finance WHERE student_id = ?",
                (student_id,),
            )
            f1, f2, f3 = st.columns(3)
            f1.metric("Total Fee (ETB)", f"{fin['total_fee']:,.2f}")
            f2.metric("Amount Paid (ETB)", f"{fin['amount_paid']:,.2f}")
            f3.metric("Outstanding Balance (ETB)", f"{balance:,.2f}")

            payments = query_df(
                """
                SELECT receipt_number AS 'Receipt Number',
                       amount AS 'Amount (ETB)',
                       payment_method AS 'Payment Method',
                       payment_date AS 'Payment Date'
                FROM payments WHERE student_id = ?
                ORDER BY payment_date DESC
                """,
                (student_id,),
            )
            st.dataframe(payments, use_container_width=True, hide_index=True)


# ============================================================
# 10. MAIN NAVIGATION
# ============================================================

st.sidebar.markdown(
    f"""
    <div style="text-align:center; padding: 12px 0;">
        <div style="font-size: 36px;">🎓</div>
        <h3 style="color:white !important; margin-bottom:4px;">
            HANEK COLLEGE
        </h3>
        <div style="font-size:12px; opacity:.85;">
            Academic and Registrar Portal
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")

if is_logged_in():
    st.sidebar.success(
        f"{st.session_state['display_name']}\n\n"
        f"{st.session_state['role']}"
    )
    st.sidebar.caption(
        f"Campus: {st.session_state['campus']}"
    )
    portal = st.sidebar.radio(
        "Institutional Workspace",
        [
            "Institutional Home",
            "My Workspace",
        ],
    )
    if st.sidebar.button("Sign Out", use_container_width=True):
        logout()

    if st.session_state.get("role") == "System Administrator":
        if portal == "Institutional Home":
            render_public_portal()
        else:
            render_admin_dashboard()
    elif portal == "Institutional Home":
        render_public_portal()
    else:
        render_staff_portal()
else:
    portal = st.sidebar.radio(
        "Portal",
        [
            "Institutional Home",
            "Secure Sign In",
        ],
    )
    if portal == "Institutional Home":
        render_public_portal()
    else:
        login_form()

st.markdown("---")
st.caption(
    f"{APP_NAME} · Multi-Campus Academic and Registrar System · "
    f"Version {APP_VERSION} · © {CURRENT_YEAR}"
)
