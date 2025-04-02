from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
import datetime

# Define roles as literals for validation
VALID_ROLES = ["ADMIN", "TEACHER", "STUDENT"]

class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6) # Add password validation
    role: Optional[str] = "STUDENT" # Default role, can be overridden
    department: Optional[str] = None # For teacher/student specific creation
    title: Optional[str] = None      # For teacher specific creation
    student_number: Optional[str] = None # For student specific creation

    @validator('role')
    def role_must_be_valid(cls, v):
        if v.upper() not in VALID_ROLES:
            raise ValueError(f'Role must be one of {VALID_ROLES}')
        return v.upper()

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1)
    last_name: Optional[str] = Field(None, min_length=1)
    # Add other updatable fields as needed

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime.datetime # Use datetime for potential formatting
    updated_at: datetime.datetime

    class Config:
        from_attributes = True # Changed from orm_mode

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse # Include user details on login

# --- Teacher Schemas ---

class TeacherBase(BaseModel):
    department: str
    title: str

class TeacherCreate(TeacherBase):
    # Used when creating teacher via admin endpoint, linked to user creation
    user_id: Optional[int] = None # Set internally

class TeacherUpdate(BaseModel):
    department: Optional[str] = None
    title: Optional[str] = None

class TeacherResponse(TeacherBase):
    id: int
    user_id: int
    user: Optional[UserResponse] = None # Embed user details
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True # Changed from orm_mode

# --- Student Schemas ---

class StudentBase(BaseModel):
    student_number: str
    department: str

class StudentCreate(StudentBase):
    # Used when creating student via admin endpoint, linked to user creation
    user_id: Optional[int] = None # Set internally

class StudentUpdate(BaseModel):
    student_number: Optional[str] = None
    department: Optional[str] = None

class StudentResponse(StudentBase):
    id: int
    user_id: int
    face_photo_url: Optional[str] = None
    # face_encodings are internal, not usually returned
    user: Optional[UserResponse] = None # Embed user details
    estimated_age: Optional[int] = None
    estimated_gender: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True # Changed from orm_mode

class StudentFaceUploadResponse(BaseModel):
    message: str
    face_photo_url: Optional[str]
    student_id: int 