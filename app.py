import streamlit as st
import pandas as pd
import os
from PIL import Image

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Hanek Technology and Business College - SIS & Registrar",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM STYLING & UI ENHANCEMENTS ---
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #4B5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    .developer-footer {
        text-align: center;
        font-size: 0.95rem;
        color: #374151;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 2px solid #E5E7EB;
        background-color: #F9FAFB;
        border-radius: 0.5rem;
        padding-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE SETUP (CSV Files) ---
STUDENTS_FILE = "students.csv"
GRADES_FILE = "grades.csv"
STAFF_FILE = "staff.csv"

def init_db():
    if not os.path.exists(STUDENTS_FILE):
        df_students = pd.DataFrame(columns=[
            "StudentID", "FullName", "Department", "Campus", "Level", 
            "AcademicYear", "EnrollmentStatus", "PhotoPath"
        ])
        df_students.to_csv(STUDENTS_FILE, index=False)
        
    if not os.path.exists(GRADES_FILE):
        df_grades = pd.DataFrame(columns=[
            "StudentID", "FullName", "Department", "Level", 
            "Semester", "CourseCode", "CourseTitle", "CreditHours", 
            "Score", "Grade", "GradePoints"
        ])
        df_grades.to_csv(GRADES_FILE, index=False)

    if not os.path.exists(STAFF_FILE):
        df_staff = pd.DataFrame(columns=[
            "StaffID", "FullName", "Role", "Department", "Campus", "Email", "Phone", "PhotoPath"
        ])
        df_staff.to_csv(STAFF_FILE, index=False)

init_db()

# --- HELPER FUNCTIONS ---
def calculate_grade_point(score):
    if score >= 90: return "A+", 4.0
    elif score >= 85: return "A", 4.0
    elif score >= 80: return "A-", 3.75
    elif score >= 75: return "B+", 3.3
    elif score >= 70: return "B", 3.0
    elif score >= 65: return "B-", 2.75
    elif score >= 60: return "C+", 2.3
    elif score >= 50: return "C", 2.0
    elif score >= 45: return "D", 1.0
    else: return "F", 0.0

# --- AUTHENTICATION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

# --- SIDEBAR NAVIGATION & LOGIN ---
st.sidebar.markdown("### 🎓 Hanek College Portal")
st.sidebar.markdown("---")

if not st.session_state.logged_in:
    st.sidebar.subheader("🔒 System Login")
    login_role = st.sidebar.selectbox("Login As", ["Admin / Registrar", "Staff / Instructor", "Student"])
    username_input = st.sidebar.text_input("Username / ID")
    password_input = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        if login_role == "Admin / Registrar" and username_input == "admin" and password_input == "password123":
            st.session_state.logged_in = True
            st.session_state.role = "Admin"
            st.session_state.username = "admin"
            st.rerun()
        elif login_role == "Staff / Instructor" and username_input == "staff" and password_input == "staff123":
            st.session_state.logged_in = True
            st.session_state.role = "Staff"
            st.session_state.username = "staff"
            st.rerun()
        elif login_role == "Student":
            df_s = pd.read_csv(STUDENTS_FILE)
            if username_input in df_s["StudentID"].values:
                st.session_state.logged_in = True
                st.session_state.role = "Student"
                st.session_state.username = username_input
                st.rerun()
            else:
                st.sidebar.error("Invalid Student ID!")
        else:
            st.sidebar.error("Invalid credentials!")
    st.stop()

else:
    st.sidebar.success(f"Logged in as: **{st.session_state.username} ({st.session_state.role})**")
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = None
        st.rerun()
    st.sidebar.markdown("---")

# --- MAIN APP INTERFACE ---
st.markdown('<div class="main-header">Hanek Technology and Business College</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Commercial Online Registrar & Student Information System (Multi-Campus TVET & Higher Education)</div>', unsafe_allow_html=True)

# Navigation Menu based on Role
if st.session_state.role in ["Admin", "Registrar"]:
    menu = st.sidebar.radio("Navigation", [
        "Dashboard Overview", 
        "Student Admission & Management", 
        "Staff Directory Management", 
        "Grade Entry & Management", 
        "Official Transcript Generator"
    ])
