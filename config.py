import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'you-should-change-this')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'super-secret-jwt-key') # Change this!
    JWT_ACCESS_TOKEN_EXPIRES = False # Set to False for no expiration during development, or a timedelta

    # Data directory
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

    # Upload directories (relative to instance folder or a specific path)
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    FACE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'faces')
    ATTENDANCE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'attendance')

    # Ensure upload directories exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(FACE_UPLOAD_FOLDER):
        os.makedirs(FACE_UPLOAD_FOLDER)
    if not os.path.exists(ATTENDANCE_UPLOAD_FOLDER):
        os.makedirs(ATTENDANCE_UPLOAD_FOLDER) 