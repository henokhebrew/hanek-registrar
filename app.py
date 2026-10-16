import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Hanek Technology and Business College",
    page_icon="🎓",
    layout="wide"
)

# --- FILE PATHS FOR LOCAL STORAGE ---
USERS_FILE = "hanek_users.csv"
STUDENTS_FILE = "hanek_students.csv"
GRADES_FILE = "hanek_grades.csv"

# Initialize default CSV databases if they don't exist
if not os.path.exists(USERS_FILE):
    df_users_init = pd.DataFrame([
        {"Username": "admin", "Password": "password123", "Role": "Registrar", "FullName": "System Administrator"},
        {"Username": "student1", "Password": "123", "Role": "Student", "FullName": "Tesfaye Silas Beyene"}
    ])
    df_users_init.to_csv(USERS_FILE, index=False)

if not os.path.exists(STUDENTS_FILE):
    df_init = pd.DataFrame(columns=[
        "StudentID", "FullName", "Gender", "Department", "Level", "Campus", "AcademicYear", "Status"
    ])
    df_init.to_csv(STUDENTS_FILE, index=False)

if not os.path.exists(GRADES_FILE):
    df_grades_init = pd.DataFrame(columns=[
        "StudentID", "FullName", "Department", "Level", "Semester", "CourseCode", "CourseTitle", "CreditHours", "Score", "Grade", "GradePoints"
    ])
    df_grades_init.to_csv(GRADES_FILE, index=False)

# --- HELPER FUNCTIONS ---
def calculate_grade_point(score):
    if score >= 90: return "A+", 4.0
    elif score >= 85: return "A", 4.0
    elif score >= 80: return "A-", 3.75
    elif score >= 75: return "B+", 3.25
    elif score >= 70: return "B", 3.0
    elif score >= 65: return "B-", 2.75
    elif score >= 60: return "C+", 2.5
    elif score >= 50: return "C", 2.0
    elif score >= 45: return "D", 1.75
    elif score >= 40: return "Fx", 1.0
    else: return "F", 0.0

# --- SESSION STATE INITIALIZATION FOR AUTHENTICATION ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "role" not in st.session_state:
    st.session_state["role"] = ""
if "fullname" not in st.session_state:
    st.session_state["fullname"] = ""

# --- LOGIN SCREEN ---
if not st.session_state["logged_in"]:
    st.title("🎓 Hanek Technology and Business College")
    st.subheader("Official Online Registrar & Student Information System")
    st.markdown("**Website:** [www.hanektechnologyandbusinesscollege.com](https://www.hanektechnologyandbusinesscollege.com)")
    st.markdown("---")
    
    st.markdown("### 🔐 Secure System Login")
    st.info("Default Login — Registrar: Username: `admin` | Password: `password123`  \n Student: Username: `student1` | Password: `123`")
    
    with st.form("login_form"):
        input_user = st.text_input("Username")
        input_pass = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Log In")
        
        if login_btn:
            df_users = pd.read_csv(USERS_FILE)
            user_match = df_users[(df_users["Username"] == input_user) & (df_users["Password"] == input_pass)]
            
            if not user_match.empty:
                st.session_state["logged_in"] = True
                st.session_state["username"] = user_match.iloc[0]["Username"]
                st.session_state["role"] = user_match.iloc[0]["Role"]
                st.session_state["fullname"] = user_match.iloc[0]["FullName"]
                st.success(f"Welcome back, {st.session_state['fullname']}!")
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again.")