elif st.session_state.role == "Staff":
    menu = st.sidebar.radio("Navigation", [
        "Dashboard Overview", 
        "Staff Directory Management", 
        "Grade Entry & Management"
    ])
else:  # Student Role
    menu = st.sidebar.radio("Navigation", [
        "My Student Profile", 
        "My Grade Records & Transcript"
    ])

# ==========================================
# 1. DASHBOARD OVERVIEW
# ==========================================
if menu == "Dashboard Overview":
    st.subheader("📊 Institutional Dashboard")
    df_students = pd.read_csv(STUDENTS_FILE)
    df_grades = pd.read_csv(GRADES_FILE)
    df_staff = pd.read_csv(STAFF_FILE)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Students Registered", len(df_students))
    with col2:
        st.metric("Total Staff Members", len(df_staff))
    with col3:
        st.metric("Total Grades Recorded", len(df_grades))
    with col4:
        st.metric("Active Campuses", "4 (Wolaita Sodo, Basketo, Boloso Bombe, Jinka)")
        
    st.markdown("---")
    st.info("💡 **System Notice:** Use the sidebar to manage students with uploaded ID photos, staff profiles, multi-level grade entries, and official transcripts.")

# ==========================================
# 2. STUDENT ADMISSION & MANAGEMENT (CRUD)
# ==========================================
elif menu == "Student Admission & Management":
    st.subheader("📝 Student Admission & Profile Management")
    
    df_students = pd.read_csv(STUDENTS_FILE)
    
    tab1, tab2 = st.tabs(["Register New Student", "View / Edit / Delete Students"])
    
    with tab1:
        with st.form("admission_form"):
            col1, col2 = st.columns(2)
            with col1:
                student_id = st.text_input("Student ID (e.g., CBM-0144-16)")
                full_name = st.text_input("Full Name")
                department = st.selectbox("Department", [
                    "Cooperative Accounting and Auditing",
                    "Cooperative Business Management",
                    "Cooperative Marketing",
                    "Hardware & Network Systems (HNS)",
                    "Natural Resource Management",
                    "Crop Production"
                ])
                campus = st.selectbox("Campus", ["Wolaita Sodo", "Basketo", "Boloso Bombe", "Jinka"])
            with col2:
                level = st.selectbox("TVET Level", ["Level I", "Level II", "Level III", "Level IV"])
                academic_year = st.text_input("Academic Year", "2024/2025")
                status = st.selectbox("Enrollment Status", ["Active", "Graduated", "Suspended", "Withdrawn"])
                photo = st.file_uploader("Upload Student Profile / Temporary ID Photo", type=["jpg", "png", "jpeg"])
                
            submitted = st.form_submit_button("Register Student")
            if submitted:
                if not student_id or not full_name:
                    st.error("Please fill in Student ID and Full Name!")
                elif student_id in df_students["StudentID"].values:
                    st.error("A student with this ID already exists!")
                else:
                    photo_path = ""
                    if photo is not None:
                        os.makedirs("uploads", exist_ok=True)
                        photo_path = os.path.join("uploads", f"{student_id}_{photo.name}")
                        with open(photo_path, "wb") as f:
                            f.write(photo.getbuffer())
                            
                    new_row = pd.DataFrame([{
                        "StudentID": student_id, "FullName": full_name,
                        "Department": department, "Campus": campus, "Level": level,
                        "AcademicYear": academic_year, "EnrollmentStatus": status, "PhotoPath": photo_path
                    }])
                    df_students = pd.concat([df_students, new_row], ignore_index=True)
                    df_students.to_csv(STUDENTS_FILE, index=False)
                    st.success(f"Student {full_name} registered successfully with ID photo!")
                    st.rerun()
                    
    with tab2:
        st.markdown("### Registered Students Directory")
        if len(df_students) > 0:
            selected_edit_id = st.selectbox("Select Student ID to Edit/Delete", df_students["StudentID"].values)
            student_row = df_students[df_students["StudentID"] == selected_edit_id].iloc[0]
            
            with st.form("edit_student_form"):
                new_name = st.text_input("Full Name", value=student_row["FullName"])
                new_dept = st.selectbox("Department", [
                    "Cooperative Accounting and Auditing", "Cooperative Business Management",
                    "Cooperative Marketing", "Hardware & Network Systems (HNS)",
                    "Natural Resource Management", "Crop Production"
                ], index=["Cooperative Accounting and Auditing", "Cooperative Business Management", "Cooperative Marketing", "Hardware & Network Systems (HNS)", "Natural Resource Management", "Crop Production"].index(student_row["Department"]) if student_row["Department"] in ["Cooperative Accounting and Auditing", "Cooperative Business Management", "Cooperative Marketing", "Hardware & Network Systems (HNS)", "Natural Resource Management", "Crop Production"] else 0)
                new_campus = st.selectbox("Campus", ["Wolaita Sodo", "Basketo", "Boloso Bombe", "Jinka"], index=["Wolaita Sodo", "Basketo", "Boloso Bombe", "Jinka"].index(student_row["Campus"]) if student_row["Campus"] in ["Wolaita Sodo", "Basketo", "Boloso Bombe", "Jinka"] else 0)
                new_level = st.selectbox("TVET Level", ["Level I", "Level II", "Level III", "Level IV"], index=["Level I", "Level II", "Level III", "Level IV"].index(student_row["Level"]) if student_row["Level"] in ["Level I", "Level II", "Level III", "Level IV"] else 0)
                new_status = st.selectbox("Enrollment Status", ["Active", "Graduated", "Suspended", "Withdrawn"], index=["Active", "Graduated", "Suspended", "Withdrawn"].index(student_row["EnrollmentStatus"]) if student_row["EnrollmentStatus"] in ["Active", "Graduated", "Suspended", "Withdrawn"] else 0)
                
                col_up1, col_up2 = st.columns(2)
                with col_up1:
                    update_btn = st.form_submit_button("Update Student Info")
                with col_up2:
                    delete_btn = st.form_submit_button("Delete Student Profile")
                    
                if update_btn:
                    df_students.loc[df_students["StudentID"] == selected_edit_id, "FullName"] = new_name
                    df_students.loc[df_students["StudentID"] == selected_edit_id, "Department"] = new_dept
                    df_students.loc[df_students["StudentID"] == selected_edit_id, "Campus"] = new_campus
                    df_students.loc[df_students["StudentID"] == selected_edit_id, "Level"] = new_level
                    df_students.loc[df_students["StudentID"] == selected_edit_id, "EnrollmentStatus"] = new_status
                    df_students.to_csv(STUDENTS_FILE, index=False)
                    st.success("Student information updated successfully!")
                    st.rerun()
                    
                if delete_btn:
                    df_students = df_students[df_students["StudentID"] != selected_edit_id]
                    df_students.to_csv(STUDENTS_FILE, index=False)
                    st.warning("Student profile deleted successfully!")
                    st.rerun()
                    
            st.dataframe(df_students, use_container_width=True)
        else:
            st.info("No students registered yet.")

