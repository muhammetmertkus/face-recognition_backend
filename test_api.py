import requests
import json
import datetime
import os

# --- Test Configuration ---
BASE_URL = "http://127.0.0.1:5000/api" # Your Flask app's base URL
TEST_LOG_FILE = "test_log.md"
FACE_IMAGE_PATH = "erkek.jpg" # Path to your test face image

# Store tokens and IDs for subsequent requests
admin_token = None
teacher_token = None
student_token = None
teacher_id = None
student_id = None
student_user_id = None
course_id = None
attendance_id = None

# Test data (use unique values to avoid conflicts on re-runs if possible)
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
admin_email = f"admin_{timestamp}@test.com"
teacher_email = f"teacher_{timestamp}@test.com"
student_email = f"student_{timestamp}@test.com"
student_number = f"S{timestamp}"
course_code = f"TEST{timestamp}"

def log_test_result(endpoint, method, payload, response, status_code, log_file):
    """Logs the test result to console and a Markdown file."""
    success = 200 <= status_code < 300
    status_icon = "✅" if success else "❌"
    print(f"{status_icon} {method} {endpoint} - Status: {status_code}")
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"## {status_icon} {method} {endpoint}\n\n")
        f.write(f"**Timestamp:** {datetime.datetime.now()}\n")
        f.write(f"**Status Code:** `{status_code}`\n\n")
        
        if payload:
            f.write(f"**Request Payload:**\n```json\n{json.dumps(payload, indent=2)}\n```\n\n")
        else:
             f.write(f"**Request Payload:** None\n\n")
             
        f.write(f"**Response Body:**\n")
        try:
            response_json = response.json()
            f.write(f"```json\n{json.dumps(response_json, indent=2)}\n```\n\n")
            if not success:
                 print(f"  Error: {json.dumps(response_json)}")
        except json.JSONDecodeError:
            # Handle non-JSON responses (like HTML error pages)
            response_text = response.text
            f.write(f"```html\n{response_text[:1000]}...\n```\n\n") # Log first 1000 chars
            if not success:
                 print(f"  Error: Received non-JSON response (Status: {status_code}) - Check log file for details.")
                 
        f.write("---\n\n")
        
    return response.json() if success and response.content else None

def run_test(method, endpoint, token=None, data=None, json_payload=None, files=None, log_file=TEST_LOG_FILE):
    """Runs a single API test."""
    headers = {"accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if json_payload and not files: # Don't set Content-Type for multipart/form-data
        headers["Content-Type"] = "application/json"
        
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
             if files:
                 # Send data as form data, not JSON
                 response = requests.post(url, headers=headers, data=data, files=files)
             else:
                 response = requests.post(url, headers=headers, json=json_payload)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=json_payload)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            print(f"❌ Unsupported method: {method}")
            return None
            
        return log_test_result(endpoint, method, json_payload or data, response, response.status_code, log_file)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed for {method} {endpoint}: {e}")
        with open(log_file, "a", encoding="utf-8") as f:
             f.write(f"## ❌ {method} {endpoint}\n\n")
             f.write(f"**Timestamp:** {datetime.datetime.now()}\n")
             f.write(f"**Status:** Request Failed\n")
             f.write(f"**Error:** `{e}`\n\n---\n\n")
        return None