# --- MAIN APP INTERFACE (AFTER SUCCESSFUL LOGIN) ---
else:
    # --- HEADER WITH BRANDING ---
    st.title("🎓 Hanek Technology and Business College")
    st.markdown("**Official Portal:** [www.hanektechnologyandbusinesscollege.com](https://www.hanektechnologyandbusinesscollege.com) | **Tel:** +251-46-180-3164")
    st.markdown(f"**Logged in as:** {st.session_state['fullname']} (*Role: {st.session_state['role']}*)")
    
    if st.sidebar.button("Log Out"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["role"] = ""
        st.session_state["fullname"] = ""
        st.rerun()

    st.markdown("---")

    # ================= REGISTRAR / ADMIN MODULES =================
    if st.session_state["role"] == "Registrar":
        menu = st.sidebar.selectbox("Registrar Navigation", [
            "Dashboard",
            "Student Admission & Enrollment",
            "Grade Entry & Management",
            "Official Transcript Generator",
            "Database Backup & Export"
        ])

        if menu == "Dashboard":
            st.header("Admin Dashboard")
            st.info("Multi-Campus System: Wolaita Sodo | Basketo | Boloso | Jinka")
            
            df_stu = pd.read_csv(STUDENTS_FILE)
            df_grd = pd.read_csv(GRADES_FILE)
            
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Total Enrolled Students", len(df_stu))
            with col2: st.metric("Active TVET Departments", 6)
            with col3: st.metric("Total Grade Records", len(df_grd))
                
            st.markdown("### 🏢 Available TVET Programs (Levels I - IV)")
            for dept in [
                "Cooperative Accounting and Auditing",
                "Cooperative Business Management",
                "Cooperative Marketing",
                "Hardware and Network System (HNS)",
                "Natural Resource Management (NARM)",
                "Crop Production (Plant Science)"
            ]:
                st.write(f"- {dept}")

        elif menu == "Student Admission & Enrollment":
            st.header("📝 Student Admission & Registration Portal")
            with st.form("admission_form"):
                col1, col2 = st.columns(2)
                with col1:
                    student_id = st.text_input("Student ID (e.g., CBM-0144-16)")
                    full_name = st.text_input("Full Name")
                    gender = st.selectbox("Gender", ["Male", "Female"])
                    campus = st.selectbox("Campus Location", ["Wolaita Sodo", "Basketo", "Boloso", "Jinka"])
                with col2:
                    department = st.selectbox("Department", [
                        "Cooperative Accounting and Auditing",
                        "Cooperative Business Management",
                        "Cooperative Marketing",
                        "Hardware and Network System (HNS)",
                        "Natural Resource Management (NARM)",
                        "Crop Production (Plant Science)"
                    ])
                    level = st.selectbox("TVET Level", ["Level I", "Level II", "Level III", "Level IV"])
                    academic_year = st.text_input("Academic Year", value="2026/2027")
                    status = st.selectbox("Enrollment Status", ["Active", "Completed", "Suspended", "Withdrawn"])
                    
                if st.form_submit_button("Register Student"):
                    if student_id and full_name:
                        df_stu = pd.read_csv(STUDENTS_FILE)
                        if student_id in df_stu["StudentID"].values:
                            st.error("A student with this ID already exists!")
                        else:
                            new_data = pd.DataFrame([{
                                "StudentID": student_id, "FullName": full_name, "Gender": gender,
                                "Department": department, "Level": level, "Campus": campus,
                                "AcademicYear": academic_year, "Status": status
                            }])
                            df_stu = pd.concat([df_stu, new_data], ignore_index=True)
                            df_stu.to_csv(STUDENTS_FILE, index=False)
                            st.success(f"Successfully registered {full_name}!")
                    else:
                        st.warning("Please fill in Student ID and Full Name.")

            st.markdown("### Registered Students Directory")
            st.dataframe(pd.read_csv(STUDENTS_FILE), use_container_width=True)

        elif menu == "Grade Entry & Management":
            st.header("📊 Student Grade Entry & Assessment")
            df_stu = pd.read_csv(STUDENTS_FILE)
            if df_stu.empty:
                st.warning("No students registered yet.")
            else:
                selected_id = st.selectbox("Select Student ID", df_stu["StudentID"].tolist())
                student_info = df_stu[df_stu["StudentID"] == selected_id].iloc[0]
                st.info(f"**Name:** {student_info['FullName']} | **Dept:** {student_info['Department']} | **Level:** {student_info['Level']}")
                
                with st.form("grade_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        semester = st.selectbox("Semester", ["Semester I", "Semester II"])
                        course_code = st.text_input("Module Code & Unit of Competence (e.g., CAB ACC1 0710)")
                        course_title = st.text_input("Course Title")
                    with col2:
                        credit_hours = st.number_input("Credit Hours (Hr)", min_value=1, max_value=10, value=3)
                        score = st.number_input("Assessment Score (0 - 100)", min_value=0.0, max_value=100.0, value=85.0)
                        
                    if st.form_submit_button("Save Grade"):
                        grade_letter, grade_point_val = calculate_grade_point(score)
                        total_gp = grade_point_val * credit_hours
                        
                        df_grd = pd.read_csv(GRADES_FILE)
                        new_grade = pd.DataFrame([{
                            "StudentID": selected_id, "FullName": student_info["FullName"],
                            "Department": student_info["Department"], "Level": student_info["Level"],
                            "Semester": semester, "CourseCode": course_code, "CourseTitle": course_title,
                            "CreditHours": credit_hours, "Score": score, "Grade": grade_letter, "GradePoints": total_gp
                        }])
                        df_grd = pd.concat([df_grd, new_grade], ignore_index=True)
                        df_grd.to_csv(GRADES_FILE, index=False)
                        st.success(f"Grade recorded! Score: {score} -> Grade: {grade_letter}")

                st.markdown("### Existing Grade Records")
                df_grd = pd.read_csv(GRADES_FILE)
                st.dataframe(df_grd[df_grd["StudentID"] == selected_id], use_container_width=True)

        elif menu == "Official Transcript Generator":
            st.header("📜 Official Academic Transcript Generator")
            df_stu = pd.read_csv(STUDENTS_FILE)
            if df_stu.empty:
                st.warning("No students available.")
            else:
                selected_id = st.selectbox("Select Student ID", df_stu["StudentID"].tolist())
                student = df_stu[df_stu["StudentID"] == selected_id].iloc[0]
                
                if st.button("Generate Official Transcript"):
                    st.markdown("---")
                    st.markdown("<h2 style='text-align: center;'>HANEK TECHNOLOGY AND BUSINESS COLLEGE</h2>", unsafe_allow_html=True)
                    st.markdown("<p style='text-align: center;'>Wolaita Sodo Campus | Website: www.hanektechnologyandbusinesscollege.com</p>", unsafe_allow_html=True)
                    st.markdown(f"<h4 style='text-align: center;'>DEPARTMENT OF {student['Department'].upper()}</h4>", unsafe_allow_html=True)
                    st.markdown("<h5 style='text-align: center;'>OFFICIAL ACADEMIC TRANSCRIPT (STUDENT COPY)</h5>", unsafe_allow_html=True)
                    
                    st.write(f"**Student ID:** {student['StudentID']} | **Name:** {student['FullName']}")
                    st.write(f"**Gender:** {student['Gender']} | **Campus:** {student['Campus']} | **Level:** {student['Level']}")
                    st.markdown("---")
                    
                    df_grd = pd.read_csv(GRADES_FILE)
                    st_grades = df_grd[df_grd["StudentID"] == selected_id]
                    
                    if st_grades.empty:
                        st.info("No grades found for this student.")
                    else:
                        st.dataframe(st_grades[["CourseCode", "CourseTitle", "CreditHours", "Score", "Grade"]], use_container_width=True)
                        total_credits = st_grades["CreditHours"].sum()
                        total_gp = st_grades["GradePoints"].sum()
                        cgpa = total_gp / total_credits if total_credits > 0 else 0.0
                        
                        col1, col2 = st.columns(2)
                        with col1: st.metric("Total Credit Hours", total_credits)
                        with col2: st.metric("Cumulative GPA (CGPA)", round(cgpa, 2))
                            
                    st.markdown("---")
                    st.markdown("Registrar Office Signature: ______________________     Dean: ______________________")

        elif menu == "Database Backup & Export":
            st.header("💾 Database Backup & CSV Export")
            if st.button("Export Students CSV"):
                pd.read_csv(STUDENTS_FILE).to_csv("exported_students.csv", index=False)
                st.success("Saved as exported_students.csv")
            if st.button("Export Grades CSV"):
                pd.read_csv(GRADES_FILE).to_csv("exported_grades.csv", index=False)
                st.success("Saved as exported_grades.csv")

    # ================= STUDENT PORTAL MODULE =================
    elif st.session_state["role"] == "Student":
        st.header("student Portal - My Academic Record")
        st.info("Welcome to your student dashboard. You can view your enrolled courses, grades, and academic standing.")
        
        # For demonstration, linking student1 to a sample ID
        target_student_id = "CBM-0144-16"
        
        df_stu = pd.read_csv(STUDENTS_FILE)
        student_record = df_stu[df_stu["StudentID"] == target_student_id]
        
        if student_record.empty:
            st.warning(f"Profile record for ID {target_student_id} is currently being updated by the registrar office.")
        else:
            stu = student_record.iloc[0]
            st.markdown(f"### Profile Summary: {stu['FullName']}")
            st.write(f"**Student ID:** {stu['StudentID']} | **Department:** {stu['Department']}")
            st.write(f"**Campus:** {stu['Campus']} | **TVET Level:** {stu['Level']} | **Status:** {stu['Status']}")
            
            st.markdown("### 📊 My Course Grades & Transcript")
            df_grd = pd.read_csv(GRADES_FILE)
            my_grades = df_grd[df_grd["StudentID"] == target_student_id]
            
            if my_grades.empty:
                st.info("No grade assessments posted for your account yet.")
            else:
                st.dataframe(my_grades[["CourseCode", "CourseTitle", "CreditHours", "Score", "Grade"]], use_container_width=True)
                total_credits = my_grades["CreditHours"].sum()
                total_gp = my_grades["GradePoints"].sum()
                cgpa = total_gp / total_credits if total_credits > 0 else 0.0
                
                col1, col2 = st.columns(2)
                with col1: st.metric("Total Earned Credit Hours", total_credits)
                with col2: st.metric("Cumulative GPA (CGPA)", round(cgpa, 2))