# ==========================================
# 3. STAFF DIRECTORY MANAGEMENT (CRUD)
# ==========================================
elif menu == "Staff Directory Management":
    st.subheader("👥 Staff & Instructor Profile Directory")
    
    df_staff = pd.read_csv(STAFF_FILE)
    tab1, tab2 = st.tabs(["Register New Staff", "View / Edit / Delete Staff"])
    
    with tab1:
        with st.form("staff_form"):
            col1, col2 = st.columns(2)
            with col1:
                staff_id = st.text_input("Staff ID (e.g., STF-001)")
                staff_name = st.text_input("Full Name")
                staff_role = st.selectbox("Role", ["Instructor", "Registrar Officer", "Department Head", "Campus Administrator"])
                staff_dept = st.text_input("Department / Unit")
            with col2:
                staff_campus = st.selectbox("Campus", ["Wolaita Sodo", "Basketo", "Boloso Bombe", "Jinka"])
                staff_email = st.text_input("Email Address")
                staff_phone = st.text_input("Phone Number")
                staff_photo = st.file_uploader("Upload Staff Photo", type=["jpg", "png", "jpeg"])
                
            if st.form_submit_button("Register Staff"):
                if not staff_id or not staff_name:
                    st.error("Please fill in Staff ID and Name!")
                elif staff_id in df_staff["StaffID"].values:
                    st.error("Staff ID already exists!")
                else:
                    photo_path = ""
                    if staff_photo is not None:
                        os.makedirs("uploads", exist_ok=True)
                        photo_path = os.path.join("uploads", f"{staff_id}_{staff_photo.name}")
                        with open(photo_path, "wb") as f:
                            f.write(staff_photo.getbuffer())
                            
                    new_staff_row = pd.DataFrame([{
                        "StaffID": staff_id, "FullName": staff_name, "Role": staff_role,
                        "Department": staff_dept, "Campus": staff_campus, "Email": staff_email,
                        "Phone": staff_phone, "PhotoPath": photo_path
                    }])
                    df_staff = pd.concat([df_staff, new_staff_row], ignore_index=True)
                    df_staff.to_csv(STAFF_FILE, index=False)
                    st.success(f"Staff member {staff_name} registered successfully!")
                    st.rerun()
                    
    with tab2:
        st.markdown("### Existing Staff Directory")
        if len(df_staff) > 0:
            selected_staff_id = st.selectbox("Select Staff ID to Edit/Delete", df_staff["StaffID"].values)
            s_row = df_staff[df_staff["StaffID"] == selected_staff_id].iloc[0]
            
            with st.form("edit_staff_form"):
                e_name = st.text_input("Full Name", value=s_row["FullName"])
                e_role = st.selectbox("Role", ["Instructor", "Registrar Officer", "Department Head", "Campus Administrator"], index=0)
                e_dept = st.text_input("Department", value=s_row["Department"])
                e_campus = st.selectbox("Campus", ["Wolaita Sodo", "Basketo", "Boloso Bombe", "Jinka"], index=0)
                e_email = st.text_input("Email", value=s_row["Email"])
                e_phone = st.text_input("Phone", value=s_row["Phone"])
                
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    up_staff = st.form_submit_button("Update Staff")
                with col_s2:
                    del_staff = st.form_submit_button("Delete Staff")
                    
                if up_staff:
                    df_staff.loc[df_staff["StaffID"] == selected_staff_id, "FullName"] = e_name
                    df_staff.loc[df_staff["StaffID"] == selected_staff_id, "Role"] = e_role
                    df_staff.loc[df_staff["StaffID"] == selected_staff_id, "Department"] = e_dept
                    df_staff.loc[df_staff["StaffID"] == selected_staff_id, "Campus"] = e_campus
                    df_staff.loc[df_staff["StaffID"] == selected_staff_id, "Email"] = e_email
                    df_staff.loc[df_staff["StaffID"] == selected_staff_id, "Phone"] = e_phone
                    df_staff.to_csv(STAFF_FILE, index=False)
                    st.success("Staff updated successfully!")
                    st.rerun()
                    
                if del_staff:
                    df_staff = df_staff[df_staff["StaffID"] != selected_staff_id]
                    df_staff.to_csv(STAFF_FILE, index=False)
                    st.warning("Staff member deleted successfully!")
                    st.rerun()
                    
            st.dataframe(df_staff, use_container_width=True)
        else:
            st.info("No staff members registered yet.")

