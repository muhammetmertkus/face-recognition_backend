from dataclasses import dataclass, field
from typing import List, Optional
import datetime

# Re-use or import the default_datetime function if needed
# from .user import default_datetime
def default_datetime(): # Define it here if not importing
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

@dataclass
class LessonTime:
    id: int
    course_id: int
    lesson_number: int
    day: str # e.g., "MONDAY"
    start_time: str # HH:MM
    end_time: str   # HH:MM
    created_at: str = field(default_factory=default_datetime)
    updated_at: str = field(default_factory=default_datetime)

@dataclass
class Course:
    id: int
    code: str
    name: str
    teacher_id: int
    semester: str
    created_at: str = field(default_factory=default_datetime)
    updated_at: str = field(default_factory=default_datetime)
    # lesson_times: List[LessonTime] = field(default_factory=list) # Or load separately
    # teacher: Optional[Teacher] = None # Or load separately

@dataclass
class StudentCourse:
    # No unique ID needed here, the combination is the key
    student_id: int
    course_id: int
    # Optional: Add registration date if needed
    # registered_at: str = field(default_factory=default_datetime) 