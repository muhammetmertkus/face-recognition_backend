from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from pydantic import ValidationError
import datetime

from app.services import data_service
from app.schemas.user import (
    UserCreate, UserResponse, LoginRequest, TokenResponse,
    TeacherCreate, StudentCreate, UserUpdate, VALID_ROLES
)
from app.models.user import User, Teacher, Student, default_datetime

auth_bp = Blueprint('auth_bp', __name__)

USERS_FILE = 'users.json'
TEACHERS_FILE = 'teachers.json'
STUDENTS_FILE = 'students.json'

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Yeni bir kullanıcı (Admin, Teacher veya Student) kaydeder.
    Temel kullanıcı kaydını ve (varsa) ilgili Öğretmen veya Öğrenci profilini oluşturur.
    ---   
    tags:
      - Kimlik Doğrulama (Auth)
    parameters:
      - in: body
        name: body
        required: true
        description: Kullanıcı kayıt detayları. Rol, gerekli profil alanlarını belirler.
        schema:
          $ref: '#/definitions/UserCreate'
    responses:
      201:
        description: Kullanıcı ve (varsa) profil başarıyla oluşturuldu. Oluşturulan kullanıcı detaylarını döndürür.
        schema:
          $ref: '#/definitions/UserResponse'
        examples:
          application/json:
            id: 1
            email: "yeni.ogrenci@ornek.com"
            first_name: "Yeni"
            last_name: "Öğrenci"
            role: "STUDENT"
            is_active: true
            created_at: "2024-01-01T10:00:00Z"
            updated_at: "2024-01-01T10:00:00Z"
      400:
        description: |-
          Geçersiz girdi verisi sağlandı. Sebepleri şunlar olabilir:
          - Gerekli alanlar eksik.
          - Geçersiz e-posta formatı veya şifre uzunluğu.
          - Belirtilen rol için gerekli profil alanları (departman, unvan, öğrenci numarası) eksik.
          - E-posta veya Öğrenci Numarası zaten mevcut.
        examples:
          application/json: { "message": "Doğrulama Hatası", "errors": [{"field": "email", "message": "geçerli bir e-posta adresi değil"}] }
          application/json (Çakışma): { "message": "E-posta zaten kayıtlı" }
          application/json (Profil Çakışması): { "message": "Öğrenci numarası zaten mevcut" }
          application/json (Eksik Profil Alanı): { "message": "Öğrenciler için departman ve öğrenci numarası gereklidir" }
      500:
        description: Kullanıcı veya profil oluşturma sırasında sunucu hatası. Detaylar için sunucu loglarını kontrol edin.
    definitions:
      UserCreate:
        type: object
        required:
          - email
          - password
          - first_name
          - last_name
          - role # Rolü açıkça gerekli kıl
        properties:
          email:
            type: string
            format: email
            description: Kullanıcının benzersiz e-posta adresi.
            example: "ali.veli@ornek.com"
          password:
            type: string
            minLength: 6
            description: Kullanıcının şifresi (en az 6 karakter).
            example: "güvenliŞifre123"
          first_name:
            type: string
            minLength: 1
            description: Kullanıcının adı.
            example: "Ali"
          last_name:
            type: string
            minLength: 1
            description: Kullanıcının soyadı.
            example: "Veli"
          role:
            type: string
            enum: ["ADMIN", "TEACHER", "STUDENT"]
            description: Kullanıcının rolü. Gerekli profil alanlarını belirler.
            example: "STUDENT"
          department:
            type: string
            description: Rol TEACHER veya STUDENT ise gereklidir.
            example: "Bilgisayar Mühendisliği"
          title:
            type: string
            description: Rol TEACHER ise gereklidir.
            example: "Profesör"
          student_number:
            type: string
            description: Rol STUDENT ise gereklidir. Benzersiz olmalı.
            example: "S123456"
      UserResponse:
        type: object
        properties:
          id:
            type: integer
            description: Kullanıcı için benzersiz tanımlayıcı.
            example: 1
          email:
            type: string
            format: email
            description: Kullanıcının e-posta adresi.
            example: "ali.veli@ornek.com"
          first_name:
            type: string
            description: Kullanıcının adı.
            example: "Ali"
          last_name:
            type: string
            description: Kullanıcının soyadı.
            example: "Veli"
          role:
            type: string
            enum: ["ADMIN", "TEACHER", "STUDENT"]
            description: Kullanıcıya atanan rol.
            example: "STUDENT"
          is_active:
            type: boolean
            description: Kullanıcı hesabının aktif olup olmadığını belirtir.
            example: true
          created_at:
            type: string
            format: date-time
            description: Kullanıcının oluşturulma zaman damgası.
            example: "2024-01-01T10:00:00Z"
          updated_at:
            type: string
            format: date-time
            description: Kullanıcının son güncellenme zaman damgası.
            example: "2024-01-01T10:00:00Z"
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "Girdi verisi sağlanmadı"}), 400

    try:
        # Gerekirse burada enum dışında rol doğrulaması ekle
        user_data = UserCreate(**json_data)
    except ValidationError as e:
        # --- Pydantic hatalarını JSON serileştirmesi için formatla --- 
        error_details = []
        for error in e.errors():
            field = ".".join(map(str, error.get('loc', [])))
            message = error.get('msg', 'Bilinmeyen hata')
            # İsteğe bağlı: Hata mesajlarını Türkçeleştir
            # message = translate_error_message(error.get('msg'), error.get('type')) 
            error_details.append({"field": field, "message": message})
        current_app.logger.warning(f"Kullanıcı kaydı için doğrulama başarısız: {error_details}")
        return jsonify({"message": "Doğrulama Hatası", "errors": error_details}), 400
        # --- Formatlama sonu --- 

    # E-postanın zaten var olup olmadığını kontrol et
    if data_service.find_one(USERS_FILE, email=user_data.email):
        return jsonify({"message": "E-posta zaten kayıtlı"}), 400

    hashed_password = generate_password_hash(user_data.password)
    now = default_datetime()

    new_user_dict = {
        "email": user_data.email,
        "password_hash": hashed_password,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "role": user_data.role.upper(),
        "is_active": True,
        "created_at": now,
        "updated_at": now
    }

    user_id = None # Olası geri alma için user_id başlat
    try:
        created_user_dict = data_service.add_item(USERS_FILE, new_user_dict)
        user_id = created_user_dict['id']

        # Varsa Öğretmen veya Öğrenci profili oluştur
        if user_data.role.upper() == "TEACHER":
            # Teacher'a özgü alanları UserCreate'den doğrula
            try:
                teacher_data = TeacherCreate(**user_data.dict(include={'department', 'title'}))
            except ValidationError as profile_e:
                 data_service.delete_item(USERS_FILE, user_id) # Kullanıcı oluşturmayı geri al
                 # Profil hatalarını formatla
                 profile_error_details = [{"field": ".".join(map(str, err.get('loc',[]))), "message": err.get('msg','')} for err in profile_e.errors()]
                 return jsonify({"message": "Öğretmen Profili İçin Doğrulama Hatası", "errors": profile_error_details}), 400

            teacher_profile = {
                "user_id": user_id,
                "department": teacher_data.department,
                "title": teacher_data.title,
                "created_at": now,
                "updated_at": now
            }
            data_service.add_item(TEACHERS_FILE, teacher_profile)
        elif user_data.role.upper() == "STUDENT":
            # Student'a özgü alanları UserCreate'den doğrula
            try:
                student_data = StudentCreate(**user_data.dict(include={'department', 'student_number'}))
            except ValidationError as profile_e:
                 data_service.delete_item(USERS_FILE, user_id) # Kullanıcı oluşturmayı geri al
                 profile_error_details = [{"field": ".".join(map(str, err.get('loc',[]))), "message": err.get('msg','')} for err in profile_e.errors()]
                 return jsonify({"message": "Öğrenci Profili İçin Doğrulama Hatası", "errors": profile_error_details}), 400

            # Öğrenci numarasının zaten var olup olmadığını kontrol et
            if data_service.find_one(STUDENTS_FILE, student_number=student_data.student_number):
                data_service.delete_item(USERS_FILE, user_id) # Kullanıcı oluşturmayı geri al
                return jsonify({"message": "Öğrenci numarası zaten mevcut"}), 400
                
            student_profile = {
                "user_id": user_id,
                "student_number": student_data.student_number,
                "department": student_data.department,
                 "face_encodings": None,
                 "face_photo_url": None,
                 "created_at": now,
                 "updated_at": now
            }
            data_service.add_item(STUDENTS_FILE, student_profile)

        # Yanıt şeması için dict'i User modeline geri dönüştür
        # Gerekirse tutarlılığı sağlamak için kullanıcıyı tekrar al veya created_user_dict kullan
        user_obj = User(**created_user_dict)
        response_data = UserResponse.from_orm(user_obj).dict()
        return jsonify(response_data), 201

    except ValueError as ve:
        # Olası ID çakışmasını veya diğer veri servisi hatalarını işle
        current_app.logger.error(f"Kayıt sırasında veri servisi hatası: {ve}")
        if user_id: data_service.delete_item(USERS_FILE, user_id) # Geri almayı dene
        return jsonify({"message": str(ve)}), 400
    except Exception as e:
        current_app.logger.error(f"Kayıt sırasında hata: {e}")
        if user_id: data_service.delete_item(USERS_FILE, user_id) # Geri almayı dene
        return jsonify({"message": "Kayıt sırasında bir hata oluştu."}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Kullanıcıyı e-posta ve şifre ile doğrular, JWT token ve kullanıcı bilgilerini döndürür.
    ---    
    tags:
      - Kimlik Doğrulama (Auth)
    parameters:
      - in: body
        name: body
        required: true
        description: Kullanıcı giriş bilgileri.
        schema:
          $ref: '#/definitions/LoginRequest'
    responses:
      200:
        description: Giriş başarılı. Erişim token'ını ve kullanıcı detaylarını döndürür.
        schema:
          $ref: '#/definitions/TokenResponse'
        examples:
          application/json:
            access_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            token_type: "bearer"
            user:
              id: 1
              email: "ali.veli@ornek.com"
              first_name: "Ali"
              last_name: "Veli"
              role: "STUDENT"
              is_active: true
              created_at: "2024-01-01T10:00:00Z"
              updated_at: "2024-01-01T10:00:00Z"
      400:
        description: Geçersiz girdi verisi (örn. eksik alanlar, geçersiz e-posta formatı).
        examples:
          application/json: { "message": "Doğrulama Hatası", "errors": [{"field": "email", "message": "geçerli bir e-posta adresi değil"}] }
      401:
        description: Geçersiz e-posta, yanlış şifre veya aktif olmayan hesap nedeniyle kimlik doğrulama başarısız.
        examples:
           application/json: { "message": "Geçersiz e-posta veya şifre" }
           application/json (Aktif Değil): { "message": "Kullanıcı hesabı aktif değil" }
    definitions:
      LoginRequest:
        type: object
        required:
          - email
          - password
        properties:
          email:
            type: string
            format: email
            description: Kullanıcının kayıtlı e-posta adresi.
            example: "ali.veli@ornek.com"
          password:
            type: string
            description: Kullanıcının şifresi.
            example: "güvenliŞifre123"
      TokenResponse:
        type: object
        properties:
          access_token:
            type: string
            description: Sonraki istekleri doğrulamak için JWT erişim token'ı.
            example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
          token_type:
            type: string
            description: Verilen token türü.
            example: "bearer"
          user:
            $ref: '#/definitions/UserResponse' # UserResponse tanımını tekrar kullan
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "Girdi verisi sağlanmadı"}), 400

    try:
        login_data = LoginRequest(**json_data)
    except ValidationError as e:
        # --- Pydantic hatalarını JSON serileştirmesi için formatla --- 
        error_details = []
        for error in e.errors():
            field = ".".join(map(str, error.get('loc', [])))
            message = error.get('msg', 'Bilinmeyen hata')
            error_details.append({"field": field, "message": message})
        current_app.logger.warning(f"Giriş için doğrulama başarısız: {error_details}")
        return jsonify({"message": "Doğrulama Hatası", "errors": error_details}), 400
        # --- Formatlama sonu --- 

    user_dict = data_service.find_one(USERS_FILE, email=login_data.email)

    if not user_dict or not check_password_hash(user_dict['password_hash'], login_data.password):
        return jsonify({"message": "Geçersiz e-posta veya şifre"}), 401

    if not user_dict.get('is_active', False):
         return jsonify({"message": "Kullanıcı hesabı aktif değil"}), 401

    # --- Kimliği JWT için string'e dönüştür --- 
    user_id_str = str(user_dict['id'])
    access_token = create_access_token(identity=user_id_str)
    # --- Dönüşüm sonu --- 
    
    user_obj = User(**user_dict)
    user_response = UserResponse.from_orm(user_obj)

    token_response = TokenResponse(
        access_token=access_token,
        user=user_response
    )

    return jsonify(token_response.dict()), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """
    Geçerli JWT token'ına sahip kullanıcının bilgilerini getirir.
    Kullanıcının rolüne göre teacher_id veya student_id bilgisi de eklenir.
    ---    
    tags:
      - Kimlik Doğrulama (Auth)
    security:
      - Bearer: []
    responses:
      200:
        description: Geçerli kullanıcının bilgileri (şifre hariç).
        schema:
          $ref: '#/definitions/UserResponseWithProfileID' # Güncellenmiş şema tanımı
        examples:
          application/json (Teacher):
            id: 2
            email: "prof.ahmet@ornek.edu"
            first_name: "Ahmet"
            last_name: "Yılmaz"
            role: "TEACHER"
            is_active: true
            created_at: "2024-01-10T09:00:00Z"
            updated_at: "2024-02-20T11:30:00Z"
            teacher_id: 1 # Öğretmen profili ID'si
          application/json (Student):
            id: 10
            email: "ayse.kaya@ornek.com"
            first_name: "Ayşe"
            last_name: "Kaya"
            role: "STUDENT"
            is_active: true
            created_at: "2024-01-15T14:00:00Z"
            updated_at: "2024-01-16T09:30:00Z"
            student_id: 5 # Öğrenci profili ID'si
          application/json (Admin):
            id: 1
            email: "admin@ornek.com"
            first_name: "Admin"
            last_name: "User"
            role: "ADMIN"
            is_active": true
            created_at": "2024-01-01T08:00:00Z"
            updated_at": "2024-01-01T08:00:00Z"
      401:
        description: Yetkisiz. Geçerli token sağlanmadı veya token geçersiz.
      404:
        description: Token'daki user_id ile eşleşen kullanıcı bulunamadı.
    definitions:
        UserResponseWithProfileID: # Yeni şema tanımı
            allOf: # Mevcut UserResponse'u temel al
              - $ref: '#/definitions/UserResponse' 
            properties:
                teacher_id:
                    type: integer
                    description: Eğer kullanıcı bir öğretmen ise, öğretmen profilinin ID'si.
                    example: 1
                    nullable: true
                student_id:
                    type: integer
                    description: Eğer kullanıcı bir öğrenci ise, öğrenci profilinin ID'si.
                    example: 5
                    nullable: true
    """
    # Kullanıcı kimliğini JWT token'dan al
    user_id_str = get_jwt_identity()
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        current_app.logger.error(f"Invalid user ID format in JWT for /me: {user_id_str}")
        return jsonify({"message": "Geçersiz token kimliği"}), 401

    # Kullanıcı bilgilerini bul
    user = data_service.find_one(USERS_FILE, id=user_id)
    if not user:
        return jsonify({"message": "Kullanıcı bulunamadı"}), 404

    # Şifreyi yanıttan çıkar
    if 'password_hash' in user:
        user.pop('password_hash')
    
    # Kullanıcı rolünü kontrol et ve ilgili profil ID'sini ekle
    user_role = user.get('role')
    
    # Öğretmen ise teacher_id ekle
    if user_role == 'TEACHER':
        # DEBUG: Log ekleyelim
        current_app.logger.info(f"TEACHER rolü tespit edildi, user_id: {user_id}")
        
        teacher_profile = data_service.find_one(TEACHERS_FILE, user_id=user_id)
        if teacher_profile:
            # DEBUG: Profile bilgisini loglayalım
            current_app.logger.info(f"Bulunan öğretmen profili: {teacher_profile}")
            
            # DOĞRUDAN TEACHER_ID EKLEYELİM
            user['teacher_id'] = teacher_profile.get('id')
            current_app.logger.info(f"Eklenen teacher_id: {teacher_profile.get('id')}")
        else:
            user['teacher_id'] = None
            current_app.logger.warning(f"User {user_id} (Teacher) için öğretmen profili bulunamadı.")
    
    # Öğrenci ise student_id ekle
    elif user_role == 'STUDENT':
        student_profile = data_service.find_one(STUDENTS_FILE, user_id=user_id)
        if student_profile:
            user['student_id'] = student_profile.get('id')
        else:
            user['student_id'] = None
            current_app.logger.warning(f"User {user_id} (Student) için öğrenci profili bulunamadı.")
    
    # DEBUG: Son response'u loglayalım
    current_app.logger.info(f"GET /me response: {user}")
    
    return jsonify(user), 200

