import base64
import hashlib
import hmac
import html
import io
import os
import secrets
import string
from datetime import date, datetime

import pandas as pd
import streamlit as st

# ============================================================
# HANek TECHNOLOGY AND BUSINESS COLLEGE
# Multi-Campus Student Information and Registrar System
# ============================================================
# Security note:
# Configure secrets in Streamlit Cloud. Do not put owner/admin
# passwords in source code. Owner access is explicit, auditable,
# and configured by the system owner; it is not a hidden backdoor.

st.set_page_config(
    page_title="Hanek Technology and Business College | Registrar SIS",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_NAME = "Hanek Technology and Business College"
APP_SHORT = "HBTC"
PHOTO_DIR = "student_photos"
os.makedirs(PHOTO_DIR, exist_ok=True)

FILES = {
    "students": "students.csv",
    "grades": "grades.csv",
    "pending_grades": "pending_grades.csv",
    "staff": "staff.csv",
    "admin": "admin.csv",
    "finance": "finances.csv",
    "departments": "departments.csv",
    "programs": "programs.csv",
    "announcements": "announcements.csv",
    "applications": "applications.csv",
    "level_requests": "level_registration_requests.csv",
    "task_requests": "staff_task_requests.csv",
    "audit": "audit_log.csv",
    "logo": "logo.png",
}

CAMPUSES = ["Wolaita Sodo", "Basketo Laska", "Boloso Bombe", "Jinka"]
LEVELS = ["Level I", "Level II", "Level III", "Level IV"]
MODALITIES = ["Regular", "Extension"]
STAFF_ROLES = [
    "College President",
    "Vice President for Academic Affairs",
    "Cross-Campus Institutional Coach / Quality Assurance Director",
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
DEFAULT_DEPARTMENTS = [
    "Cooperative Accounting and Auditing",
    "Cooperative Business Management",
    "Cooperative Marketing",
    "Hardware and Network Systems (HNS)",
    "Natural Resource Management (NARM)",
    "Crop Production (Plant Science)",
]
DEFAULT_PROGRAMS = LEVELS

STUDENT_COLUMNS = [
    "StudentID", "FullName", "DateOfBirth", "Campus", "Department",
    "ProgramLevel", "Modality", "YearOfEntry", "AcademicYear",
    "YearOfGraduation", "PasswordHash", "Photo", "PhotoStatus",
    "Active", "CreatedAt",
]
GRADE_COLUMNS = [
    "GradeID", "StudentID", "FullName", "Level", "CourseCode",
    "CourseName", "CreditHour", "Score", "Grade", "GradePoint",
    "Semester", "AcademicYear", "Instructor", "Status", "ApprovedBy",
    "ApprovedAt",
]
PENDING_GRADE_COLUMNS = [
    "RequestID", "StudentID", "FullName", "Level", "CourseCode",
    "CourseName", "CreditHour", "Score", "Semester", "AcademicYear",
    "Instructor", "SubmittedAt", "Status",
]
STAFF_COLUMNS = [
    "StaffID", "FullName", "Role", "Campus", "Department",
    "InstitutionalEmail", "PasswordHash", "Active",
]
FINANCE_COLUMNS = [
    "StudentID", "Level", "TuitionFeeETB", "OtherFeesETB",
    "PaidETB", "BalanceETB", "Status", "LastUpdated",
]
APPLICATION_COLUMNS = [
    "AppID", "FullName", "DateOfBirth", "Phone", "Email", "Campus",
    "Department", "Level", "Modality", "YearOfEntry", "Status",
    "DateSubmitted",
]
LEVEL_REQUEST_COLUMNS = [
    "RequestID", "StudentID", "FullName", "CurrentLevel", "RequestedLevel",
    "AcademicYear", "SubmittedAt", "Status", "ReviewedBy", "ReviewNote",
]
TASK_REQUEST_COLUMNS = [
    "RequestID", "StaffID", "StaffName", "StaffRole", "TaskType",
    "Description", "RelatedStudentID", "SubmittedAt", "Status",
    "ReviewedBy", "ReviewNote",
]
AUDIT_COLUMNS = ["Timestamp", "Actor", "Role", "Action", "Details"]

def read_csv(key, columns=None):
    path = FILES[key]
    if not os.path.exists(path):
        df = pd.DataFrame(columns=columns or [])
        df.to_csv(path, index=False)
        return df
    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
    except (pd.errors.EmptyDataError, UnicodeDecodeError):
        df = pd.DataFrame(columns=columns or [])
    if columns:
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        # Preserve existing extra columns to avoid data loss.
        df = df[list(dict.fromkeys(list(columns) + [c for c in df.columns if c not in columns]))]
    return df.fillna("")

def save_csv(key, df):
    df.to_csv(FILES[key], index=False)

def ensure_storage():
    for key, cols in [
        ("students", STUDENT_COLUMNS), ("grades", GRADE_COLUMNS),
        ("pending_grades", PENDING_GRADE_COLUMNS), ("staff", STAFF_COLUMNS),
        ("finance", FINANCE_COLUMNS), ("applications", APPLICATION_COLUMNS),
        ("level_requests", LEVEL_REQUEST_COLUMNS), ("task_requests", TASK_REQUEST_COLUMNS),
        ("audit", AUDIT_COLUMNS),
    ]:
        df = read_csv(key, cols)
        save_csv(key, df)
    if not os.path.exists(FILES["departments"]):
        pd.DataFrame({"Department": DEFAULT_DEPARTMENTS}).to_csv(FILES["departments"], index=False)
    if not os.path.exists(FILES["programs"]):
        pd.DataFrame({"Program": DEFAULT_PROGRAMS}).to_csv(FILES["programs"], index=False)
    if not os.path.exists(FILES["announcements"]):
        pd.DataFrame(columns=["NoticeID", "Title", "Date", "Category", "Content"]).to_csv(FILES["announcements"], index=False)
    if not os.path.exists(FILES["admin"]):
        pd.DataFrame(columns=["Username", "PasswordHash", "Role", "Active"]).to_csv(FILES["admin"], index=False)

def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 260_000).hex()
    return f"pbkdf2_sha256${salt}${digest}"

def verify_password(password, stored):
    if not stored:
        return False
    if stored.startswith("pbkdf2_sha256$"):
        try:
            _, salt, digest = stored.split("$", 2)
            check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 260_000).hex()
            return hmac.compare_digest(check, digest)
        except ValueError:
            return False
    # One-time compatibility for older CSV records with plain-text passwords.
    # On successful login, the record is upgraded to a salted hash.
    return hmac.compare_digest(str(password), str(stored))

def new_id(prefix):
    return f"{prefix}-{datetime.now().strftime('%y%m%d')}-{secrets.token_hex(3).upper()}"

def audit(actor, role, action, details=""):
    df = read_csv("audit", AUDIT_COLUMNS)
    df.loc[len(df)] = [
        datetime.now().isoformat(timespec="seconds"),
        str(actor), str(role), str(action), str(details)
    ]
    save_csv("audit", df.tail(5000))

def grade_for_score(score):
    score = float(score)
    if score >= 90: return "A+", 4.0
    if score >= 85: return "A", 4.0
    if score >= 80: return "A-", 3.75
    if score >= 75: return "B+", 3.25
    if score >= 70: return "B", 3.0
    if score >= 65: return "B-", 2.75
    if score >= 60: return "C+", 2.5
    if score >= 50: return "C", 2.0
    if score >= 40: return "D", 1.0
    return "F", 0.0

def level_index(level):
    try:
        return LEVELS.index(str(level))
    except ValueError:
        return -1

def get_departments():
    df = read_csv("departments", ["Department"])
    values = [x for x in df["Department"].tolist() if str(x).strip()]
    return values or DEFAULT_DEPARTMENTS

def get_programs():
    # Academic progression levels are intentionally separate from modality.
    return LEVELS

def safe(v):
    return html.escape(str(v if v is not None else ""))

def logo_data_uri():
    if not os.path.exists(FILES["logo"]):
        return ""
    try:
        with open(FILES["logo"], "rb") as f:
            encoded = base64.b64encode(f.read()).decode("ascii")
        ext = os.path.splitext(FILES["logo"])[1].lower()
        mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
        return f"data:{mime};base64,{encoded}"
    except OSError:
        return ""

def current_user():
    return st.session_state.get("username", "Guest")

def current_role():
    return st.session_state.get("user_role", "Guest")

def is_admin():
    return current_role() in ("College Administrator", "System Owner")

def configured_secret(name, default=""):
    """Read a credential setting from Streamlit secrets, then environment variables."""
    try:
        value = st.secrets.get(name, "")
    except Exception:
        value = ""
    return str(value or os.environ.get(name, default) or "")

