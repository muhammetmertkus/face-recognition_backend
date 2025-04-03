from flask import Flask
from flask_jwt_extended import JWTManager
from flasgger import Swagger # Import Flasgger
from flask_cors import CORS # Import CORS
from config import Config
import os
from datetime import timedelta
from .routes.courses import courses_bp
from .routes.teachers import teachers_bp
from .routes.students import students_bp
from .routes.auth import auth_bp
from .routes.attendance import attendance_bp
from .routes.reports import reports_bp
from .routes.password_reset import password_reset

jwt = JWTManager()

# Define Swagger UI configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
    "swagger": "2.0", # Use Swagger 2.0 spec
    "info": {
        "title": "Yüz Tanıma ile Yoklama Sistemi API",
        "version": "1.0.0",
        "description": "Yüz tanıma kullanarak yoklama alan sistem için API",
    },
    # --- Add Security Definitions for JWT --- 
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Bearer şemasını kullanan JWT Yetkilendirme başlığı. Örnek: \"Authorization: Bearer {token}\""
        }
    },
    # --- Define tag order --- 
    "tags": [
        {"name": "Auth (Kimlik Doğrulama)", "description": "Kullanıcı Girişi, Kayıt ve Profil İşlemleri"},
        {"name": "Öğretmenler (Teachers)", "description": "Öğretmen Kayıtlarını Yönetme"},
        {"name": "Öğrenciler (Students)", "description": "Öğrenci Kayıtlarını ve Yüz Verilerini Yönetme"},
        {"name": "Dersler (Courses)", "description": "Ders Yönetimi ve Öğrenci/Ders İlişkileri"},
        {"name": "Yoklama (Attendance)", "description": "Yoklama Alma, Görüntüleme ve Manuel Güncelleme İşlemleri"},
        {"name": "Yüz Tanıma (Face Recognition)", "description": "Yüz Tanıma ile İlgili Yardımcı İşlemler (Genellikle Yoklama içinde kullanılır)"},
        {"name": "Raporlar (Reports)", "description": "Yoklama ve Duygu Durumu ile İlgili Raporlama Endpointleri"},
        {"name": "Duygular (Emotions)", "description": "Duygu Analizi Raporları (Geliştirme Aşamasında)"},
    ]
}

swagger = Swagger(config=swagger_config) # Initialize Swagger with config

def create_app(config_class=Config):
    """Flask application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize CORS - Allow specific frontend origin with detailed settings
    CORS(app, resources={
        r"/api/*": {
            "origins": ["https://facerecognitionattendance.netlify.app", "http://127.0.0.1:5000", "http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type", "Authorization"],
            "max_age": 600
        }
    })
    # Note: The previous CORS setting for localhost:3000 is now replaced.
    # Add localhost:3000 back to the "origins" list if local development is still needed:
    # "origins": ["https://facerecognitionattendance.netlify.app", "http://localhost:3000"]
    
    # Merge swagger config into app config
    app.config['SWAGGER'] = swagger_config

    # Ensure data directory exists
    if not os.path.exists(app.config['DATA_DIR']):
        os.makedirs(app.config['DATA_DIR'])
    # Ensure upload directories exist (moved from config.py for app context)
    face_upload_folder = os.path.join(app.root_path, app.config['FACE_UPLOAD_FOLDER'])
    attendance_upload_folder = os.path.join(app.root_path, app.config['ATTENDANCE_UPLOAD_FOLDER'])
    if not os.path.exists(face_upload_folder):
        os.makedirs(face_upload_folder)
    if not os.path.exists(attendance_upload_folder):
        os.makedirs(attendance_upload_folder)
    # Update config with absolute paths if needed elsewhere, though relative might be fine
    app.config['FACE_UPLOAD_FOLDER'] = face_upload_folder
    app.config['ATTENDANCE_UPLOAD_FOLDER'] = attendance_upload_folder

    # Initialize extensions
    jwt.init_app(app)
    swagger.init_app(app)

    # Register blueprints (API routes)
    app.register_blueprint(courses_bp, url_prefix='/api/courses')
    app.register_blueprint(teachers_bp, url_prefix='/api/teachers')
    app.register_blueprint(students_bp, url_prefix='/api/students')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(password_reset, url_prefix='/api/password')

    @app.route('/')
    def hello():
        # Simple route for testing
        return "<h1>Yüz Tanıma Backend Aktif! Swagger UI için /apidocs adresine gidin.</h1>"

    return app 