@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_me():
    """
    O anda kimliği doğrulanmış kullanıcının profilini (ad, soyad) günceller.
    Geçerli bir JWT token gerektirir. Yalnızca belirli alanların güncellenmesine izin verir.
    ---    
    tags:
      - Kimlik Doğrulama (Auth)
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        description: Kullanıcının profili için güncellenecek alanlar. Sadece first_name ve last_name izinlidir.
        schema:
          $ref: '#/definitions/UserUpdate'
    responses:
      200:
        description: Kullanıcı profili başarıyla güncellendi. Güncellenmiş kullanıcı profilini döndürür.
        schema:
          $ref: '#/definitions/UserResponse' # UserResponse tanımını tekrar kullan
        examples:
          application/json:
            id: 1
            email: "ali.veli@ornek.com"
            first_name: "Ahmet"
            last_name: "Veli"
            role: "STUDENT"
            is_active: true
            created_at: "2024-01-01T10:00:00Z"
            updated_at: "2024-01-02T11:30:00Z"
      400:
        description: Geçersiz girdi verisi (örn. eksik alanlar, doğrulama hatası) veya güncellenecek alan sağlanmadı.
        examples:
          application/json: { "message": "Doğrulama Hatası", "errors": [{"field": "first_name", "message": "bu değerin en az 1 karakter olduğundan emin olun"}] }
          application/json (Veri Yok): { "message": "Güncellenecek alan sağlanmadı" }
      401:
        description: Yetkisiz. Token eksik, geçersiz veya süresi dolmuş.
      404:
        description: Token ile ilişkili kullanıcı bulunamadı.
    definitions:
      UserUpdate:
        type: object
        properties:
          first_name:
            type: string
            minLength: 1
            description: Kullanıcının güncellenmiş adı.
            example: "Ahmet"
          last_name:
            type: string
            minLength: 1
            description: Kullanıcının güncellenmiş soyadı.
            example: "Veli"
    """
    # --- JWT kimliğini (string) int'e geri dönüştür --- 
    current_user_id_str = get_jwt_identity()
    try:
        current_user_id = int(current_user_id_str)
    except ValueError:
        current_app.logger.error(f"JWT'de geçersiz kullanıcı ID formatı: {current_user_id_str}")
        return jsonify({"message": "Geçersiz token kimliği"}), 401
    # --- Dönüşüm sonu --- 

    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "Girdi verisi sağlanmadı"}), 400

    try:
        update_data = UserUpdate(**json_data)
    except ValidationError as e:
        # --- Pydantic hatalarını JSON serileştirmesi için formatla --- 
        error_details = []
        for error in e.errors():
            field = ".".join(map(str, error.get('loc', [])))
            message = error.get('msg', 'Bilinmeyen hata')
            error_details.append({"field": field, "message": message})
        current_app.logger.warning(f"Profil güncellemesi için doğrulama başarısız: {error_details}")
        return jsonify({"message": "Doğrulama Hatası", "errors": error_details}), 400
        # --- Formatlama sonu --- 

    # Sadece istekte ayarlanan alanları al
    updates = update_data.dict(exclude_unset=True)
    if not updates:
         return jsonify({"message": "Güncellenecek alan sağlanmadı"}), 400

    # Güncelleme için zaman damgası ekle
    updates['updated_at'] = default_datetime()

    updated_user_dict = data_service.update_item(USERS_FILE, current_user_id, updates)

    if not updated_user_dict:
        return jsonify({"message": "Kullanıcı bulunamadı veya güncelleme başarısız"}), 404

    user_obj = User(**updated_user_dict)
    response_data = UserResponse.from_orm(user_obj).dict()
    return jsonify(response_data), 200 