def make_brand():
    st.markdown(
        f"""
        <div class="brand">
          <div class="eyebrow">EXCELLENCE • KNOWLEDGE • PROFESSIONALISM</div>
          <h1>{APP_NAME.upper()}</h1>
          <div class="gold-rule"></div>
          <p>Multi-Campus Student Information and Registrar Management System</p>
          <div class="campus-line">Wolaita Sodo&nbsp; • &nbsp;Basketo Laska&nbsp; • &nbsp;Boloso Bombe&nbsp; • &nbsp;Jinka</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

ensure_storage()

st.markdown("""
<style>
:root{--navy:#10213f;--blue:#1e4e8c;--royal:#2865b0;--gold:#d6a943;--bg:#f3f6fb;--ink:#18263d;--muted:#64748b;--line:#dbe4ef}
.stApp{background:var(--bg);color:var(--ink)}
.main .block-container{max-width:1600px;padding-top:1.4rem;padding-bottom:2.5rem}
h1,h2,h3,h4{color:var(--navy);font-weight:800;letter-spacing:-.25px}
h1{border-bottom:3px solid var(--gold);padding-bottom:.35rem}
.brand{background:linear-gradient(125deg,#10213f,#173f78 62%,#2865b0);color:white;padding:28px 30px;border-radius:16px;border-bottom:5px solid var(--gold);margin-bottom:22px;box-shadow:0 8px 25px #10213f20}
.brand h1{color:white!important;border:0;font-size:clamp(22px,3vw,35px);line-height:1.3;margin:7px 0}
.brand p{color:white;margin:0;font-weight:700;font-size:16px}
.brand .eyebrow{color:#f2d68b;font-size:10px;letter-spacing:2px;font-weight:900}
.brand .gold-rule{height:4px;width:78px;background:var(--gold);border-radius:8px;margin:12px 0}
.campus-line{font-size:12px;color:#e7edf7;margin-top:12px}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#10213f,#17365f);border-right:3px solid var(--gold)}
[data-testid="stSidebar"] *{color:#fff}
[data-testid="stSidebar"] [data-baseweb="select"]>div,[data-testid="stSidebar"] input{background:#fff;color:#10213f}
.stButton>button,.stFormSubmitButton>button{background:linear-gradient(135deg,#173f78,#2865b0);color:white!important;border:1px solid #173f78;border-radius:9px;min-height:40px;font-weight:750;box-shadow:0 3px 8px #173f781c}
.stButton>button:hover,.stFormSubmitButton>button:hover{background:#10213f;border-color:var(--gold);transform:translateY(-1px)}
.stTextInput input,.stTextArea textarea,.stNumberInput input,.stDateInput input{background:#fff;border-radius:8px;border:1px solid #cbd5e1}
.stTabs [data-baseweb="tab-list"]{gap:5px;border-bottom:2px solid var(--line)}
.stTabs [data-baseweb="tab"]{background:#e8edf5;border-radius:8px 8px 0 0;padding:9px 12px;font-weight:700}
.stTabs [aria-selected="true"]{background:#173f78;color:#fff!important;border-bottom:3px solid var(--gold)}
.stTabs [aria-selected="true"] p{color:white!important}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:10px;background:white}
[data-testid="stExpander"]{background:white;border:1px solid var(--line);border-radius:12px}
[data-testid="stAlert"]{border-radius:10px}
.metric-card{background:#fff;border:1px solid var(--line);border-top:4px solid var(--gold);padding:17px;border-radius:12px;box-shadow:0 4px 15px #10213f0a}
.metric-label{color:var(--muted);font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.6px}
.metric-value{color:var(--navy);font-size:27px;font-weight:900;margin-top:5px}
.notice{background:#fff;border:1px solid var(--line);border-left:5px solid var(--gold);border-radius:11px;padding:18px 20px;margin:12px 0}
.footer{background:white;border-top:4px solid var(--gold);border-radius:10px;text-align:center;padding:18px;margin-top:30px;color:#173f78}
.small-muted{font-size:12px;color:#64748b}
@media(max-width:768px){.main .block-container{padding-left:.8rem;padding-right:.8rem}.brand{padding:20px 17px}.stButton>button,.stFormSubmitButton>button{width:100%}}
@media print{@page{size:A4 landscape;margin:8mm} [data-testid="stSidebar"],header,footer,.stButton,.stFormSubmitButton{display:none!important}.main .block-container{max-width:100%;padding:0!important}.print-document{page-break-inside:avoid;break-inside:avoid}}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div style='text-align:center;padding:10px 4px 16px;border-bottom:2px solid #d6a943'><div style='font-size:38px'>🎓</div><div style='font-size:21px;font-weight:900'>HANEK COLLEGE</div><div style='color:#f2d68b;font-size:10px;letter-spacing:1.5px;font-weight:800'>TECHNOLOGY & BUSINESS</div><div style='font-size:11px;margin-top:8px'>Registrar and Student Information System</div></div>", unsafe_allow_html=True)
    if os.path.exists(FILES["logo"]):
        st.image(FILES["logo"], use_container_width=True)
    portal = st.selectbox("Portal", [
        "Home / About / Contact",
        "Online Admission",
        "College Administration",
        "Staff and Registrar Portal",
        "Student Portal",
    ])
    st.markdown("---")
    st.caption("Secure institutional access • All actions subject to role permissions")

# Public landing page
if portal == "Home / About / Contact":
    make_brand()
    students = read_csv("students", STUDENT_COLUMNS)
    staff = read_csv("staff", STAFF_COLUMNS)
    applications = read_csv("applications", APPLICATION_COLUMNS)
    c1,c2,c3 = st.columns(3)
    for col,label,val in [(c1,"CAMPUSES SERVED","4"),(c2,"ACADEMIC LEVELS","4"),(c3,"SYSTEM PURPOSE","Registrar SIS")]:
        with col:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{val}</div></div>",unsafe_allow_html=True)
    st.markdown("### Welcome to Hanek Technology and Business College")
    st.write("The institutional registrar platform supports student admission, level-by-level academic progression, grade administration, financial clearance, staff workflows, and official academic records across the College's campuses.")
    tabs = st.tabs(["About the College","Public Announcements","Contact the College","Admissions Information"])
    with tabs[0]:
        st.markdown("#### About Us")
        st.write("Hanek Technology and Business College provides technical, vocational, and business-oriented education. This digital platform is designed to support accurate academic records, transparent administrative workflows, and consistent registrar services across campuses.")
        st.markdown("#### Academic Structure")
        st.write("Students progress through Level I, Level II, Level III, and Level IV. Regular and Extension are study modalities, not academic levels. Progression to the next level requires completion of the current level and institutional approval.")
        st.markdown("#### Campuses")
        st.write(", ".join(CAMPUSES))
        st.markdown("#### Departments")
        for d in get_departments():
            st.write("• " + d)
    with tabs[1]:
        announcements = read_csv("announcements", ["NoticeID","Title","Date","Category","Content"])
        if announcements.empty:
            st.info("There are no public announcements at present.")
        else:
            for _,n in announcements.iloc[::-1].iterrows():
                st.markdown(f"<div class='notice'><h4>{safe(n['Title'])}</h4><div class='small-muted'>{safe(n['Date'])} · {safe(n['Category'])}</div><p>{safe(n['Content'])}</p></div>",unsafe_allow_html=True)
    with tabs[2]:
        st.markdown("#### Office of the Registrar")
        st.write("**Headquarters:** Wolaita Sodo, Ethiopia (P.O. Box 23)")
        st.write("**Telephone:** +251-46-180-3164 / +251916747538")
        st.write("**Email:** registrar@hanekcollege.edu.et")
        st.write("**Website:** http://www.hanekcollege.edu.et")
        st.caption("Please verify institutional contact details before publishing them as official contact information.")
        st.markdown("---")
        st.markdown("#### Software Developer and Technical Support")
        st.write("**Developer:** Ebirawi Henok Loha")
        st.write("**Telephone / WhatsApp:** +251965514327 / +251916070065")
        st.write("**Email:** henokebirawi3@gmail.com")
        st.caption("For system licensing, deployment support, technical maintenance, or institutional onboarding, contact the software developer.")
    with tabs[3]:
        st.write("Applicants may submit an online application using the Online Admission portal. Admission remains subject to institutional review and confirmation.")
        st.write("Available academic levels: " + ", ".join(LEVELS))
        st.write("Available modalities: " + ", ".join(MODALITIES))

# Online admission
elif portal == "Online Admission":
    make_brand()
    st.title("Online Admission Application")
    with st.form("application_form"):
        a,b = st.columns(2)
        with a:
            name = st.text_input("Full legal name")
            dob = st.date_input("Date of birth", value=date(2000,1,1), min_value=date(1940,1,1), max_value=date.today())
            phone = st.text_input("Telephone number")
            email = st.text_input("Email address (optional)")
        with b:
            campus = st.selectbox("Preferred campus", CAMPUSES)
            dept = st.selectbox("Department", get_departments())
            level = st.selectbox("Entry level", LEVELS)
            modality = st.selectbox("Study modality", MODALITIES)
            entry_year = st.number_input("Year of entry", min_value=2000, max_value=2100, value=datetime.now().year)
        submitted = st.form_submit_button("Submit admission application")
    if submitted:
        if not name.strip() or not phone.strip():
            st.error("Please provide the applicant's full legal name and telephone number.")
        else:
            df = read_csv("applications", APPLICATION_COLUMNS)
            df.loc[len(df)] = [new_id("APP"),name.strip(),dob.isoformat(),phone.strip(),email.strip(),campus,dept,level,modality,str(entry_year),"Pending Review",date.today().isoformat()]
            save_csv("applications",df)
            audit(name.strip(),"Applicant","Submitted admission application",f"{level} / {campus}")
            st.success("Your application has been submitted for institutional review.")
            st.info("Please retain your application reference: " + str(df.iloc[-1]["AppID"]))

# Admin / owner portal
elif portal == "College Administration":
    make_brand()
    st.title("College Administration")
    st.caption("Administrative actions are logged. Student progression, grade publication, credential issuance, and staff task execution require authorised review.")
    if st.session_state.get("user_role") not in ("College Administrator","System Owner"):
        with st.form("admin_login"):
            username = st.text_input("Administrator username")
            password = st.text_input("Password",type="password")
            login = st.form_submit_button("Sign in")
        if login:
            # Owner credentials are configured in Streamlit secrets, never embedded in source.
            owner_name = configured_secret("HANEK_OWNER_USERNAME")
            owner_password = configured_secret("HANEK_OWNER_PASSWORD")
            if owner_name and owner_password and hmac.compare_digest(username, owner_name) and hmac.compare_digest(password, owner_password):
                st.session_state["username"] = username
                st.session_state["user_role"] = "System Owner"
                audit(username,"System Owner","Successful login","Owner account")
                st.rerun()
            admins = read_csv("admin",["Username","PasswordHash","Role","Active"])
            match_idx = None
            for idx,row in admins.iterrows():
                if row.get("Username","") == username and str(row.get("Active","True")).lower() not in ("false","0","no"):
                    # Support old admin.csv files that stored a Password column or a
                    # legacy plain-text PasswordHash. Successful legacy logins are upgraded.
                    stored = row.get("PasswordHash", "") or row.get("Password", "")
                    if verify_password(password, stored):
                        match_idx = idx
                        break
            if match_idx is not None:
                stored = str(admins.at[match_idx,"PasswordHash"] or admins.at[match_idx,"Password"] if "Password" in admins.columns else admins.at[match_idx,"PasswordHash"])
                admins.at[match_idx,"PasswordHash"] = hash_password(password)
                if "Password" in admins.columns:
                    admins.at[match_idx,"Password"] = ""
                save_csv("admin",admins)
                st.session_state["username"] = username
                st.session_state["user_role"] = "College Administrator"
                audit(username,"College Administrator","Successful login","College admin account; legacy credential format migrated if applicable")
                st.rerun()
            # Optional emergency recovery account configured by the owner in hosting Secrets.
            # It is used only when there is no active local administrator account.
            active_admins = admins[admins.get("Active", pd.Series("True", index=admins.index)).astype(str).str.lower().isin(["true","1","yes"])] if not admins.empty else admins
            recovery_name = configured_secret("HANEK_ADMIN_USERNAME")
            recovery_password = configured_secret("HANEK_ADMIN_PASSWORD")
            if active_admins.empty and recovery_name and recovery_password and hmac.compare_digest(username, recovery_name) and hmac.compare_digest(password, recovery_password):
                # Bootstrap a durable local administrator record, then authenticate normally.
                admins.loc[len(admins)] = [recovery_name, hash_password(recovery_password), "College Administrator", "True"]
                save_csv("admin", admins)
                st.session_state["username"] = username
                st.session_state["user_role"] = "College Administrator"
                audit(username,"College Administrator","Bootstrapped recovery administrator","Created local administrator record from hosting Secrets")
                st.rerun()
            st.error("The supplied credentials are invalid. If this is the first login after updating the app, verify the owner/admin credentials in Streamlit Cloud → App settings → Secrets. Existing local CSV accounts may not carry over between deployments.")
    else:
        user_role = st.session_state["user_role"]
        st.success(f"Signed in as {user_role}: {st.session_state['username']}")
        if st.button("Sign out"):
            audit(current_user(),current_role(),"Signed out")
            for key in ["username","user_role"]:
                st.session_state.pop(key,None)
            st.rerun()

        owner_tools_view = False
        if user_role == "System Owner":
            st.info("System Owner access is enabled. You can use the full institutional administration workspace below, as well as the separate owner security and licensing tools.")
            owner_tools_view = st.checkbox("Open System Owner Security & Licensing tools", value=False)
        if user_role == "System Owner" and owner_tools_view:
            owner_tabs = st.tabs(["Institutional Administration","Owner Security & Licensing","Audit Log"])
            with owner_tabs[0]:
                st.markdown("### College administrator account")
                admins = read_csv("admin",["Username","PasswordHash","Role","Active"])
                with st.form("create_admin"):
                    new_user = st.text_input("New administrator username")
                    new_pw = st.text_input("Temporary password",type="password")
                    confirm_pw = st.text_input("Confirm temporary password",type="password")
                    create = st.form_submit_button("Create college administrator")
                if create:
                    if not new_user.strip() or len(new_pw)<12:
                        st.error("Enter a username and a password of at least 12 characters.")
                    elif new_pw != confirm_pw:
                        st.error("The passwords do not match.")
                    elif new_user in admins["Username"].tolist():
                        st.error("That username already exists.")
                    else:
                        admins.loc[len(admins)] = [new_user.strip(),hash_password(new_pw),"College Administrator","True"]
                        save_csv("admin",admins)
                        audit(current_user(),user_role,"Created college administrator",new_user.strip())
                        st.success("Administrator account created.")
                if not admins.empty:
                    display_admins = admins.copy()
                    display_admins["PasswordHash"] = "••••••••"
                    st.dataframe(display_admins,use_container_width=True)
            with owner_tabs[1]:
                st.markdown("### System owner and deployment configuration")
                st.write("The system owner account is configured through the hosting platform's secret settings. It is separate from college administrator accounts.")
                st.code('HANEK_OWNER_USERNAME = "your-owner-username"\nHANEK_OWNER_PASSWORD = "a-long-unique-password"\n# Optional, temporary recovery account only if no active admin exists\nHANEK_ADMIN_USERNAME = "temporary-admin-username"\nHANEK_ADMIN_PASSWORD = "a-long-unique-password"',language="toml")
                st.warning("Do not publish owner credentials, embed them in app.py, or share them with institutional administrators. Use a unique password and protect the hosting account and source repository.")
                st.markdown("### Institutional ownership")
                st.write("Keep your copyright notice and system licence terms in the application and contract. Technical controls alone cannot guarantee that no administrator can copy source code if they have repository or hosting access.")
            with owner_tabs[2]:
                st.dataframe(read_csv("audit",AUDIT_COLUMNS).iloc[::-1],use_container_width=True)
        else:
            tabs = st.tabs([
                "Dashboard","Student Records Master","Level Registration Approvals",
                "Applicants & Admissions","Staff Directory & Task Approvals",
                "Announcements","Departments & Programs","Grade Approvals",
                "Student Financial Accounts","Official Credential Issuance",
                "System Configuration & Audit"
            ])
            students = read_csv("students",STUDENT_COLUMNS)
            grades = read_csv("grades",GRADE_COLUMNS)
            pending = read_csv("pending_grades",PENDING_GRADE_COLUMNS)
            staff = read_csv("staff",STAFF_COLUMNS)
            finance = read_csv("finance",FINANCE_COLUMNS)
            applications = read_csv("applications",APPLICATION_COLUMNS)
            level_requests = read_csv("level_requests",LEVEL_REQUEST_COLUMNS)
            task_requests = read_csv("task_requests",TASK_REQUEST_COLUMNS)
            with tabs[0]:
                st.markdown("### Institutional overview")
                metric_cols = st.columns(4)
                metrics = [
                    ("Enrolled students",len(students)),
                    ("Staff members",len(staff)),
                    ("Pending grade submissions",len(pending)),
                    ("Pending level registrations",len(level_requests[level_requests["Status"]=="Pending Review"])),
                ]
                for col,(label,value) in zip(metric_cols,metrics):
                    with col:
                        st.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div></div>",unsafe_allow_html=True)
                st.markdown("#### Enrolment by campus")
                if not students.empty:
                    campus_counts = students.groupby("Campus").size().reset_index(name="Students")
                    st.bar_chart(campus_counts.set_index("Campus"))
                else:
                    st.info("Student enrolment data will appear here after records are created.")
            with tabs[1]:
                st.markdown("### Student Records Master")
                with st.expander("Register a new student",expanded=False):
                    with st.form("create_student"):
                        x1,x2 = st.columns(2)
                        with x1:
                            sid = st.text_input("Student ID")
                            fullname = st.text_input("Full legal name")
                            dob = st.date_input("Official date of birth",value=date(2000,1,1),min_value=date(1940,1,1),max_value=date.today())
                            campus = st.selectbox("Campus",CAMPUSES)
                            department = st.selectbox("Department",get_departments())
                        with x2:
                            level = st.selectbox("Initial academic level",LEVELS)
                            modality = st.selectbox("Study modality",MODALITIES)
                            entry_year = st.number_input("Year of entry",min_value=2000,max_value=2100,value=datetime.now().year)
                            academic_year = st.text_input("Academic year",value=f"{datetime.now().year}/{datetime.now().year+1}")
                            student_pw = st.text_input("Initial student password",type="password")
                        photo = st.file_uploader("Profile photograph (optional)",type=["png","jpg","jpeg"])
                        save_student = st.form_submit_button("Create student record")
                    if save_student:
                        if not sid.strip() or not fullname.strip() or len(student_pw)<8:
                            st.error("Student ID, full legal name, and a password of at least 8 characters are required.")
                        elif sid.strip() in students["StudentID"].tolist():
                            st.error("That Student ID already exists.")
                        else:
                            photo_path = ""
                            if photo:
                                ext = os.path.splitext(photo.name)[1].lower()
                                if ext not in [".png",".jpg",".jpeg"]:
                                    ext = ".png"
                                photo_path = os.path.join(PHOTO_DIR,f"{sid.strip().replace('/','_')}{ext}")
                                with open(photo_path,"wb") as f: f.write(photo.getbuffer())
                            students.loc[len(students)] = [sid.strip(),fullname.strip(),dob.isoformat(),campus,department,level,modality,str(entry_year),academic_year,"",hash_password(student_pw),photo_path,"Approved" if photo else "Not Uploaded","True",datetime.now().isoformat(timespec="seconds")]
                            save_csv("students",students)
                            audit(current_user(),user_role,"Created student record",sid.strip())
                            st.success("Student record created.")
                            st.rerun()
                st.markdown("#### Student register")
                if students.empty:
                    st.info("No student records are available.")
                else:
                    filter_campus = st.selectbox("Filter by campus",["All campuses"]+CAMPUSES,key="student_filter_campus")
                    shown = students if filter_campus=="All campuses" else students[students["Campus"]==filter_campus]
                    visible = shown.drop(columns=["PasswordHash"],errors="ignore")
                    st.dataframe(visible,use_container_width=True)
                    student_ids = students["StudentID"].tolist()
                    chosen = st.selectbox("Select a student to edit or deactivate",student_ids,key="edit_student_select")
                    row = students[students["StudentID"]==chosen].iloc[0]
                    with st.form("edit_student_record"):
                        ename = st.text_input("Full legal name",value=row["FullName"])
                        edob = st.date_input("Date of birth",value=pd.to_datetime(row["DateOfBirth"]).date() if row["DateOfBirth"] else date(2000,1,1),min_value=date(1940,1,1),max_value=date.today())
                        ecampus = st.selectbox("Campus",CAMPUSES,index=CAMPUSES.index(row["Campus"]) if row["Campus"] in CAMPUSES else 0)
                        edept = st.selectbox("Department",get_departments(),index=get_departments().index(row["Department"]) if row["Department"] in get_departments() else 0)
                        elevel = st.selectbox("Current level",LEVELS,index=LEVELS.index(row["ProgramLevel"]) if row["ProgramLevel"] in LEVELS else 0)
                        emod = st.selectbox("Modality",MODALITIES,index=MODALITIES.index(row["Modality"]) if row["Modality"] in MODALITIES else 0)
                        eyear = st.text_input("Year of entry",value=row["YearOfEntry"])
                        eacademic = st.text_input("Current academic year",value=row["AcademicYear"])
                        egrad = st.text_input("Year of graduation (leave blank until completion)",value=row["YearOfGraduation"])
                        eactive = st.selectbox("Record status",["True","False"],index=0 if row["Active"]!="False" else 1)
                        save_edit = st.form_submit_button("Save student changes")
                    if save_edit:
                        mask = students["StudentID"]==chosen
                        for col,val in {"FullName":ename.strip(),"DateOfBirth":edob.isoformat(),"Campus":ecampus,"Department":edept,"ProgramLevel":elevel,"Modality":emod,"YearOfEntry":eyear,"AcademicYear":eacademic,"YearOfGraduation":egrad,"Active":eactive}.items():
                            students.loc[mask,col]=val
                        save_csv("students",students)
                        audit(current_user(),user_role,"Edited student record",chosen)
                        st.success("Student record updated.")
                        st.rerun()
                    confirm_del = st.checkbox("I confirm that this student record should be permanently deleted.",key="confirm_student_delete")
                    if st.button("Delete selected student record",disabled=not confirm_del):
                        students = students[students["StudentID"]!=chosen]
                        save_csv("students",students)
                        audit(current_user(),user_role,"Deleted student record",chosen)
                        st.warning("Student record deleted. Related grade and finance records were retained for audit; review them separately.")
                        st.rerun()
            with tabs[2]:
                st.markdown("### Level Registration Approvals")
                st.write("Students request progression after completing the preceding level. Approval updates the student's current level and grants level-scoped access.")
                reqs = read_csv("level_requests",LEVEL_REQUEST_COLUMNS)
                pending_reqs = reqs[reqs["Status"]=="Pending Review"]
                if pending_reqs.empty:
                    st.info("There are no level-registration requests awaiting review.")
                else:
                    st.dataframe(pending_reqs,use_container_width=True)
                    req_id = st.selectbox("Select request",pending_reqs["RequestID"].tolist(),key="level_request_select")
                    review_note = st.text_input("Review note (optional)",key="level_review_note")
                    ca,cr = st.columns(2)
                    if ca.button("Approve level registration"):
                        req = reqs[reqs["RequestID"]==req_id].iloc[0]
                        student_mask = students["StudentID"]==req["StudentID"]
                        if student_mask.any():
                            students.loc[student_mask,"ProgramLevel"] = req["RequestedLevel"]
                            students.loc[student_mask,"AcademicYear"] = req["AcademicYear"]
                            save_csv("students",students)
                            reqs.loc[reqs["RequestID"]==req_id,["Status","ReviewedBy","ReviewNote"]]=["Approved",current_user(),review_note]
                            save_csv("level_requests",reqs)
                            audit(current_user(),user_role,"Approved level registration",f"{req['StudentID']} -> {req['RequestedLevel']}")
                            st.success("Registration approved. Student access is now limited to the approved level.")
                            st.rerun()
                        else:
                            st.error("The student record could not be found.")
                    if cr.button("Reject level registration"):
                        reqs.loc[reqs["RequestID"]==req_id,["Status","ReviewedBy","ReviewNote"]]=["Rejected",current_user(),review_note]
                        save_csv("level_requests",reqs)
                        audit(current_user(),user_role,"Rejected level registration",req_id)
                        st.warning("Level-registration request rejected.")
                        st.rerun()
                st.markdown("#### Registration history")
                st.dataframe(reqs,use_container_width=True)
            with tabs[3]:
                st.markdown("### Applicants and Admissions")
                apps = read_csv("applications",APPLICATION_COLUMNS)
                if apps.empty:
                    st.info("No applications have been received.")
                else:
                    st.dataframe(apps,use_container_width=True)
                    appid = st.selectbox("Application to review",apps["AppID"].tolist(),key="admission_review_id")
                    approw = apps[apps["AppID"]==appid].iloc[0]
                    decision = st.selectbox("Decision",["Admitted","Waitlisted","Rejected"],key="admission_decision")
                    if st.button("Save admission decision"):
                        apps.loc[apps["AppID"]==appid,"Status"]=decision
                        save_csv("applications",apps)
                        audit(current_user(),user_role,"Updated application status",f"{appid}: {decision}")
                        st.success("Application decision saved.")
                        st.rerun()
                    if approw["Status"]=="Admitted" and not (not students.empty and approw["AppID"] in students.get("AdmissionAppID",pd.Series(dtype=str)).tolist()):
                        st.caption("Create an enrolled student record from this admitted application in Student Records Master, using the approved Student ID and secure initial credentials.")
            with tabs[4]:
                st.markdown("### Staff Directory and Task Approvals")
                st.write("Staff may submit requests through their portal. College administrators review requests before changes are applied.")
                staff = read_csv("staff",STAFF_COLUMNS)
                with st.expander("Register staff member"):
                    with st.form("staff_create_form"):
                        staffid = st.text_input("Staff ID")
                        staffname = st.text_input("Staff full name")
                        staffrole = st.selectbox("Institutional role",STAFF_ROLES)
                        staffcampus = st.selectbox("Assigned campus",CAMPUSES+["All Campuses"])
                        staffdept = st.text_input("Department / unit")
                        staffemail = st.text_input("Institutional email")
                        staffpw = st.text_input("Initial password",type="password")
                        staffcreate = st.form_submit_button("Create staff account")
                    if staffcreate:
                        if not staffid.strip() or not staffname.strip() or len(staffpw)<8:
                            st.error("Staff ID, name, and a password of at least 8 characters are required.")
                        elif staffid.strip() in staff["StaffID"].tolist():
                            st.error("That Staff ID already exists.")
                        else:
                            staff.loc[len(staff)] = [staffid.strip(),staffname.strip(),staffrole,staffcampus,staffdept,staffemail.strip(),hash_password(staffpw),"True"]
                            save_csv("staff",staff)
                            audit(current_user(),user_role,"Created staff account",staffid.strip())
                            st.success("Staff account created.")
                            st.rerun()
                if not staff.empty:
                    shown_staff=staff.drop(columns=["PasswordHash"],errors="ignore")
                    st.dataframe(shown_staff,use_container_width=True)
                    selected_staff=st.selectbox("Staff account to edit/deactivate",staff["StaffID"].tolist(),key="staff_edit_select")
                    sr=staff[staff["StaffID"]==selected_staff].iloc[0]
                    with st.form("staff_edit_form"):
                        new_role=st.selectbox("Role",STAFF_ROLES,index=STAFF_ROLES.index(sr["Role"]) if sr["Role"] in STAFF_ROLES else 0)
                        new_campus=st.selectbox("Campus",CAMPUSES+["All Campuses"],index=(CAMPUSES+["All Campuses"]).index(sr["Campus"]) if sr["Campus"] in CAMPUSES+["All Campuses"] else 0)
                        new_dept=st.text_input("Department / unit",value=sr["Department"])
                        new_email=st.text_input("Institutional email",value=sr["InstitutionalEmail"])
                        new_active=st.selectbox("Account status",["True","False"],index=0 if sr["Active"]!="False" else 1)
                        staff_edit=st.form_submit_button("Save staff changes")
                    if staff_edit:
                        mask=staff["StaffID"]==selected_staff
                        staff.loc[mask,["Role","Campus","Department","InstitutionalEmail","Active"]]=[new_role,new_campus,new_dept,new_email,new_active]
                        save_csv("staff",staff)
                        audit(current_user(),user_role,"Edited staff account",selected_staff)
                        st.success("Staff account updated.")
                        st.rerun()
                tasks=read_csv("task_requests",TASK_REQUEST_COLUMNS)
                st.markdown("#### Pending staff requests")
                todo=tasks[tasks["Status"]=="Pending Review"]
                if todo.empty:
                    st.info("No staff task requests are pending.")
                else:
                    st.dataframe(todo,use_container_width=True)
                    taskid=st.selectbox("Request to review",todo["RequestID"].tolist(),key="task_approval_id")
                    tasknote=st.text_input("Decision note",key="task_review_note")
                    tc1,tc2=st.columns(2)
                    if tc1.button("Approve task request"):
                        tasks.loc[tasks["RequestID"]==taskid,["Status","ReviewedBy","ReviewNote"]]=["Approved",current_user(),tasknote]
                        save_csv("task_requests",tasks)
                        audit(current_user(),user_role,"Approved staff task request",taskid)
                        st.success("Request approved. If it involves a record change, apply that change in the relevant authorised administrative section.")
                        st.rerun()
                    if tc2.button("Reject task request"):
                        tasks.loc[tasks["RequestID"]==taskid,["Status","ReviewedBy","ReviewNote"]]=["Rejected",current_user(),tasknote]
                        save_csv("task_requests",tasks)
                        audit(current_user(),user_role,"Rejected staff task request",taskid)
                        st.warning("Request rejected.")
                        st.rerun()
            with tabs[5]:
                st.markdown("### Public Announcements")
                anns=read_csv("announcements",["NoticeID","Title","Date","Category","Content"])
                if not anns.empty: st.dataframe(anns,use_container_width=True)
                with st.form("announcement_create"):
                    atitle=st.text_input("Announcement title")
                    acat=st.selectbox("Category",["General Notice","Registration","Examination","Academic Calendar","Financial Notice"])
                    acontent=st.text_area("Announcement text")
                    ann_submit=st.form_submit_button("Publish announcement")
                if ann_submit:
                    if atitle.strip() and acontent.strip():
                        anns.loc[len(anns)]=[new_id("NOTICE"),atitle.strip(),date.today().isoformat(),acat,acontent.strip()]
                        save_csv("announcements",anns)
                        audit(current_user(),user_role,"Published announcement",atitle)
                        st.success("Announcement published.")
                        st.rerun()
                    else: st.error("A title and announcement text are required.")
                if not anns.empty:
                    delete_notice=st.selectbox("Select announcement to delete",anns["NoticeID"].tolist(),key="delete_notice")
                    if st.button("Delete selected announcement"):
                        anns=anns[anns["NoticeID"]!=delete_notice]
                        save_csv("announcements",anns)
                        audit(current_user(),user_role,"Deleted announcement",delete_notice)
                        st.rerun()
            with tabs[6]:
                st.markdown("### Departments and Academic Levels")
                d1,d2=st.columns(2)
                with d1:
                    st.markdown("#### Departments")
                    depdf=read_csv("departments",["Department"])
                    for _,dr in depdf.iterrows():
                        st.markdown(f"<div class='notice' style='padding:12px 15px;margin:7px 0'><strong>{safe(dr['Department'])}</strong></div>",unsafe_allow_html=True)
                    with st.form("department_add"):
                        nd=st.text_input("New department name")
                        adddep=st.form_submit_button("Add department")
                    if adddep:
                        if nd.strip() and nd.strip() not in depdf["Department"].tolist():
                            depdf.loc[len(depdf)]=[nd.strip()]
                            save_csv("departments",depdf)
                            audit(current_user(),user_role,"Added department",nd.strip())
                            st.success("Department added.")
                            st.rerun()
                    if not depdf.empty:
                        depdel=st.selectbox("Department to remove",depdf["Department"].tolist(),key="dep_delete")
                        if st.button("Remove department"):
                            depdf=depdf[depdf["Department"]!=depdel]
                            save_csv("departments",depdf)
                            audit(current_user(),user_role,"Removed department",depdel)
                            st.rerun()
                with d2:
                    st.markdown("#### Academic levels")
                    for lvl in LEVELS:
                        st.markdown(f"<div class='notice' style='padding:12px 15px;margin:7px 0'><strong>{lvl}</strong><div class='small-muted'>Academic progression stage</div></div>",unsafe_allow_html=True)
                    st.info("Regular and Extension are study modalities. They are not academic levels.")
                    st.markdown("#### Modality options")
                    st.write(", ".join(MODALITIES))
            with tabs[7]:
                st.markdown("### Grade Submission Review and Approval")
                pending=read_csv("pending_grades",PENDING_GRADE_COLUMNS)
                todo=pending[pending["Status"]=="Pending Review"]
                if todo.empty:
                    st.info("No grade submissions are awaiting review.")
                else:
                    st.dataframe(todo,use_container_width=True)
                    rid=st.selectbox("Select grade submission",todo["RequestID"].tolist(),key="grade_review_id")
                    gr=todo[todo["RequestID"]==rid].iloc[0]
                    st.write(f"**Student:** {gr['FullName']} ({gr['StudentID']}) · **Level:** {gr['Level']}")
                    note=st.text_input("Review note (optional)",key="grade_review_note")
                    ga,grj=st.columns(2)
                    if ga.button("Approve and publish grade"):
                        letter,gp=grade_for_score(float(gr["Score"]))
                        grades=read_csv("grades",GRADE_COLUMNS)
                        grades.loc[len(grades)]=[new_id("GRADE"),gr["StudentID"],gr["FullName"],gr["Level"],gr["CourseCode"],gr["CourseName"],gr["CreditHour"],gr["Score"],letter,gp,gr["Semester"],gr["AcademicYear"],gr["Instructor"],"Approved",current_user(),datetime.now().isoformat(timespec="seconds")]
                        save_csv("grades",grades)
                        pending.loc[pending["RequestID"]==rid,"Status"]="Approved"
                        save_csv("pending_grades",pending)
                        audit(current_user(),user_role,"Approved grade",rid)
                        st.success("Grade approved and published to the student's level-specific record.")
                        st.rerun()
                    if grj.button("Reject grade submission"):
                        pending.loc[pending["RequestID"]==rid,"Status"]="Rejected"
                        save_csv("pending_grades",pending)
                        audit(current_user(),user_role,"Rejected grade",rid)
                        st.warning("Grade submission rejected.")
                        st.rerun()
            with tabs[8]:
                st.markdown("### Student Financial Accounts")
                st.write("Tuition and other charges are recorded by academic level. The student's clearance status is calculated from the total amount due and payments recorded.")
                fin=read_csv("finance",FINANCE_COLUMNS)
                if not fin.empty: st.dataframe(fin,use_container_width=True)
                if not students.empty:
                    with st.form("finance_update"):
                        fsid=st.selectbox("Student",students["StudentID"].tolist())
                        flvl=st.selectbox("Academic level",LEVELS)
                        tuition=st.number_input("Tuition fee (ETB)",min_value=0.0,value=15000.0,step=500.0)
                        other=st.number_input("Other charges (ETB)",min_value=0.0,value=0.0,step=100.0)
                        paid=st.number_input("Total amount paid for this level (ETB)",min_value=0.0,value=0.0,step=500.0)
                        update_fin=st.form_submit_button("Save level financial account")
                    if update_fin:
                        balance=max(0.0,tuition+other-paid)
                        status="Fully Cleared" if balance<=0 else "Outstanding Balance"
                        mask=(fin["StudentID"]==fsid)&(fin["Level"]==flvl)
                        newrow=[fsid,flvl,f"{tuition:.2f}",f"{other:.2f}",f"{paid:.2f}",f"{balance:.2f}",status,date.today().isoformat()]
                        if mask.any():
                            fin.loc[mask,FINANCE_COLUMNS]=newrow
                        else:
                            fin.loc[len(fin)]=newrow
                        save_csv("finance",fin)
                        audit(current_user(),user_role,"Updated student financial account",f"{fsid} / {flvl} / {status}")
                        st.success(f"Financial account saved. Outstanding balance: ETB {balance:,.2f}")
                        st.rerun()
                if not students.empty:
                    fs=st.selectbox("View consolidated student balance",students["StudentID"].tolist(),key="finance_student_summary")
                    sf=fin[fin["StudentID"]==fs] if not fin.empty else pd.DataFrame(columns=FINANCE_COLUMNS)
                    if sf.empty:
                        st.info("No financial accounts have been recorded for this student.")
                    else:
                        total_due=sum(pd.to_numeric(sf["TuitionFeeETB"],errors="coerce").fillna(0)+pd.to_numeric(sf["OtherFeesETB"],errors="coerce").fillna(0))
                        total_paid=sum(pd.to_numeric(sf["PaidETB"],errors="coerce").fillna(0))
                        st.metric("Total outstanding balance (ETB)",f"{max(0,total_due-total_paid):,.2f}")
                        st.dataframe(sf,use_container_width=True)
            with tabs[9]:
                st.markdown("### Official Credential Issuance")
                st.write("Credentials are generated in landscape A4 format. A level transcript contains only grades for the selected level. The diploma becomes available only after Level I–IV completion and full financial clearance.")
                if students.empty:
                    st.info("Register students before issuing credentials.")
                else:
                    sid=st.selectbox("Student",students["StudentID"]+" — "+students["FullName"],key="credential_student").split(" — ")[0]
                    srow=students[students["StudentID"]==sid].iloc[0]
                    student_grades=grades[(grades["StudentID"]==sid)&(grades["Status"]=="Approved")]
                    sf=finance[finance["StudentID"]==sid] if not finance.empty else pd.DataFrame(columns=FINANCE_COLUMNS)
                    total_due=sum(pd.to_numeric(sf["TuitionFeeETB"],errors="coerce").fillna(0)+pd.to_numeric(sf["OtherFeesETB"],errors="coerce").fillna(0)) if not sf.empty else 0
                    total_paid=sum(pd.to_numeric(sf["PaidETB"],errors="coerce").fillna(0)) if not sf.empty else 0
                    balance=max(0,total_due-total_paid)
                    clear=balance<=0
                    completed_levels=set(student_grades.loc[student_grades["Grade"]!="F","Level"].tolist())
                    all_levels_complete=all(l in completed_levels for l in LEVELS)
                    doc_type=st.selectbox("Credential type",["Official Academic Transcript — Level I","Official Academic Transcript — Level II","Official Academic Transcript — Level III","Official Academic Transcript — Level IV","Official TVET Diploma Certificate"])
                    is_diploma=doc_type=="Official TVET Diploma Certificate"
                    target_level=doc_type.rsplit("— ",1)[-1].strip() if not is_diploma else ""
                    if not clear:
                        st.error(f"Credential issuance is blocked until all recorded fees are cleared. Outstanding balance: ETB {balance:,.2f}.")
                    elif is_diploma and not all_levels_complete:
                        st.error("The diploma is unavailable until the student has successfully completed Levels I, II, III, and IV.")
                    else:
                        if is_diploma:
                            credential_grades=student_grades
                        else:
                            credential_grades=student_grades[student_grades["Level"]==target_level]
                        auth_code=f"HBTC-AUTH-{datetime.now().strftime('%Y')}-{secrets.randbelow(999999)+1:06d}"
                        logo_uri=logo_data_uri()
                        photo_uri=""
                        photo_path=srow.get("Photo","")
                        if photo_path and os.path.exists(photo_path):
                            try:
                                with open(photo_path,"rb") as f:
                                    pencoded=base64.b64encode(f.read()).decode("ascii")
                                ext=os.path.splitext(photo_path)[1].lower()
                                pmime="image/jpeg" if ext in (".jpg",".jpeg") else "image/png"
                                photo_uri=f"data:{pmime};base64,{pencoded}"
                            except OSError: pass
                        dob_text=srow.get("DateOfBirth","")
                        grad_year=srow.get("YearOfGraduation","") or str(datetime.now().year)
                        if is_diploma:
                            body_title="TVET DIPLOMA CERTIFICATE — LEVEL IV"
                            body_text=f"""
                            <div class="award">DIPLOMA CERTIFICATE</div>
                            <p class="certify">This is to certify that</p>
                            <h1 class="student-name">{safe(srow['FullName'])}</h1>
                            <p class="certify">Student ID: <strong>{safe(sid)}</strong></p>
                            <p class="certify">having successfully completed the required academic programme across Levels I, II, III and IV in the Department of <strong>{safe(srow['Department'])}</strong>, is awarded this diploma subject to the College's official academic regulations.</p>
                            <div class="cert-details"><span><b>Date of birth:</b> {safe(dob_text)}</span><span><b>Year of entry:</b> {safe(srow['YearOfEntry'])}</span><span><b>Year of graduation:</b> {safe(grad_year)}</span><span><b>Campus:</b> {safe(srow['Campus'])}</span></div>
                            """
                        else:
                            body_title=f"OFFICIAL ACADEMIC TRANSCRIPT — {safe(target_level.upper())}"
                            if credential_grades.empty:
                                grade_rows="<tr><td colspan='7' class='empty-row'>No approved grades are recorded for this level.</td></tr>"
                            else:
                                grade_rows=""
                                for _,g in credential_grades.iterrows():
                                    grade_rows+=f"<tr><td>{safe(g['CourseCode'])}</td><td>{safe(g['CourseName'])}</td><td>{safe(g['CreditHour'])}</td><td>{safe(g['Score'])}</td><td>{safe(g['Grade'])}</td><td>{safe(g['GradePoint'])}</td><td>{safe(g['Semester'])}</td></tr>"
                            credits=pd.to_numeric(credential_grades["CreditHour"],errors="coerce").fillna(0) if not credential_grades.empty else pd.Series(dtype=float)
                            points=pd.to_numeric(credential_grades["GradePoint"],errors="coerce").fillna(0) if not credential_grades.empty else pd.Series(dtype=float)
                            cgpa=(sum(credits*points)/sum(credits)) if len(credits) and sum(credits)>0 else 0
                            body_text=f"""
                            <div class="student-details">
                              <span><b>Student:</b> {safe(srow['FullName'])}</span><span><b>Student ID:</b> {safe(sid)}</span>
                              <span><b>Date of birth:</b> {safe(dob_text)}</span><span><b>Campus:</b> {safe(srow['Campus'])}</span>
                              <span><b>Department:</b> {safe(srow['Department'])}</span><span><b>Modality:</b> {safe(srow['Modality'])}</span>
                              <span><b>Year of entry:</b> {safe(srow['YearOfEntry'])}</span><span><b>Academic year:</b> {safe(srow['AcademicYear'])}</span>
                            </div>
                            <table class="transcript-table"><thead><tr><th>Course code</th><th>Course title</th><th>Credit hours</th><th>Score</th><th>Grade</th><th>Grade point</th><th>Semester</th></tr></thead><tbody>{grade_rows}</tbody></table>
                            <div class="summary-row"><span><b>Level:</b> {safe(target_level)}</span><span><b>Total credits:</b> {sum(credits):.1f}</span><span><b>Level GPA:</b> {cgpa:.2f}</span><span><b>Financial status:</b> Fully Cleared</span></div>
                            """
                        logo_html=f"<img class='college-logo' src='{logo_uri}' alt='College logo'>" if logo_uri else "<div class='logo-placeholder'>HBTC</div>"
                        photo_html=f"<img class='student-photo' src='{photo_uri}' alt='Student photograph'>" if photo_uri else ""
                        doc_html=f"""
                        <html><head><meta charset="utf-8"><style>
                        @page{{size:A4 landscape;margin:8mm}}
                        *{{box-sizing:border-box}}body{{font-family:Arial,sans-serif;color:#17243b;margin:0;background:white}}
                        .print-document{{width:100%;border:2px solid #173f78;padding:9mm;position:relative;min-height:175mm}}
                        .doc-header{{display:grid;grid-template-columns:75px 1fr 75px;align-items:center;border-bottom:3px solid #d6a943;padding-bottom:8px;gap:10px}}
                        .college-logo{{width:68px;height:68px;object-fit:contain}}.logo-placeholder{{width:65px;height:65px;border:2px solid #d6a943;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#173f78;font-weight:900}}
                        .header-text{{text-align:center}}.header-text h2{{font-size:18px;color:#10213f;margin:0 0 4px}}.header-text p{{font-size:9px;margin:2px}}
                        .student-photo{{width:62px;height:76px;object-fit:cover;border:1px solid #9aa8ba}}
                        .doc-title{{text-align:center;font-size:14px;font-weight:900;letter-spacing:.7px;color:#173f78;margin:10px 0}}
                        .student-details{{display:grid;grid-template-columns:repeat(4,1fr);gap:7px 12px;font-size:9px;border:1px solid #dbe4ef;padding:8px;background:#f7f9fc}}
                        .transcript-table{{width:100%;border-collapse:collapse;margin-top:10px;font-size:9px}}
                        .transcript-table th{{background:#173f78;color:white;padding:6px 5px;border:1px solid #173f78;text-align:left}}
                        .transcript-table td{{border:1px solid #cbd5e1;padding:5px}}
                        .transcript-table tr:nth-child(even){{background:#f7f9fc}}.empty-row{{text-align:center;padding:12px!important}}
                        .summary-row{{display:flex;justify-content:space-between;border:1px solid #dbe4ef;background:#f7f9fc;padding:8px;margin-top:8px;font-size:10px}}
                        .award{{text-align:center;color:#173f78;font-size:23px;font-weight:900;letter-spacing:2px;margin-top:12px}}
                        .certify{{text-align:center;font-size:12px;line-height:1.6;max-width:850px;margin:12px auto}}
                        .student-name{{text-align:center;color:#10213f;font-size:25px;border:0;margin:12px 0}}
                        .cert-details{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:25px 0;font-size:10px}}
                        .signatures{{display:grid;grid-template-columns:1fr 1fr;gap:40px;margin-top:24px;font-size:10px;text-align:center}}
                        .sign-line{{border-top:1px solid #17243b;padding-top:5px;margin:20px 15px 0}}
                        .doc-footer{{border-top:2px solid #d6a943;margin-top:15px;padding-top:7px;display:flex;justify-content:space-between;font-size:8px;color:#475569}}
                        </style></head><body><div class="print-document">
                        <div class="doc-header">{logo_html}<div class="header-text"><h2>HANEK TECHNOLOGY AND BUSINESS COLLEGE</h2><p>OFFICE OF THE REGISTRAR</p><p>Wolaita Sodo, Ethiopia · P.O. Box 23 · +251-46-180-3164 / +251916747538</p><p>www.hanekcollege.edu.et · registrar@hanekcollege.edu.et</p></div>{photo_html}</div>
                        <div class="doc-title">{body_title}</div>{body_text}
                        <div class="signatures"><div><div class="sign-line">College President</div></div><div><div class="sign-line">Head Registrar / Authorised Registrar Officer</div></div></div>
                        <div class="doc-footer"><span>Authentication code: <b>{auth_code}</b></span><span>Issued: {date.today().isoformat()}</span><span>Official institutional record · Verify before use</span></div>
                        </div></body></html>
                        """
                        st.components.v1.html(doc_html,height=690,scrolling=True)
                        st.download_button("Save credential as HTML (print-ready landscape A4)",data=doc_html.encode("utf-8"),file_name=f"{sid}_{target_level.replace(' ','_') if target_level else 'Diploma'}_credential.html",mime="text/html")
                        # Create an editable Excel workbook with landscape A4 page setup.
                        excel_buffer=io.BytesIO()
                        with pd.ExcelWriter(excel_buffer,engine="openpyxl") as writer:
                            info_df=pd.DataFrame([
                                ["Institution",APP_NAME],["Credential",body_title],["Student ID",sid],
                                ["Full legal name",srow["FullName"]],["Date of birth",dob_text],
                                ["Campus",srow["Campus"]],["Department",srow["Department"]],
                                ["Modality",srow["Modality"]],["Year of entry",srow["YearOfEntry"]],
                                ["Year of graduation",grad_year if is_diploma else ""],
                                ["Authentication code",auth_code],["Issue date",date.today().isoformat()],
                                ["Financial status","Fully Cleared"],["Level GPA",f"{cgpa:.2f}" if not is_diploma else "N/A"]
                            ])
                            info_df.to_excel(writer,index=False,header=False,sheet_name="Credential")
                            ws=writer.sheets["Credential"]
                            ws.page_setup.orientation="landscape";ws.page_setup.paperSize=ws.PAPERSIZE_A4
                            ws.page_setup.fitToWidth=1;ws.page_setup.fitToHeight=1;ws.sheet_properties.pageSetUpPr.fitToPage=True
                            ws.column_dimensions["A"].width=28;ws.column_dimensions["B"].width=65
                            from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
                            for r in ws.iter_rows():
                                for cell in r:
                                    cell.alignment=Alignment(vertical="center",wrap_text=True)
                                    if cell.column==1:
                                        cell.font=Font(bold=True,color="173F78")
                                        cell.fill=PatternFill("solid",fgColor="EAF0F8")
                            if not is_diploma:
                                credential_grades.to_excel(writer,index=False,startrow=len(info_df)+2,sheet_name="Credential")
                                ws=writer.sheets["Credential"]
                                ws.page_setup.orientation="landscape";ws.page_setup.paperSize=ws.PAPERSIZE_A4
                                ws.page_setup.fitToWidth=1;ws.page_setup.fitToHeight=1;ws.sheet_properties.pageSetUpPr.fitToPage=True
                                for col in ws.columns:
                                    letter=col[0].column_letter
                                    ws.column_dimensions[letter].width=min(max(max(len(str(c.value or "")) for c in col)+2,12),32)
                        st.download_button("Save as Excel workbook (A4 landscape)",data=excel_buffer.getvalue(),file_name=f"{sid}_credential.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                        st.caption("For a Word/PDF printout, open the print-ready credential in a browser, choose Print, and select A4 landscape. A verification code is generated for this issuance; maintain an issuance register before relying on it for external verification.")
            with tabs[10]:
                st.markdown("### System configuration and audit")
                st.write(f"Student records: {len(students)}")
                st.write(f"Staff accounts: {len(staff)}")
                st.write(f"Pending grade requests: {len(pending[pending['Status']=='Pending Review'])}")
                logo=st.file_uploader("Upload college logo",type=["png","jpg","jpeg"])
                if logo:
                    ext=os.path.splitext(logo.name)[1].lower()
                    if ext not in (".png",".jpg",".jpeg"): ext=".png"
                    with open(FILES["logo"],"wb") as f:f.write(logo.getbuffer())
                    audit(current_user(),user_role,"Uploaded institutional logo",logo.name)
                    st.success("College logo updated.")
                    st.rerun()
                st.markdown("#### Audit log")
                st.dataframe(read_csv("audit",AUDIT_COLUMNS).iloc[::-1],use_container_width=True)

# Staff portal
elif portal == "Staff and Registrar Portal":
    make_brand()
    st.title("Staff and Registrar Portal")
    if "staff_user" not in st.session_state:
        with st.form("staff_login"):
            staff_id=st.text_input("Staff ID")
            staff_pw=st.text_input("Password",type="password")
            staff_login=st.form_submit_button("Sign in")
        if staff_login:
            staff=read_csv("staff",STAFF_COLUMNS)
            match=staff[(staff["StaffID"]==staff_id)&(staff["Active"]!="False")]
            valid=None
            for idx,row in match.iterrows():
                if verify_password(staff_pw,row["PasswordHash"]):
                    valid=(idx,row)
                    break
            if valid:
                idx,row=valid
                if not str(row["PasswordHash"]).startswith("pbkdf2_sha256$"):
                    staff.at[idx,"PasswordHash"]=hash_password(staff_pw);save_csv("staff",staff)
                st.session_state["staff_user"]=row["StaffID"]
                st.session_state["staff_name"]=row["FullName"]
                st.session_state["staff_role"]=row["Role"]
                audit(row["StaffID"],row["Role"],"Successful staff login")
                st.rerun()
            else: st.error("The Staff ID or password is invalid, or the account is inactive.")
    else:
        sid=st.session_state["staff_user"]
        name=st.session_state["staff_name"]
        role=st.session_state["staff_role"]
        st.success(f"Welcome, {name} · {role}")
        if st.button("Sign out of staff portal"):
            audit(sid,role,"Signed out")
            for k in ["staff_user","staff_name","staff_role"]:st.session_state.pop(k,None)
            st.rerun()
        tabs=st.tabs(["My Workbench","Submit a Grade","Request an Administrative Action"])
        with tabs[0]:
            st.write("Staff access is role-based. Student records are limited to the student's currently approved academic level. Staff members cannot directly modify official records from this portal.")
            tasks=read_csv("task_requests",TASK_REQUEST_COLUMNS)
            mine=tasks[tasks["StaffID"]==sid]
            st.markdown("#### My administrative requests")
            st.dataframe(mine,use_container_width=True)
            if role in ["Instructor / Lecturer","Department Head"]:
                students=read_csv("students",STUDENT_COLUMNS)
                st.markdown("#### Students at their currently approved level")
                allowed=students[(students["Active"]!="False")]
                staff_df=read_csv("staff",STAFF_COLUMNS)
                sr=staff_df[staff_df["StaffID"]==sid]
                if not sr.empty:
                    scampus=sr.iloc[0]["Campus"]; sdept=sr.iloc[0]["Department"]
                    if scampus!="All Campuses": allowed=allowed[allowed["Campus"]==scampus]
                    if role=="Instructor / Lecturer" and sdept: allowed=allowed[allowed["Department"]==sdept]
                if allowed.empty: st.info("No active students are assigned to your authorised campus/department.")
                else: st.dataframe(allowed[["StudentID","FullName","Campus","Department","ProgramLevel","AcademicYear"]],use_container_width=True)
        with tabs[1]:
            if role not in ["Instructor / Lecturer","Department Head"]:
                st.info("Grade submission is available only to authorised instructional roles.")
            else:
                students=read_csv("students",STUDENT_COLUMNS)
                staffdf=read_csv("staff",STAFF_COLUMNS)
                staffrow=staffdf[staffdf["StaffID"]==sid].iloc[0]
                allowed=students[students["Active"]!="False"]
                if staffrow["Campus"]!="All Campuses": allowed=allowed[allowed["Campus"]==staffrow["Campus"]]
                if role=="Instructor / Lecturer" and staffrow["Department"]: allowed=allowed[allowed["Department"]==staffrow["Department"]]
                if allowed.empty: st.info("No students are available within your assigned scope.")
                else:
                    with st.form("submit_grade"):
                        target=st.selectbox("Student",allowed["StudentID"]+" — "+allowed["FullName"])
                        student_id=target.split(" — ")[0]
                        studentrow=allowed[allowed["StudentID"]==student_id].iloc[0]
                        level=studentrow["ProgramLevel"]
                        st.info(f"Student's approved registration level: {level}. Grades can only be submitted for this level.")
                        code=st.text_input("Course code")
                        course=st.text_input("Course title")
                        credit=st.number_input("Credit hours",min_value=0.5,max_value=30.0,value=3.0,step=0.5)
                        score=st.number_input("Assessment score",min_value=0.0,max_value=100.0,value=75.0,step=0.5)
                        semester=st.selectbox("Semester",["Semester I","Semester II","Summer / Special Semester"])
                        acad=st.text_input("Academic year",value=studentrow["AcademicYear"])
                        submit_grade=st.form_submit_button("Submit grade for administrative approval")
                    if submit_grade:
                        if not code.strip() or not course.strip(): st.error("Course code and course title are required.")
                        else:
                            pending=read_csv("pending_grades",PENDING_GRADE_COLUMNS)
                            pending.loc[len(pending)]=[new_id("GRREQ"),student_id,studentrow["FullName"],level,code.strip(),course.strip(),str(credit),str(score),semester,acad,name,datetime.now().isoformat(timespec="seconds"),"Pending Review"]
                            save_csv("pending_grades",pending)
                            audit(sid,role,"Submitted grade for approval",f"{student_id}/{level}/{code}")
                            st.success("Grade submitted. It will not appear on the official transcript until an administrator approves it.")
        with tabs[2]:
            with st.form("staff_task_request"):
                tasktype=st.selectbox("Request type",["Student record correction","Level registration support","Financial account update","Credential request","Staff/account issue","Other administrative request"])
                related=st.text_input("Related Student ID (if applicable)")
                description=st.text_area("Describe the requested action and supporting reason")
                request_task=st.form_submit_button("Submit request for approval")
            if request_task:
                if not description.strip(): st.error("Describe the requested action.")
                else:
                    tasks=read_csv("task_requests",TASK_REQUEST_COLUMNS)
                    tasks.loc[len(tasks)]=[new_id("TASK"),sid,name,role,tasktype,description.strip(),related.strip(),datetime.now().isoformat(timespec="seconds"),"Pending Review","",""]
                    save_csv("task_requests",tasks)
                    audit(sid,role,"Submitted administrative task request",tasktype)
                    st.success("Request submitted. No official record will change until the authorised administrator reviews it.")

# Student portal
elif portal == "Student Portal":
    make_brand()
    st.title("Student Portal")
    if "student_user" not in st.session_state:
        with st.form("student_login"):
            student_id=st.text_input("Student ID")
            student_pw=st.text_input("Password",type="password")
            student_login=st.form_submit_button("Sign in")
        if student_login:
            students=read_csv("students",STUDENT_COLUMNS)
            match=students[(students["StudentID"]==student_id)&(students["Active"]!="False")]
            valid=None
            for idx,row in match.iterrows():
                if verify_password(student_pw,row["PasswordHash"]):
                    valid=(idx,row);break
            if valid:
                idx,row=valid
                if not str(row["PasswordHash"]).startswith("pbkdf2_sha256$"):
                    students.at[idx,"PasswordHash"]=hash_password(student_pw);save_csv("students",students)
                st.session_state["student_user"]=row["StudentID"]
                audit(row["StudentID"],"Student","Successful login")
                st.rerun()
            else:st.error("The Student ID or password is invalid, or the account is inactive.")
    else:
        sid=st.session_state["student_user"]
        students=read_csv("students",STUDENT_COLUMNS)
        found=students[students["StudentID"]==sid]
        if found.empty:
            st.error("Your student record could not be found.")
            st.session_state.pop("student_user",None)
            st.stop()
        student=found.iloc[0]
        st.success(f"Welcome, {student['FullName']} · {student['ProgramLevel']}")
        if st.button("Sign out of student portal"):
            audit(sid,"Student","Signed out");st.session_state.pop("student_user",None);st.rerun()
        tabs=st.tabs(["My Profile","My Grades","Level Registration","Financial Status","My Credentials"])
        with tabs[0]:
            p1,p2=st.columns([1,2])
            with p1:
                photo=student.get("Photo","")
                if photo and os.path.exists(photo):st.image(photo,width=150)
                else:st.info("No profile photograph has been uploaded.")
                with st.form("student_photo_form"):
                    upload=st.file_uploader("Upload or update profile photograph",type=["png","jpg","jpeg"])
                    photo_submit=st.form_submit_button("Submit photograph for approval")
                if photo_submit:
                    if upload is None:st.error("Choose a photograph first.")
                    else:
                        ext=os.path.splitext(upload.name)[1].lower()
                        if ext not in (".png",".jpg",".jpeg"):ext=".png"
                        path=os.path.join(PHOTO_DIR,f"{sid.replace('/','_')}{ext}")
                        with open(path,"wb") as f:f.write(upload.getbuffer())
                        students.loc[students["StudentID"]==sid,["Photo","PhotoStatus"]]=[path,"Pending Approval"]
                        save_csv("students",students);audit(sid,"Student","Uploaded profile photograph","Pending approval")
                        st.success("Photograph submitted for administrative approval.");st.rerun()
            with p2:
                st.markdown("#### Official student information")
                for label,key in [("Student ID","StudentID"),("Full legal name","FullName"),("Date of birth","DateOfBirth"),("Campus","Campus"),("Department","Department"),("Current level","ProgramLevel"),("Study modality","Modality"),("Year of entry","YearOfEntry"),("Academic year","AcademicYear"),("Photo status","PhotoStatus")]:
                    st.write(f"**{label}:** {student.get(key,'')}")
        with tabs[1]:
            grades=read_csv("grades",GRADE_COLUMNS)
            my=grades[(grades["StudentID"]==sid)&(grades["Status"]=="Approved")&(grades["Level"]==student["ProgramLevel"])]
            st.caption(f"Access is restricted to the currently approved registration level: {student['ProgramLevel']}.")
            if my.empty:st.info("No approved grades are available for your current level.")
            else:
                st.dataframe(my.drop(columns=["ApprovedBy"],errors="ignore"),use_container_width=True)
                credits=pd.to_numeric(my["CreditHour"],errors="coerce").fillna(0)
                points=pd.to_numeric(my["GradePoint"],errors="coerce").fillna(0)
                gpa=sum(credits*points)/sum(credits) if sum(credits)>0 else 0
                st.metric("Current-level GPA",f"{gpa:.2f}")
        with tabs[2]:
            current=student["ProgramLevel"]
            idx=level_index(current)
            if idx<0:st.error("Your academic level needs administrative correction.")
            elif idx==len(LEVELS)-1:st.success("You are registered at Level IV, the final level in the current programme structure.")
            else:
                next_level=LEVELS[idx+1]
                st.write(f"Current level: **{current}**")
                st.write(f"Requested next level: **{next_level}**")
                mygrades=read_csv("grades",GRADE_COLUMNS)
                level_grades=mygrades[(mygrades["StudentID"]==sid)&(mygrades["Level"]==current)&(mygrades["Status"]=="Approved")]
                passed=not level_grades.empty and (level_grades["Grade"]!="F").all()
                if not passed:
                    st.warning("Your level-registration request may be submitted, but approval requires the College to verify successful completion of the current level. Ensure all required modules have been graded.")
                reqs=read_csv("level_requests",LEVEL_REQUEST_COLUMNS)
                existing=reqs[(reqs["StudentID"]==sid)&(reqs["RequestedLevel"]==next_level)&(reqs["Status"]=="Pending Review")]
                if not existing.empty:
                    st.info("A request for the next level is already awaiting administrative review.")
                else:
                    with st.form("next_level_request"):
                        next_acad=st.text_input("Next academic year",value=f"{datetime.now().year}/{datetime.now().year+1}")
                        reason=st.text_area("Additional information (optional)")
                        send=st.form_submit_button(f"Request registration for {next_level}")
                    if send:
                        # Store the reason in a separate audit event; request is not auto-approved.
                        reqs.loc[len(reqs)]=[new_id("LVLREQ"),sid,student["FullName"],current,next_level,next_acad,datetime.now().isoformat(timespec="seconds"),"Pending Review","",""]
                        save_csv("level_requests",reqs)
                        audit(sid,"Student","Requested next-level registration",f"{current} -> {next_level}. {reason}")
                        st.success("Your request has been submitted. You remain registered at your current level until the College approves the request.")
        with tabs[3]:
            finance=read_csv("finance",FINANCE_COLUMNS)
            sf=finance[finance["StudentID"]==sid]
            if sf.empty:st.info("No financial account has been recorded for your student ID.")
            else:
                for _,r in sf.iterrows():
                    due=float(r["TuitionFeeETB"] or 0)+float(r["OtherFeesETB"] or 0)
                    paid=float(r["PaidETB"] or 0)
                    balance=max(0,due-paid)
                    st.markdown(f"<div class='metric-card'><div class='metric-label'>{safe(r['Level'])} · Financial status</div><div class='metric-value'>ETB {balance:,.2f}</div><div>{'Fully cleared' if balance<=0 else 'Outstanding balance'} · Tuition ETB {float(r['TuitionFeeETB'] or 0):,.2f} · Other charges ETB {float(r['OtherFeesETB'] or 0):,.2f} · Paid ETB {paid:,.2f}</div></div>",unsafe_allow_html=True)
                total_due=sum(pd.to_numeric(sf["TuitionFeeETB"],errors="coerce").fillna(0)+pd.to_numeric(sf["OtherFeesETB"],errors="coerce").fillna(0))
                total_paid=sum(pd.to_numeric(sf["PaidETB"],errors="coerce").fillna(0))
                st.metric("Total outstanding balance (ETB)",f"{max(0,total_due-total_paid):,.2f}")
        with tabs[4]:
            finance=read_csv("finance",FINANCE_COLUMNS)
            sf=finance[finance["StudentID"]==sid]
            due=sum(pd.to_numeric(sf["TuitionFeeETB"],errors="coerce").fillna(0)+pd.to_numeric(sf["OtherFeesETB"],errors="coerce").fillna(0)) if not sf.empty else 0
            paid=sum(pd.to_numeric(sf["PaidETB"],errors="coerce").fillna(0)) if not sf.empty else 0
            if due-paid>0:st.error(f"Credentials are unavailable while a balance of ETB {due-paid:,.2f} remains outstanding.")
            else:
                grades=read_csv("grades",GRADE_COLUMNS)
                mine=grades[(grades["StudentID"]==sid)&(grades["Level"]==student["ProgramLevel"])&(grades["Status"]=="Approved")]
                st.write("Your current-level transcript can be requested from the College's Official Credential Issuance section. This portal currently displays your approved current-level grades only.")
                if mine.empty:st.info("No approved grades are available for the current level.")
                else:st.dataframe(mine[["Level","CourseCode","CourseName","CreditHour","Score","Grade","Semester","AcademicYear"]],use_container_width=True)

st.markdown("<div class='footer'><strong>HANEK TECHNOLOGY AND BUSINESS COLLEGE</strong><br>Multi-Campus Student Information and Registrar System<br><span class='small-muted'>Software Developer: Ebirawi Henok Loha · Tel: +251965514327 / +251916070065 · Email: henokebirawi3@gmail.com<br>Institutional system design and development · © 2026 Ebirawi Henok Loha · All rights reserved</span></div>",unsafe_allow_html=True)