# ==========================================
# 4. GRADE ENTRY & MANAGEMENT (CRUD & Level Selector)
# ==========================================
elif menu == "Grade Entry & Management":
    st.subheader("📋 Academic Grade Entry & Management")
    
    df_students = pd.read_csv(STUDENTS_FILE)
    df_grades = pd.read_csv(GRADES_FILE)
    
    if len(df_students) == 0:
        st.warning("Please register at least one student before entering grades.")
    else:
        tab1, tab2 = st.tabs(["Enter New Grade", "Manage / Edit / Delete Grades"])
        
        with tab1:
            student_ids = df_students["StudentID"].values
            selected_id = st.selectbox("Select Student ID", student_ids)
            
            student_info = df_students[df_students["StudentID"] == selected_id].iloc[0]
            st.info(f"**Student:** {student_info['FullName']} | **Dept:** {student_info['Department']} | **Campus:** {student_info['Campus']}")
            
            with st.form("grade_form"):
                col1, col2 = st.columns(2)
                with col1:
                    grade_level = st.selectbox("TVET Level for this Course", ["Level I", "Level II", "Level III", "Level IV"])
                    semester = st.selectbox("Semester", ["Semester I", "Semester II"])
                    course_code = st.text_input("Module Code & Unit of Competence (e.g., CAB ACC1 0710)")
                    course_title = st.text_input("Course / Module Title")
                with col2:
                    credit_hours = st.number_input("Credit Hours (Hr)", min_value=1, max_value=10, value=3)
                    score = st.number_input("Assessment Score (0 - 100)", min_value=0.0, max_value=100.0, value=85.0)
                    
                if st.form_submit_button("Save Grade"):
                    grade_letter, grade_point_val = calculate_grade_point(score)
                    total_gp = grade_point_val * credit_hours
                    
                    new_grade = pd.DataFrame([{
                        "StudentID": selected_id, "FullName": student_info["FullName"],
                        "Department": student_info["Department"], "Level": grade_level,
                        "Semester": semester, "CourseCode": course_code, "CourseTitle": course_title,
                        "CreditHours": credit_hours, "Score": score, "Grade": grade_letter, "GradePoints": total_gp
                    }])
                    df_grades = pd.concat([df_grades, new_grade], ignore_index=True)
                    df_grades.to_csv(GRADES_FILE, index=False)
                    st.success(f"Grade recorded! Score: {score} -> Grade: {grade_letter}")
                    st.rerun()
                    
        with tab2:
            st.markdown("### Existing Grade Records")
            if len(df_grades) > 0:
                filter_id = st.selectbox("Filter by Student ID", ["All"] + list(df_grades["StudentID"].unique()))
                temp_df = df_grades if filter_id == "All" else df_grades[df_grades["StudentID"] == filter_id]
                
                st.dataframe(temp_df, use_container_width=True)
                
                st.markdown("### Delete a Grade Record")
                grade_index_to_delete = st.selectbox("Select Row Index to Delete", temp_df.index)
                if st.button("Delete Selected Grade"):
                    df_grades = df_grades.drop(index=grade_index_to_delete).reset_index(drop=True)
                    df_grades.to_csv(GRADES_FILE, index=False)
                    st.warning("Grade record deleted successfully!")
                    st.rerun()
            else:
                st.info("No grade records entered yet.")

