from dataclasses import dataclass, field
from typing import Optional, List
import datetime

# Helper function for default created_at/updated_at
def default_datetime():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

@dataclass
class User:
    id: int
    email: str
    password_hash: str
    first_name: str
    last_name: str
    role: str # "ADMIN", "TEACHER", "STUDENT"
    is_active: bool = True
    created_at: str = field(default_factory=default_datetime)
    updated_at: str = field(default_factory=default_datetime)

    # Helper to prevent returning password hash in API responses implicitly
    def to_dict(self, exclude_password=True):
        d = self.__dict__.copy()
        if exclude_password:
            d.pop('password_hash', None)
        return d

@dataclass
class Teacher:
    id: int
    user_id: int
    department: str
    title: str
    created_at: str = field(default_factory=default_datetime)
    updated_at: str = field(default_factory=default_datetime)
    # You might add related user info here if needed frequently, or join later
    # user: Optional[User] = None

@dataclass
class Student:
    id: int
    user_id: int
    student_number: str
    department: str
    face_encodings: Optional[str] = None # Stored as JSON string or similar
    face_photo_url: Optional[str] = None
    created_at: str = field(default_factory=default_datetime)
    updated_at: str = field(default_factory=default_datetime)
    # user: Optional[User] = None 