# --- Main Test Execution --- 
def main():
    global admin_token, teacher_token, student_token, teacher_id, student_id, student_user_id, course_id, attendance_id
    
    # Clear log file at the start
    if os.path.exists(TEST_LOG_FILE):
        os.remove(TEST_LOG_FILE)
    with open(TEST_LOG_FILE, "w", encoding="utf-8") as f:
        f.write("# API Test Log\n\n")
        
    print("Starting API tests...")
    print(f"Log file: {TEST_LOG_FILE}")
    print(f"Using face image: {FACE_IMAGE_PATH}\n")

    if not os.path.exists(FACE_IMAGE_PATH):
         print(f"❌ ERROR: Face image not found at {FACE_IMAGE_PATH}. Please add the image.")
         return

    # === 1. Auth Endpoints ===
    print("--- Testing Auth ---")
    # Register Admin (assuming first user is Admin or adjust role)
    admin_payload = {"email": admin_email, "password": "adminpass", "first_name": "Admin", "last_name": "User", "role": "ADMIN"}
    run_test("POST", "/auth/register", json_payload=admin_payload)
    
    # Register Teacher
    teacher_payload = {"email": teacher_email, "password": "teacherpass", "first_name": "Test", "last_name": "Teacher", "role": "TEACHER", "department": "CompSci", "title": "Professor"}
    teacher_reg_res = run_test("POST", "/auth/register", json_payload=teacher_payload)
    # teacher_user_id = teacher_reg_res.get('id') if teacher_reg_res else None
    
    # Register Student
    student_payload = {"email": student_email, "password": "studentpass", "first_name": "Test", "last_name": "Student", "role": "STUDENT", "department": "CompEng", "student_number": student_number}
    student_reg_res = run_test("POST", "/auth/register", json_payload=student_payload)
    student_user_id = student_reg_res.get('id') if student_reg_res else None
    
    # Login Admin
    admin_login_payload = {"email": admin_email, "password": "adminpass"}
    admin_login_res = run_test("POST", "/auth/login", json_payload=admin_login_payload)
    if admin_login_res:
        admin_token = admin_login_res.get('access_token')
        
    # Login Teacher
    teacher_login_payload = {"email": teacher_email, "password": "teacherpass"}
    teacher_login_res = run_test("POST", "/auth/login", json_payload=teacher_login_payload)
    if teacher_login_res:
        teacher_token = teacher_login_res.get('access_token')
        # We need the Teacher ID (not just User ID) for creating courses etc.
        # We fetch it via the /teachers endpoint later or assume it based on registration order if needed early

    # Login Student
    student_login_payload = {"email": student_email, "password": "studentpass"}
    student_login_res = run_test("POST", "/auth/login", json_payload=student_login_payload)
    if student_login_res:
        student_token = student_login_res.get('access_token')
        
    # Get Me (Admin)
    run_test("GET", "/auth/me", token=admin_token)
    # Update Me (Student)
    update_payload = {"last_name": "StudentUpdated"}
    run_test("PUT", "/auth/me", token=student_token, json_payload=update_payload)

    # === 2. Teacher Endpoints ===
    print("\n--- Testing Teachers ---")
    # Get all teachers (as Admin)
    teachers_list = run_test("GET", "/teachers/", token=admin_token)
    if teachers_list and isinstance(teachers_list, list) and len(teachers_list) > 0:
         # Find the teacher we created by email or assume the first relevant one
         created_teacher_info = next((t for t in teachers_list if t.get('user', {}).get('email') == teacher_email), teachers_list[0])
         teacher_id = created_teacher_info.get('id')
         print(f"  (Using Teacher ID: {teacher_id} for further tests)")
    else:
         print("❌ Could not retrieve teacher list or teacher ID. Skipping some tests.")

    if teacher_id:
        # Get specific teacher (as Teacher)
        run_test("GET", f"/teachers/{teacher_id}", token=teacher_token)
        # Update teacher (as Admin)
        teacher_update_payload = {"title": "Associate Professor"}
        run_test("PUT", f"/teachers/{teacher_id}", token=admin_token, json_payload=teacher_update_payload)
        # Get teacher courses (as Teacher) - should be empty initially
        run_test("GET", f"/teachers/{teacher_id}/courses", token=teacher_token)

    # === 3. Student Endpoints ===
    print("\n--- Testing Students ---")
    # Get all students (as Teacher)
    students_list = run_test("GET", "/students/", token=teacher_token)
    if students_list and isinstance(students_list, list) and len(students_list) > 0:
         # Find the student we created by student number
         created_student_info = next((s for s in students_list if s.get('student_number') == student_number), None)
         if created_student_info:
            student_id = created_student_info.get('id')
            print(f"  (Using Student ID: {student_id} for further tests)")
         else:
             print(f"❌ Could not find created student S{timestamp} in list.")
             # Fallback if needed: find by user_id
             if student_user_id:
                 created_student_info = next((s for s in students_list if s.get('user_id') == student_user_id), students_list[0])
                 student_id = created_student_info.get('id')
                 print(f"  (Fallback: Using Student ID: {student_id} for further tests)")
             
    if not student_id:
        print("❌ Could not retrieve student ID. Skipping some tests.")
        
    if student_id:
        # Get specific student (as Student)
        run_test("GET", f"/students/{student_id}", token=student_token)
        # Update student (as Admin) - Requires Admin Token
        if admin_token:
            student_update_payload = {"department": "Computer Science & Eng."}
            run_test("PUT", f"/students/{student_id}", token=admin_token, json_payload=student_update_payload)
        else:
             print("  Skipping Student PUT test (Admin): Admin token not available.")
        
        # Upload face (as Student)
        print(f"  Uploading face for student {student_id}...")
        with open(FACE_IMAGE_PATH, "rb") as f:
             files = {'file': (FACE_IMAGE_PATH, f, 'image/jpeg')} # Adjust content type if needed
             # No json_payload when sending files with requests library like this
             run_test("POST", f"/students/{student_id}/face", token=student_token, files=files)
             
        # Get student courses (as Student) - should be empty
        run_test("GET", f"/students/{student_id}/courses", token=student_token)

    # === 4. Course Endpoints ===
    print("\n--- Testing Courses ---")
    if not teacher_id or not student_id:
         print("❌ Missing Teacher ID or Student ID. Skipping Course tests.")
    else:
        # Create course (as Teacher)
        course_payload = {
             "code": course_code,
             "name": "API Test Course",
             "semester": "2025-Test",
             # teacher_id is determined by logged-in teacher token
             "lesson_times": [
                 {"day": "TUESDAY", "start_time": "10:00", "end_time": "11:50", "lesson_number": 1},
                 {"day": "THURSDAY", "start_time": "14:00", "end_time": "15:50", "lesson_number": 2}
             ]
         }
        course_create_res = run_test("POST", "/courses/", token=teacher_token, json_payload=course_payload)
        if course_create_res:
            course_id = course_create_res.get('id')
            print(f"  (Using Course ID: {course_id} for further tests)")
        else:
             print("❌ Failed to create course. Skipping dependent tests.")

    if course_id:
        # Get all courses (as Student)
        run_test("GET", "/courses/", token=student_token)
        # Get specific course (as Student)
        run_test("GET", f"/courses/{course_id}", token=student_token)
        # Update course (as Teacher) - e.g., change semester
        course_update_payload = {"semester": "2025-Test-Updated"}
        run_test("PUT", f"/courses/{course_id}", token=teacher_token, json_payload=course_update_payload)
        
        # Enroll student in course (as Teacher)
        enroll_payload = {"student_id": student_id}
        run_test("POST", f"/courses/{course_id}/students", token=teacher_token, json_payload=enroll_payload)
        # Get enrolled students (as Teacher) - should show the student
        run_test("GET", f"/courses/{course_id}/students", token=teacher_token)
        # Get student courses (as Student) - should now show the course
        run_test("GET", f"/students/{student_id}/courses", token=student_token)
         # Get course attendance (as Teacher) - should be empty
        run_test("GET", f"/courses/{course_id}/attendance", token=teacher_token)
        # --- New Test: Remove student from course ---
        if student_id:
            print(f"  Attempting to remove student {student_id} from course {course_id}...")
            run_test("DELETE", f"/courses/{course_id}/students/{student_id}", token=teacher_token)
            # Optional Verification: Get enrolled students again, should be empty or student missing
            # run_test("GET", f"/courses/{course_id}/students", token=teacher_token)
        # --- End Remove Student Test ---

    # === 5. Attendance Endpoints === 
    # Re-enroll student for attendance tests if removed above
    if course_id and student_id:
        print(f"  Re-enrolling student {student_id} in course {course_id} for attendance tests...")
        enroll_payload = {"student_id": student_id}
        run_test("POST", f"/courses/{course_id}/students", token=teacher_token, json_payload=enroll_payload)

    print("\n--- Testing Attendance ---")
    if not course_id or not student_id or not teacher_token:
         print("❌ Missing Course ID, Student ID, or Teacher Token. Skipping Attendance tests.")
    else:
        # Create attendance record (as Teacher)
        print(f"  Taking attendance for course {course_id} using {FACE_IMAGE_PATH}...")
        attendance_form_data = {
            'course_id': course_id,
            'lesson_number': 1,
            'date': datetime.date.today().isoformat(),
            'type': 'FACE'
        }
        with open(FACE_IMAGE_PATH, "rb") as f:
             files = {'file': (FACE_IMAGE_PATH, f, 'image/jpeg')} 
             # Use data= for form fields, files= for the file part
             attendance_res = run_test("POST", "/attendance/", token=teacher_token, data=attendance_form_data, files=files)
             if attendance_res:
                 attendance_id = attendance_res.get('attendance_id')
                 print(f"  (Using Attendance ID: {attendance_id} for further tests)")
             else:
                 print("❌ Failed to create attendance record.")
                 
    if attendance_id:
        # Get attendance record details (as Teacher)
        attendance_details_res = run_test("GET", f"/attendance/{attendance_id}", token=teacher_token)
        # Get attendance for course (alternative endpoint)
        run_test("GET", f"/attendance/course/{course_id}", token=teacher_token)
        # Get student attendance for course
        run_test("GET", f"/attendance/course/{course_id}/student/{student_id}", token=teacher_token)

        # --- Find absent student using API calls for manual update test ---
        absent_student_id = None
        if attendance_details_res and 'details' in attendance_details_res and course_id:
            # Get IDs of students marked as PRESENT
            present_student_ids = {detail['student_id'] for detail in attendance_details_res['details'] if detail.get('status') == 'PRESENT'}
            
            # Get IDs of all enrolled students via API
            enrolled_students_res = run_test("GET", f"/courses/{course_id}/students", token=teacher_token)
            if enrolled_students_res and isinstance(enrolled_students_res, list):
                enrolled_student_ids = {student['id'] for student in enrolled_students_res}
                
                # Find a student who is enrolled but not marked as PRESENT
                absent_ids = enrolled_student_ids - present_student_ids
                if absent_ids:
                    absent_student_id = list(absent_ids)[0] # Pick the first one
                    print(f"  (Found presumably absent student {absent_student_id} via API to test manual update)")
            else:
                 print("  Warning: Could not retrieve enrolled students list via API to find an absent student.")
        else:
             print("  Warning: Could not retrieve attendance details via API to find an absent student.")
        # --- End finding absent student ---

        # Manually update status
        if absent_student_id:       
            manual_payload = {"status": "PRESENT"}
            print(f"  Attempting to manually mark student {absent_student_id} as PRESENT for attendance {attendance_id}")
            run_test("POST", f"/attendance/{attendance_id}/students/{absent_student_id}", token=teacher_token, json_payload=manual_payload)
        else:
             # Test marking the recognized student (originally PRESENT) as EXCUSED
             manual_payload = {"status": "EXCUSED"}
             print(f"  Attempting to manually mark student {student_id} (originally present) as EXCUSED for attendance {attendance_id}")
             run_test("POST", f"/attendance/{attendance_id}/students/{student_id}", token=teacher_token, json_payload=manual_payload)

    # === 6. Report Endpoints ===
    print("\n--- Testing Reports ---")
    if not course_id or not student_id or not teacher_token:
         print("❌ Missing Course/Student ID or Teacher Token. Skipping Report tests.")
    else:
        # Get daily report (as Teacher)
        run_test("GET", "/reports/attendance/daily", token=teacher_token)
        # Get daily report for specific course
        run_test("GET", f"/reports/attendance/daily?course_id={course_id}", token=teacher_token)
        # Get student attendance report (as Teacher)
        run_test("GET", f"/reports/attendance/student/{student_id}", token=teacher_token)
        # Get student attendance report for specific course
        run_test("GET", f"/reports/attendance/student/{student_id}?course_id={course_id}", token=teacher_token)
        # Get course emotion report (will likely be empty/not implemented)
        run_test("GET", f"/reports/emotions/course/{course_id}", token=teacher_token)
        
    # === 7. Cleanup (Optional but Recommended) ===
    print("\n--- Testing Cleanup ---")
    # --- Delete Course (Teacher or Admin) --- 
    # Note: This should cascade delete related data (enrollments, attendance) if implemented correctly
    if course_id and teacher_token:
         print(f"  Attempting to delete course {course_id} (as Teacher)...")
         run_test("DELETE", f"/courses/{course_id}", token=teacher_token)
         # Verify deletion (optional)
         # run_test("GET", f"/courses/{course_id}", token=teacher_token) # Expect 404
    else:
         print("  Skipping Course DELETE test: Course ID or Teacher token missing.")

    # --- Delete Teacher (Admin Only) --- 
    if teacher_id and admin_token:
         print(f"  Attempting to delete teacher {teacher_id} (as Admin)...")
         run_test("DELETE", f"/teachers/{teacher_id}", token=admin_token)
         # Verify deletion (optional)
         # run_test("GET", f"/teachers/{teacher_id}", token=admin_token) # Expect 404
    else:
         print("  Skipping Teacher DELETE test: Teacher ID or Admin token missing.")
         
    # --- Delete Student (Admin Only) --- 
    if student_id and admin_token:
         print(f"  Attempting to delete student {student_id} (as Admin)...")
         run_test("DELETE", f"/students/{student_id}", token=admin_token)
         # Verify deletion (optional)
         # run_test("GET", f"/students/{student_id}", token=admin_token) # Expect 404
    else:
         print("  Skipping Student DELETE test: Student ID or Admin token missing.")

    print("\nAPI tests completed.")

if __name__ == "__main__":
    # This import is needed here if test_api.py is in the root
    # and needs to access data_service functions indirectly during tests
    # (e.g., finding absent student). We assume the Flask app context is not available here.
    # For a standalone script, direct JSON reading might be needed for setup/verification.
    # Let's try running without app context for simplicity, relying on API calls.
    # from app.services import data_service 
    main() 