# ==========================================
# 5. OFFICIAL TRANSCRIPT GENERATOR
# ==========================================
elif menu == "Official Transcript Generator":
    st.subheader("📜 Official Academic Transcript Generator")
    
    df_students = pd.read_csv(STUDENTS_FILE)
    df_grades = pd.read_csv(GRADES_FILE)
    
    if len(df_students) == 0:
        st.warning("No students available.")
    else:
        selected_id = st.selectbox("Select Student ID for Transcript", df_students["StudentID"].values)
        student = df_students[df_students["StudentID"] == selected_id].iloc[0]
        s_grades = df_grades[df_grades["StudentID"] == selected_id]
        
        generate_transcript = st.button("Generate Official Transcript")
            
        if generate_transcript:
            st.markdown("---")
            
            # Transcript Header with Photo Preview
            col_ph1, col_ph2, col_ph3 = st.columns([1, 2, 1])
            with col_ph1:
                if pd.notna(student["PhotoPath"]) and student["PhotoPath"] != "" and os.path.exists(student["PhotoPath"]):
                    st.image(student["PhotoPath"], width=120, caption="Temporary ID Photo")
                else:
                    st.info("No Photo")
            with col_ph2:
                st.markdown("<h3 style='text-align: center; color: #1E3A8A; margin-bottom: 0;'>HANEK TECHNOLOGY AND BUSINESS COLLEGE</h3>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; font-weight: 600;'>OFFICIAL ACADEMIC TRANSCRIPT | Campus: {student['Campus']}</p>", unsafe_allow_html=True)
            with col_ph3:
                st.write("")
                
            st.markdown("---")
            
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.write(f"**Student Name:** {student['FullName']}")
                st.write(f"**Student ID:** {student['StudentID']}")
                st.write(f"**Department:** {student['Department']}")
            with col_info2:
                st.write(f"**Admission Level:** {student['Level']}")
                st.write(f"**Academic Year:** {student['AcademicYear']}")
                st.write(f"**Status:** {student['EnrollmentStatus']}")
                
            st.markdown("---")
            
            if len(s_grades) > 0:
                for lvl in ["Level I", "Level II", "Level III", "Level IV"]:
                    lvl_grades = s_grades[s_grades["Level"] == lvl]
                    if len(lvl_grades) > 0:
                        st.markdown(f"### **{lvl.upper()}**")
                        display_df = lvl_grades[["CourseCode", "CourseTitle", "CreditHours", "Score", "Grade", "GradePoints"]]
                        st.dataframe(display_df, use_container_width=True)
                        
                        total_cr = lvl_grades["CreditHours"].sum()
                        total_pts = lvl_grades["GradePoints"].sum()
                        gpa = total_pts / total_cr if total_cr > 0 else 0.0
                        st.markdown(f"**Total Credit Hours:** {total_cr} | **Total Grade Points:** {total_pts:.2f} | **GPA:** **{gpa:.2f}**")
                        st.markdown("---")
                
                tot_credits = s_grades["CreditHours"].sum()
                tot_points = s_grades["GradePoints"].sum()
                cgpa = tot_points / tot_credits if tot_credits > 0 else 0.0
                st.success(f"### Cumulative Grade Point Average (CGPA): **{cgpa:.2f}** / 4.00")
            else:
                st.info("No grades recorded for this student yet.")

