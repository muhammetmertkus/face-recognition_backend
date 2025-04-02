from functools import wraps
from flask import jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services import data_service

USERS_FILE = 'users.json'

def get_current_user_role_and_id():
    """Helper function to get the role and INT id of the current JWT identity."""
    user_id_str = get_jwt_identity()
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        current_app.logger.error(f"Invalid user ID format in JWT: {user_id_str}")
        return None, None
        
    user = data_service.find_one(USERS_FILE, id=user_id)
    if user:
        return user.get('role'), user_id
    return None, None

def role_required(allowed_roles: list):
    """Decorator to ensure user has one of the allowed roles."""
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_role, _ = get_current_user_role_and_id()
            if current_role is None:
                 return jsonify({"message": "Invalid token identity or user not found"}), 401
            if current_role not in allowed_roles:
                return jsonify({"message": f"Access forbidden: Requires one of roles {allowed_roles}"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# Specific role decorators (examples)
def admin_required(fn):
    return role_required(["ADMIN"])(fn)

def teacher_required(fn):
    # Teachers and Admins can access teacher-specific routes usually
    return role_required(["ADMIN", "TEACHER"])(fn)

def student_required(fn):
     # Students and Admins can access student-specific routes usually
    return role_required(["ADMIN", "STUDENT"])(fn)


# Decorator for checking if the current user is the owner (e.g., updating their own profile)
def self_or_admin_required(resource_id_param: str, resource_type: str):
    """Decorator allowing access if user is ADMIN or the owner of the resource."""
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_role, current_user_id = get_current_user_role_and_id()

            if current_role is None or current_user_id is None:
                 return jsonify({"message": "Invalid token identity or user not found"}), 401

            if current_role == "ADMIN":
                return fn(*args, **kwargs) # Admin has access

            resource_id = kwargs.get(resource_id_param)
            if resource_id is None:
                 return jsonify({"message": "Internal server error: Resource ID not found in route"}), 500

            # Check ownership based on resource type
            if resource_type == "teacher":
                teacher_profile = data_service.find_one("teachers.json", id=resource_id)
                if teacher_profile and teacher_profile.get('user_id') == current_user_id:
                    return fn(*args, **kwargs) # User is the owner
            elif resource_type == "student":
                 student_profile = data_service.find_one("students.json", id=resource_id)
                 if student_profile and student_profile.get('user_id') == current_user_id:
                     return fn(*args, **kwargs) # User is the owner
            elif resource_type == "course": # Check if current user is the teacher of the course
                 course = data_service.find_one("courses.json", id=resource_id)
                 if course:
                     teacher_profile = data_service.find_one("teachers.json", id=course.get('teacher_id'))
                     if teacher_profile and teacher_profile.get('user_id') == current_user_id:
                         return fn(*args, **kwargs) # User is the teacher of the course

            return jsonify({"message": "Access forbidden: Requires admin privileges or ownership"}), 403
        return wrapper
    return decorator 