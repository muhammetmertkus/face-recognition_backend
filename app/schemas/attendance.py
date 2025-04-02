from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import datetime

# Re-use UserResponse, StudentResponse etc. if needed by importing
from .user import StudentResponse # Assuming user schemas are defined
from .course import CourseResponse # Assuming course schemas are defined

VALID_ATTENDANCE_STATUS = ["PRESENT", "ABSENT", "LATE", "EXCUSED"]
VALID_ATTENDANCE_TYPES = ["FACE", "EMOTION", "FACE_EMOTION", "MANUAL"]

class AttendanceDetailBase(BaseModel):
    student_id: int
    status: str
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    emotion: Optional[str] = None
    emotion_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    emotion_statistics: Optional[Dict[str, float]] = None
    estimated_age: Optional[int] = None
    estimated_gender: Optional[str] = None

    @validator('status')
    def status_must_be_valid(cls, v):
        if v.upper() not in VALID_ATTENDANCE_STATUS:
            raise ValueError(f'Status must be one of {VALID_ATTENDANCE_STATUS}')
        return v.upper()

class AttendanceDetailCreate(AttendanceDetailBase):
    # Used internally when creating attendance record
    pass

class AttendanceDetailResponse(AttendanceDetailBase):
    id: int
    attendance_id: int
    student: Optional[StudentResponse] = None # Optionally embed student details
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class AttendanceBase(BaseModel):
    course_id: int
    date: datetime.date # Use date type for validation
    lesson_number: int = Field(..., gt=0)
    type: str
    photo_path: Optional[str] = None

    @validator('type')
    def type_must_be_valid(cls, v):
        if v.upper() not in VALID_ATTENDANCE_TYPES:
            raise ValueError(f'Type must be one of {VALID_ATTENDANCE_TYPES}')
        return v.upper()

class AttendanceCreate(BaseModel):
    # Schema for the POST /api/attendance endpoint request (form data)
    course_id: int
    lesson_number: int
    date: datetime.date
    type: str = Field(..., description=f"Must be one of {VALID_ATTENDANCE_TYPES}")
    # file: UploadFile = File(...) # Handled separately in Flask route

class AttendanceManualUpdate(BaseModel):
    # Schema for POST /api/attendance/{id}/students/{sid}
    status: str

    @validator('status')
    def status_must_be_valid(cls, v):
        if v.upper() not in VALID_ATTENDANCE_STATUS:
            raise ValueError(f'Status must be one of {VALID_ATTENDANCE_STATUS}')
        return v.upper()

class AttendanceResponse(AttendanceBase):
    id: int
    total_students: Optional[int] = None
    recognized_students: Optional[int] = None
    unrecognized_students: Optional[int] = None
    emotion_statistics: Optional[Dict[str, int]] = None
    created_by: int # User ID (Teacher)
    created_at: datetime.datetime
    details: List[AttendanceDetailResponse] = [] # Embed details
    course: Optional[CourseResponse] = None # Optionally embed course details

    class Config:
        from_attributes = True

# Öğrenci bilgisi modeli
class StudentInfo(BaseModel):
    id: int 
    student_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None

class AttendanceResultDetail(BaseModel):
    student_id: int
    status: str
    confidence: Optional[float] = None
    emotion: Optional[str] = None
    estimated_age: Optional[int] = None
    estimated_gender: Optional[str] = None
    student: Optional[StudentInfo] = None  # Öğrenci detaylarını ekledik

class AttendanceResultSummary(BaseModel):
    # Updated response after POST /api/attendance
    attendance_id: int
    recognized_count: int
    unrecognized_count: int
    total_students: int  # Toplam öğrenci sayısı eklendi
    emotion_statistics: Optional[Dict[str, int]] = None # Added field for overall stats
    results: List[AttendanceResultDetail] # Use the specific model here

# --- Emotion History Schemas ---

class EmotionHistoryBase(BaseModel):
    student_id: int
    course_id: int
    emotion: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime.datetime

class EmotionHistoryCreate(EmotionHistoryBase):
    # Used internally
    pass

class EmotionHistoryResponse(EmotionHistoryBase):
    id: int

    class Config:
        from_attributes = True

# --- Reporting Schemas ---

class DailyAttendanceReportItem(BaseModel):
    course_id: int
    course_code: str
    course_name: str
    present_count: int
    absent_count: int
    # Add more fields as needed (late, excused, etc.)

class DailyAttendanceReportResponse(BaseModel):
    date: datetime.date
    reports: List[DailyAttendanceReportItem]

class CourseEmotionReportResponse(BaseModel):
    course_id: int
    course_code: str
    course_name: str
    overall_emotion_stats: Dict[str, int]
    timeline: List[Dict[str, Any]] # List of {"date": ..., "emotion_stats": {...}}

class StudentAttendanceCourseReport(BaseModel):
    course_id: int
    course_code: str
    rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    details: List[AttendanceDetailResponse] # List all attendance details for this course

class StudentAttendanceReportResponse(BaseModel):
    student_info: StudentResponse
    overall_attendance_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    course_reports: List[StudentAttendanceCourseReport] 