# ==========================================
# 6. STUDENT SELF-SERVICE PORTAL
# ==========================================
elif menu == "My Student Profile":
    st.subheader("🎓 My Student Portal")
    df_students = pd.read_csv(STUDENTS_FILE)
    df_grades = pd.read_csv(GRADES_FILE)
    
    student = df_students[df_students["StudentID"] == st.session_state.username].iloc[0]
    s_grades = df_grades[df_grades["StudentID"] == st.session_state.username]
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if pd.notna(student["PhotoPath"]) and student["PhotoPath"] != "" and os.path.exists(student["PhotoPath"]):
            st.image(student["PhotoPath"], width=150, caption="Temporary ID Photo")
        else:
            st.info("No Temporary Photo Uploaded")
    with col2:
        st.markdown(f"### **{student['FullName']}**")
        st.write(f"**Student ID:** {student['StudentID']}")
        st.write(f"**Department:** {student['Department']}")
        st.write(f"**Campus:** {student['Campus']}")
        st.write(f"**Current Level:** {student['Level']}")
        st.write(f"**Enrollment Status:** {student['EnrollmentStatus']}")
        
    st.markdown("---")
    st.subheader("My Academic Grades")
    if len(s_grades) > 0:
        st.dataframe(s_grades[["Level", "Semester", "CourseCode", "CourseTitle", "CreditHours", "Score", "Grade"]], use_container_width=True)
        tot_cr = s_grades["CreditHours"].sum()
        tot_pts = s_grades["GradePoints"].sum()
        cgpa = tot_pts / tot_cr if tot_cr > 0 else 0.0
        st.metric("My Cumulative GPA", f"{cgpa:.2f} / 4.00")
    else:
        st.info("Your grade records are currently being updated by the registrar.")

elif menu == "My Grade Records & Transcript":
    st.subheader("📜 My Official Transcript Summary")
    df_grades = pd.read_csv(GRADES_FILE)
    s_grades = df_grades[df_grades["StudentID"] == st.session_state.username]
    if len(s_grades) > 0:
        st.dataframe(s_grades, use_container_width=True)
    else:
        st.info("No grades available yet.")

# --- DEVELOPER FOOTER ---
st.markdown("""
    <div class="developer-footer">
        <b>Hanek Technology and Business College Registrar System</b><br>
        Lead Developer: <b>Ebirawi Henok Loha</b> | Phone: <b>+251965514327</b> | Email: <b>henokebirawi3@gmail.com</b><br>
        Wolaita Sodo, Basketo, Boloso Bombe, Jinka Campuses © 2026
    </div>
""", unsafe_allow_html=True)
