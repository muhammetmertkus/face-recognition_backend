from pydantic import BaseModel, Field, validator
from typing import List, Optional
import datetime
import re # For time validation

# Re-use UserResponse and TeacherResponse if needed by importing
from .user import UserResponse, TeacherResponse, StudentResponse # Assuming user schemas are defined

VALID_DAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]

class LessonTimeBase(BaseModel):
    lesson_number: int = Field(..., gt=0)
    day: str
    start_time: str # HH:MM format
    end_time: str   # HH:MM

    @validator('day')
    def day_must_be_valid(cls, v):
        if v.upper() not in VALID_DAYS:
            raise ValueError(f'Day must be one of {VALID_DAYS}')
        return v.upper()

    @validator('start_time', 'end_time')
    def time_format_must_be_valid(cls, v):
        if not re.match(r"^[0-2][0-9]:[0-5][0-9]$", v):
            raise ValueError('Time must be in HH:MM format')
        # Optional: Add check HH < 24
        return v

    # Optional: Add validator to ensure end_time > start_time

class LessonTimeCreate(LessonTimeBase):
    pass

class LessonTimeResponse(LessonTimeBase):
    id: int
    course_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    code: str = Field(..., min_length=3)
    name: str = Field(..., min_length=3)
    semester: str

class CourseCreate(CourseBase):
    teacher_id: Optional[int] = None # Make teacher_id optional in schema
    lesson_times: List[LessonTimeCreate] = [] # Allow creating lesson times with the course

class CourseUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=3)
    name: Optional[str] = Field(None, min_length=3)
    semester: Optional[str] = None
    # Potentially allow updating teacher_id or lesson_times (more complex)
    lesson_times: Optional[List[LessonTimeCreate]] = None # Allow replacing lesson times

class CourseResponse(CourseBase):
    id: int
    teacher_id: int
    teacher: Optional[TeacherResponse] = None # Embed teacher details
    lesson_times: List[LessonTimeResponse] = [] # Embed lesson time details
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

# Schema for associating a student with a course
class StudentCourseLink(BaseModel):
    student_id: int

class StudentCourseResponse(BaseModel):
    student_id: int
    course_id: int
    # Add student and course details if needed for specific endpoints
    student: Optional[StudentResponse] = None
    course: Optional[CourseResponse] = None

    class Config:
        from_attributes = True 