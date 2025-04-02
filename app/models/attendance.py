from dataclasses import dataclass, field
from typing import Optional, Dict, List
import datetime

# Re-use or import the default_datetime function
def default_datetime():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

@dataclass
class AttendanceDetail:
    id: int
    attendance_id: int
    student_id: int
    status: str # "PRESENT", "ABSENT", "LATE", "EXCUSED"
    confidence: Optional[float] = None
    emotion: Optional[str] = None
    emotion_confidence: Optional[float] = None
    emotion_statistics: Optional[Dict[str, float]] = None
    created_at: str = field(default_factory=default_datetime)

@dataclass
class Attendance:
    # Non-default fields first
    id: int
    course_id: int
    date: str # ISO format date (YYYY-MM-DD) or datetime string
    lesson_number: int
    type: str # "FACE", "EMOTION", "FACE_EMOTION", "MANUAL"
    created_by: int # User ID (Teacher)
    
    # Default fields last
    photo_path: Optional[str] = None
    total_students: Optional[int] = None # Number of students registered for the course at this time
    recognized_students: Optional[int] = None
    unrecognized_students: Optional[int] = None
    emotion_statistics: Optional[Dict[str, int]] = None # Overall stats for the session
    created_at: str = field(default_factory=default_datetime)
    # details: List[AttendanceDetail] = field(default_factory=list) # Or load separately

@dataclass
class EmotionHistory:
    id: int
    student_id: int
    course_id: int
    emotion: str
    confidence: float
    timestamp: str # ISO format datetime string
    # Might link to attendance_id or attendance_detail_id if needed
    # attendance_detail_id: Optional[int] = None 