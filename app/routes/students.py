import os
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from werkzeug.utils import secure_filename
import datetime

from flask_jwt_extended import jwt_required

from app.services import data_service, face_service
from app.schemas.user import StudentResponse, StudentUpdate, StudentFaceUploadResponse, UserResponse
from app.schemas.course import CourseResponse # For listing student courses
from app.models.user import Student, default_datetime
from app.utils.auth import admin_required, teacher_required, student_required, get_current_user_role_and_id, self_or_admin_required

students_bp = Blueprint('students_bp', __name__)

USERS_FILE = 'users.json'
STUDENTS_FILE = 'students.json'
STUDENT_COURSE_FILE = 'student_course.json'
COURSES_FILE = 'courses.json'
ATTENDANCE_DETAILS_FILE = 'attendance_details.json'

def _get_student_with_user(student_dict):
    """Yardımcı fonksiyon: Öğrenci detaylarına kullanıcı bilgilerini ekler ve hassas verileri çıkarır."""
    if not student_dict:
        return None
    user = data_service.find_one(USERS_FILE, id=student_dict.get('user_id'))
    if user:
        user.pop('password_hash', None)
        student_dict['user'] = user
    # Genel yanıtlardan yüz kodlamalarını güvenlik/kısalık için kaldır
    student_dict.pop('face_encodings', None)
    return student_dict

@students_bp.route('/', methods=['GET'])
@teacher_required # Admin ve Öğretmenlerin listeyi görmesine izin ver
def get_students():
    """
    Tüm öğrencilerin listesini kullanıcı detaylarıyla birlikte getirir.
    ---    
    tags:
      - Öğrenciler (Students)
    security:
      - Bearer: []
    responses:
      200:
        description: Öğrencilerin listesi.
        schema:
          type: array
          items:
            $ref: '#/definitions/StudentResponse' 
        examples:
          application/json:
            - id: 5
              user_id: 10
              student_number: "S12345"
              department: "Bilgisayar Mühendisliği"
              face_photo_url: "/uploads/faces/student_5_foto.jpg"
              created_at: "2024-01-15T14:00:00Z"
              updated_at: "2024-01-16T09:30:00Z"
              user:
                id: 10
                email: "ayse.kaya@ornek.com"
                first_name: "Ayşe"
                last_name: "Kaya"
                role: "STUDENT"
                is_active: true
            - id: 6
              user_id: 11
              student_number: "S67890"
              department: "Elektrik Mühendisliği"
              face_photo_url: null
              created_at: "2024-01-16T11:20:00Z"
              updated_at: "2024-01-16T11:20:00Z"
              user:
                id: 11
                email: "mehmet.can@ornek.com"
                first_name: "Mehmet"
                last_name: "Can"
                role: "STUDENT"
                is_active: true
      401:
        description: Yetkisiz. Geçerli token sağlanmadı.
      403:
        description: Yasak. Kullanıcı Admin veya Öğretmen değil.
    definitions:
      # StudentResponse ve iç içe UserResponse tanımları (global değilse)
      # UserResponse tanımı app/schemas/user.py içinde global olarak tanımlı olduğu için
      # burada tekrar tanımlamaya gerek yok. Flasgger bunu otomatik alacaktır.
      # UserResponseShort tanımı kaldırıldı.
      StudentResponse:
          type: object
          description: Bir öğrencinin detaylı bilgilerini içeren yanıt modeli.
          properties:
              id:
                  type: integer
                  description: Öğrenci profilinin benzersiz ID'si.
                  example: 5
              user_id:
                  type: integer
                  description: İlişkili kullanıcı hesabının ID'si.
                  example: 10
              student_number:
                  type: string
                  description: Öğrencinin benzersiz numarası.
                  example: "S12345"
              department:
                  type: string
                  description: Öğrencinin bölümü.
                  example: "Bilgisayar Mühendisliği"
              face_photo_url:
                  type: string
                  nullable: true
                  description: Öğrencinin yüklenmiş yüz fotoğrafının sunucudaki göreceli yolu (varsa).
                  example: "/uploads/faces/student_5_foto.jpg"
              estimated_age:
                  type: integer
                  nullable: true
                  description: Öğrencinin fotoğrafından DeepFace ile tahmin edilen yaş.
                  example: 22
              estimated_gender:
                  type: string
                  nullable: true
                  description: Öğrencinin fotoğrafından DeepFace ile tahmin edilen cinsiyet (örn. 'Man', 'Woman').
                  example: "Woman"
              created_at:
                  type: string
                  format: date-time
                  description: Öğrenci profilinin oluşturulma zaman damgası.
                  example: "2024-01-15T14:00:00Z"
              updated_at:
                  type: string
                  format: date-time
                  description: Öğrenci profilinin son güncellenme zaman damgası.
                  example: "2024-01-16T09:30:00Z"
              user:
                  $ref: '#/definitions/UserResponse'
                  description: Öğrenciye ait kullanıcı hesabı detayları.
    """
    students_list = data_service.read_data(STUDENTS_FILE)
    detailed_students = [_get_student_with_user(s.copy()) for s in students_list] # Kopya kullanmak iyi pratik
    return jsonify(detailed_students), 200

@students_bp.route('/<int:student_id>', methods=['GET'])
@student_required # Admin, Öğretmen ve Öğrencinin kendisi erişebilir
def get_student(student_id):
    """
    Belirli bir öğrencinin detaylarını getirir (tahmini yaş/cinsiyet dahil).
    ---    
    tags:
      - Öğrenciler (Students)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        type: integer
        required: true
        description: Detayları alınacak öğrencinin ID'si.
        example: 5
    responses:
      200:
        description: Öğrenci detayları başarıyla alındı.
        schema:
          $ref: '#/definitions/StudentResponse' # Updated definition in docstring below
        examples:
          application/json:
            id: 5
            user_id: 10
            student_number: "S12345"
            department: "Bilgisayar Mühendisliği"
            face_photo_url: "/uploads/faces/student_5_foto.jpg"
            estimated_age: 22 # Added
            estimated_gender: "Woman" # Added
            created_at: "2024-01-15T14:00:00Z"
            updated_at: "2024-01-16T09:30:00Z"
            user:
              id: 10
              email: "ayse.kaya@ornek.com"
              first_name: "Ayşe"
              last_name: "Kaya"
              role: "STUDENT"
              is_active: true
      401:
        description: Yetkisiz. Geçerli token sağlanmadı.
      403:
        description: Yasak. Kullanıcı bu öğrencinin bilgilerini görme yetkisine sahip değil.
      404:
        description: Belirtilen ID'ye sahip öğrenci bulunamadı.
    definitions:
      # StudentResponse definition including new fields
      StudentResponse:
          type: object
          description: Bir öğrencinin detaylı bilgilerini içeren yanıt modeli.
          properties:
              id:
                  type: integer
              user_id:
                  type: integer
              student_number:
                  type: string
              department:
                  type: string
              face_photo_url:
                  type: string
                  nullable: true
              estimated_age:
                  type: integer
                  nullable: true
                  description: Öğrencinin fotoğrafından DeepFace ile tahmin edilen yaş.
                  example: 22
              estimated_gender:
                  type: string
                  nullable: true
                  description: Öğrencinin fotoğrafından DeepFace ile tahmin edilen cinsiyet (örn. 'Man', 'Woman').
                  example: "Woman"
              created_at:
                  type: string
                  format: date-time
              updated_at:
                  type: string
                  format: date-time
              user:
                  $ref: '#/definitions/UserResponse'
    """
    student = data_service.find_one(STUDENTS_FILE, id=student_id)
    if not student:
        return jsonify({"message": "Öğrenci bulunamadı"}), 404
    
    # Yetkilendirme decorator tarafından kontrol edilir
    detailed_student = _get_student_with_user(student.copy())

    # --- Analyze Age and Gender --- 
    estimated_age = None
    estimated_gender = None
    face_url = detailed_student.get('face_photo_url')

    if face_url:
        try:
            # Convert relative URL to absolute path
            # Assumes FACE_UPLOAD_FOLDER is configured correctly and accessible
            # Note: face_photo_url might contain the base upload folder already or not.
            # Adjust path joining logic based on how URLs are stored.
            # Example Logic: If URL starts with configured static path segment
            
            # Simplistic approach: Assume URL is relative to upload folder base
            # This needs careful adjustment based on your actual URL structure and file saving logic
            upload_folder = current_app.config.get('FACE_UPLOAD_FOLDER') # Get abs path from config
            if upload_folder:
                 # Extract filename from URL (handle potential leading slashes)
                 filename = os.path.basename(face_url.strip('/'))
                 absolute_image_path = os.path.join(upload_folder, filename)

                 if os.path.exists(absolute_image_path):
                    analysis_result = face_service.analyze_age_and_gender(absolute_image_path)
                    if analysis_result:
                        estimated_age = analysis_result.get('age')
                        estimated_gender = analysis_result.get('gender')
                 else:
                     current_app.logger.warning(f"Face photo file not found at expected path: {absolute_image_path} (derived from URL: {face_url})")
            else:
                 current_app.logger.error("FACE_UPLOAD_FOLDER is not configured.")

        except Exception as e:
            # Log error but don't fail the request, just return no age/gender
            current_app.logger.error(f"Error analyzing age/gender for student {student_id} from {face_url}: {e}")
    
    # Add results to the response dictionary
    detailed_student['estimated_age'] = estimated_age
    detailed_student['estimated_gender'] = estimated_gender
    # --- End Analyze Age and Gender ---

    return jsonify(detailed_student), 200

# POST / endpoint ile öğrenci oluşturma /api/auth/register altında
# role="STUDENT" ile yapılır.

@students_bp.route('/<int:student_id>', methods=['PUT'])
@admin_required # Sadece Admin öğrenci no/bölüm güncelleyebilir
def update_student(student_id):
    """
    Bir öğrencinin profilini (öğrenci numarası, bölüm) günceller. Sadece Admin yetkilidir.
    Kullanıcı bilgilerini (ad, soyad vb.) güncellemek için /api/auth/me (PUT) endpoint'i kullanılmalıdır.
    ---    
    tags:
      - Öğrenciler (Students)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        type: integer
        required: true
        description: Güncellenecek öğrencinin ID'si.
        example: 5
      - in: body
        name: body
        required: true
        description: Güncellenecek öğrenci profili bilgileri.
        schema:
          $ref: '#/definitions/StudentUpdate'
    responses:
      200:
        description: Öğrenci profili başarıyla güncellendi. Güncellenmiş öğrenci detaylarını döndürür.
        schema:
          $ref: '#/definitions/StudentResponse' # Tanımı tekrar kullan
        examples:
          application/json:
            id: 5
            user_id: 10
            student_number: "S12345-NEW"
            department: "Yazılım Mühendisliği"
            face_photo_url: "/uploads/faces/student_5_foto.jpg"
            created_at: "2024-01-15T14:00:00Z"
            updated_at: "2024-03-10T12:00:00Z"
            user:
              id: 10
              email: "ayse.kaya@ornek.com"
              first_name: "Ayşe" 
              last_name: "Kaya"
              role: "STUDENT"
              is_active: true
      400:
        description: |-
          Geçersiz girdi verisi veya işlem hatası. Sebepleri:
          - İstek gövdesi eksik veya geçersiz.
          - Güncellenecek alan sağlanmadı.
          - Yeni `student_number` başka bir öğrenciye ait.
        examples:
          application/json (Validation): { "message": "Doğrulama Hatası", "errors": [{"field": "department", "message": "Bu alan boş olamaz"}] }
          application/json (Conflict): { "message": "Öğrenci numarası 'S99999' zaten mevcut" }
          application/json (No Data): { "message": "Güncellenecek alan sağlanmadı" }
      401:
        description: Yetkisiz. Geçerli token sağlanmadı.
      403:
        description: Yasak. Kullanıcı Admin değil.
      404:
        description: Belirtilen ID'ye sahip öğrenci bulunamadı.
    definitions:
      StudentUpdate:
        type: object
        description: Öğrenci profili güncelleme için istek gövdesi modeli.
        properties:
          student_number:
            type: string
            description: Öğrencinin yeni benzersiz numarası.
            example: "S12345-NEW"
          department:
            type: string
            description: Öğrencinin yeni bölümü.
            example: "Yazılım Mühendisliği"
    """
    student = data_service.find_one(STUDENTS_FILE, id=student_id)
    if not student:
        return jsonify({"message": "Öğrenci bulunamadı"}), 404

    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "Girdi verisi sağlanmadı"}), 400

    try:
        update_data = StudentUpdate(**json_data)
    except ValidationError as e:
        # --- Pydantic hatalarını JSON serileştirmesi için formatla --- 
        error_details = []
        for error in e.errors():
            field = ".".join(map(str, error.get('loc', [])))
            message = error.get('msg', 'Bilinmeyen hata')
            error_details.append({"field": field, "message": message})
        current_app.logger.warning(f"{student_id} ID'li öğrenci güncellemesi için doğrulama başarısız: {error_details}")
        return jsonify({"message": "Doğrulama Hatası", "errors": error_details}), 400
        # --- Formatlama sonu --- 

    updates = update_data.dict(exclude_unset=True) # Sadece gönderilen alanları al
    if not updates:
        return jsonify({"message": "Güncellenecek alan sağlanmadı"}), 400

    # Eğer student_number güncelleniyorsa ve başka bir öğrenciye aitse kontrol et
    new_student_number = updates.get('student_number')
    if new_student_number and new_student_number != student.get('student_number'):
        existing_student = data_service.find_one(STUDENTS_FILE, student_number=new_student_number)
        if existing_student and existing_student.get('id') != student_id:
            return jsonify({"message": f"Öğrenci numarası '{new_student_number}' zaten mevcut"}), 400

    updates['updated_at'] = default_datetime()

    updated_student_dict = data_service.update_item(STUDENTS_FILE, student_id, updates)

    if not updated_student_dict:
        # Bu durum, update_item içindeki bir hatayı veya yarış durumunu gösterebilir
        return jsonify({"message": "Öğrenci güncelleme başarısız"}), 500

    detailed_student = _get_student_with_user(updated_student_dict.copy())
    return jsonify(detailed_student), 200

@students_bp.route('/<int:student_id>', methods=['DELETE'])
@admin_required # Sadece Admin öğrenci silebilir
def delete_student(student_id):
    """
    Bir öğrenciyi ve ilişkili kullanıcı hesabını siler. (Sadece Admin yetkilidir)
    DİKKAT: Bu işlem öğrencinin tüm verilerini (kayıtlar, yoklamalar vb.) ve kullanıcı hesabını kalıcı olarak siler!
    Mevcut implementasyon, silmeden önce aktif ders kaydı kontrolü yapmaz.
    ---    
    tags:
      - Öğrenciler (Students)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        type: integer
        required: true
        description: Silinecek öğrencinin ID'si.
        example: 6
    responses:
      200:
        description: Öğrenci ve ilişkili veriler başarıyla silindi.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Öğrenci 6 ve ilişkili veriler başarıyla silindi"
      400:
        description: Öğrenci silinemedi (örn. aktif ders kaydı gibi kısıtlamalar - bu kontrol şu an yok).
      401:
        description: Yetkisiz. Geçerli token sağlanmadı.
      403:
        description: Yasak. Kullanıcı Admin değil.
      404:
        description: Belirtilen ID'ye sahip öğrenci bulunamadı.
      500:
        description: Silme işlemi sırasında bir sunucu hatası oluştu.
    """
    student = data_service.find_one(STUDENTS_FILE, id=student_id)
    if not student:
        return jsonify({"message": "Öğrenci bulunamadı"}), 404

    user_id = student.get('user_id')

    # **Potansiyel İyileştirme**: Silmeden önce aktif ders kayıtlarını, yoklama kayıtlarını vb.
    # kontrol et. Basitlik için bu kontrol atlanmıştır.
    # Örnek kontrol:
    # enrollments = data_service.find_many(STUDENT_COURSE_FILE, student_id=student_id)
    # if enrollments:
    #    return jsonify({"message": "Aktif ders kaydı olan öğrenci silinemez."}), 400

    try:
        # 1. Öğrenci-ders ilişkilerini sil
        num_enrollments_deleted = data_service.delete_many(STUDENT_COURSE_FILE, student_id=student_id)
        current_app.logger.info(f"{student_id} ID'li öğrenci için {num_enrollments_deleted} ders kaydı silindi.")

        # 2. Yoklama detaylarını sil (isteğe bağlı ama temizlik için iyi)
        # Bu, önce yoklama kayıtlarını bulmayı, sonra detayları silmeyi gerektirir. Daha karmaşık.
        # Basamaklı silme mantığına daha sağlam bir şekilde ihtiyaç olup olmadığını düşünün.
        num_attendance_details_deleted = data_service.delete_many(ATTENDANCE_DETAILS_FILE, student_id=student_id)
        current_app.logger.info(f"{student_id} ID'li öğrenci için {num_attendance_details_deleted} yoklama detayı silindi.")
        # TODO: Varsa Emotion History kayıtlarını da sil

        # 3. Öğrenci profilini sil
        deleted_student = data_service.delete_item(STUDENTS_FILE, student_id)
        if not deleted_student:
             # Eğer find_one başarılıysa burası olmamalı ama loglamak iyi olabilir
             current_app.logger.error(f"Öğrenci profili {student_id} silinemedi (önce bulunmuştu).")
             return jsonify({"message": "Öğrenci profili silinemedi"}), 500

        # 4. İlişkili kullanıcı hesabını sil
        if user_id:
            deleted_user = data_service.delete_item(USERS_FILE, user_id)
            if not deleted_user:
                current_app.logger.warning(f"Öğrenci profili {student_id} silindi, ancak ilişkili kullanıcı {user_id} silinemedi.")
                # Başarı mesajı döndür ama kullanıcı sorunu belirtilebilir?
                # return jsonify({"message": f"Öğrenci profili {student_id} silindi, ancak ilişkili kullanıcı {user_id} kalmış olabilir."}), 200
        
        # 5. İlişkili yüz fotoğrafını dosya sisteminden sil (varsa)
        face_photo_path = student.get('face_photo_url')
        if face_photo_path:
            try:
                # Fotoğraf yolunun nasıl saklandığına bağlı olarak tam yolu oluştur
                # Örneğin: /uploads/faces/student_5...jpg veya sadece student_5...jpg
                if face_photo_path.startswith('/'):
                    # Muhtemelen web sunucusu tarafından sunulan göreceli yol
                    # Tam dosya sistemi yolu için yapılandırmaya veya root_path'e ihtiyaç var
                     base_upload_folder = current_app.config.get('FACE_UPLOAD_FOLDER', '')
                     if base_upload_folder:
                        # photo_path'ın başlangıçtaki / işaretini kaldırarak birleştir
                        filename = os.path.basename(face_photo_path)
                        full_path = os.path.join(base_upload_folder, filename) 
                     else:
                        full_path = None # Klasör bilinmiyorsa silme
                        current_app.logger.warning("FACE_UPLOAD_FOLDER yapılandırılmadığı için yüz fotoğrafı silinemedi.")
                else:
                    # Sadece dosya adı ise
                    base_upload_folder = current_app.config.get('FACE_UPLOAD_FOLDER', '')
                    if base_upload_folder:
                        full_path = os.path.join(base_upload_folder, face_photo_path)
                    else:
                         full_path = None
                         current_app.logger.warning("FACE_UPLOAD_FOLDER yapılandırılmadığı için yüz fotoğrafı silinemedi.")

                if full_path and os.path.exists(full_path):
                    os.remove(full_path)
                    current_app.logger.info(f"{student_id} ID'li öğrenci için yüz fotoğrafı silindi: {full_path}")
            except Exception as e:
                current_app.logger.error(f"Yüz fotoğrafı {face_photo_path} silinirken hata: {e}")


        return jsonify({"message": f"Öğrenci {student_id} ve ilişkili veriler başarıyla silindi"}), 200

    except Exception as e:
        current_app.logger.error(f"{student_id} ID'li öğrenci veya ilişkili veriler silinirken hata: {e}")
        # Burada geri alma daha karmaşık olabilir.
        return jsonify({"message": "Silme sırasında bir hata oluştu."}), 500


@students_bp.route('/<int:student_id>/face', methods=['POST'])
@jwt_required()
def upload_student_face(student_id):
    """
    Belirli bir öğrenci için bir yüz fotoğrafı yükler ve yüz kodlamalarını çıkarıp kaydeder.
    Mevcut bir fotoğraf varsa üzerine yazılır.
    Yetki: Öğrencinin kendisi, Öğretmenler veya Admin.
    ---    
    tags:
      - Öğrenciler (Students)
      - Yüz Tanıma (Face Recognition)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        type: integer
        required: true
        description: Yüz fotoğrafı yüklenecek öğrencinin ID'si.
        example: 5
      - in: formData
        name: file
        type: file
        required: true
        description: Yüklenecek öğrenci yüz fotoğrafı.
    responses:
      200:
        description: Yüz fotoğrafı başarıyla yüklendi ve kodlamalar kaydedildi.
        schema:
          $ref: '#/definitions/StudentFaceUploadResponse'
        examples:
          application/json:
            message: "Yüz fotoğrafı başarıyla yüklendi ve kodlamalar kaydedildi."
            face_photo_url: "/uploads/faces/student_5_face_20240310120530.jpg"
            encodings_count: 1 # Veya bulunan kodlama sayısı
      400:
        description: |-
          Geçersiz istek. Sebepleri:
          - İstekte dosya bölümü yok.
          - Seçili dosya yok.
          - Dosya türü desteklenmiyor (izin verilenler: jpg, jpeg, png).
          - Yüklenen resimde yüz tespit edilemedi.
          - Yüz kodlaması çıkarılamadı.
        examples:
          application/json (No File): { "message": "İstekte dosya bölümü yok" }
          application/json (Invalid Type): { "message": "Dosya türüne izin verilmiyor..." }
          application/json (No Face): { "message": "Yüklenen resimde yüz tespit edilemedi." }
      401:
        description: Yetkisiz. Geçerli token sağlanmadı.
      403:
        description: Yasak. Kullanıcının bu işlemi yapma yetkisi yok (Öğrencinin kendisi, Öğretmen veya Admin değil).
        examples:
          application/json: { "message": "Bu işlem için yetkiniz yok." }
      404:
        description: Belirtilen ID'ye sahip öğrenci bulunamadı.
    definitions:
      StudentFaceUploadResponse:
          type: object
          properties:
              message:
                  type: string
                  example: "Yüz fotoğrafı başarıyla yüklendi..."
              face_photo_url:
                  type: string
                  description: Kaydedilen fotoğrafın sunucu yolu.
                  example: "/uploads/faces/student_5_face.jpg"
              encodings_count:
                   type: integer
                   description: Fotoğraftan çıkarılan ve kaydedilen yüz kodlaması sayısı.
                   example: 1
              student_id:
                  type: integer
                  description: Yüzü yüklenen öğrencinin ID'si.
                  example: 5
    """
    # --- Custom Authorization Check --- 
    current_role, current_user_id = get_current_user_role_and_id()
    if current_role is None or current_user_id is None:
        return jsonify({"message": "Geçersiz token kimliği veya kullanıcı bulunamadı"}), 401
    
    student = data_service.find_one(STUDENTS_FILE, id=student_id)
    if not student:
        return jsonify({"message": "Öğrenci bulunamadı"}), 404

    is_owner = student.get('user_id') == current_user_id
    is_admin = current_role == "ADMIN"
    is_teacher = current_role == "TEACHER"

    if not (is_owner or is_admin or is_teacher):
        return jsonify({"message": "Bu işlem için yetkiniz yok."}), 403
    # --- End Custom Authorization Check --- 

    # --- File Handling and Validation ---
    if 'file' not in request.files:
        return jsonify({"message": "İstekte dosya bölümü yok"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "Seçili dosya yok"}), 400

    # Dosya adı kontrolünden sonra dosya varlığını ve izin verilen türü kontrol et
    if file and face_service.allowed_file(file.filename):
        try:
            # Yüz kodlamalarını bul (izin verilmeyen tür için ValueError yükseltir)
            # Bu dosyayı okur, sonra kaydetmek için stream işaretçisini sıfırlamamız gerekir
            # Dosyayı belleğe okumak yerine doğrudan yol ile çalışmak daha verimli olabilir
            # temp_path = ... # Dosyayı geçici bir yere kaydet
            # encodings = face_service.find_face_encodings_from_path(temp_path)
            
            # Mevcut implementasyon: dosyayı doğrudan işle
            file.seek(0) # Stream'i başa sar
            encodings = face_service.find_face_encodings(file) # Bu, dosya içeriğini okur

            if not encodings:
                return jsonify({"message": "Yüklenen resimde yüz bulunamadı."}), 400
            if len(encodings) > 1:
                 # Politika: Profil fotoğrafları için birden fazla yüz içeren resimleri reddet
                 return jsonify({"message": "Resimde birden fazla yüz bulundu. Lütfen sadece bir yüz içeren bir resim yükleyin."}), 400

            face_encoding = encodings[0] # İlk (ve tek) kodlamayı kullan
            encoding_str = face_service.encode_encodings_for_json([face_encoding])

            # --- Dosyayı Kaydet --- 
            # Önce eski fotoğrafı silmek iyi bir pratik olabilir
            old_photo_path = student.get('face_photo_url')
            if old_photo_path:
                 try:
                      base_upload_folder = current_app.config.get('FACE_UPLOAD_FOLDER', '')
                      if base_upload_folder:
                           filename_only = os.path.basename(old_photo_path)
                           full_old_path = os.path.join(base_upload_folder, filename_only)
                           if os.path.exists(full_old_path):
                                os.remove(full_old_path)
                                current_app.logger.info(f"Eski yüz fotoğrafı silindi: {full_old_path}")
                 except Exception as delete_e:
                      current_app.logger.error(f"Eski yüz fotoğrafı {old_photo_path} silinirken hata: {delete_e}")
            
            # Yeni dosyayı kaydet
            filename = secure_filename(f"student_{student_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.{file.filename.rsplit('.', 1)[1].lower()}")
            upload_dir = current_app.config['FACE_UPLOAD_FOLDER']
            if not os.path.exists(upload_dir):
                 os.makedirs(upload_dir)
            file_path = os.path.join(upload_dir, filename)
            
            # Stream işaretçisini sıfırla ve dosyayı kaydet
            file.seek(0) 
            file.save(file_path)
            # Web erişimi için göreceli URL sakla (örneğin /uploads/faces/dosya.jpg)
            # Bu URL'nin uygulamanızın statik dosya sunumuyla eşleştiğinden emin olun
            relative_url_part = os.path.relpath(upload_dir, current_app.static_folder if current_app.static_folder else current_app.root_path)
            face_photo_url = f"/{relative_url_part.replace(os.sep, '/')}/{filename}" 
            current_app.logger.info(f"Yeni yüz fotoğrafı kaydedildi: {file_path}, URL: {face_photo_url}")
            # --- Dosya Kaydetme Sonu --- 

            # Öğrenci kaydını kodlama ve fotoğraf URL'si ile güncelle
            updates = {
                "face_encodings": encoding_str,
                "face_photo_url": face_photo_url,
                "updated_at": default_datetime()
            }
            updated_student = data_service.update_item(STUDENTS_FILE, student_id, updates)

            if not updated_student:
                 # Başlangıçta öğrenci bulunduysa olmamalı, ancak savunmacı olarak ele al
                 return jsonify({"message": "Yüz işlendikten sonra öğrenci kaydı güncellenemedi."}), 500

            response_data = StudentFaceUploadResponse(
                message="Yüz fotoğrafı başarıyla işlendi ve kodlama kaydedildi.",
                face_photo_url=face_photo_url,
                encodings_count=len(encodings),
                student_id=student_id
            )
            return jsonify(response_data.dict()), 200

        except ValueError as ve: # face_service'den geçersiz dosya türü hatasını işle
             return jsonify({"message": str(ve)}), 400
        except FileNotFoundError: # Eğer yüz tanıma geçici dosya kullanıyorsa
             current_app.logger.error(f"{student_id} için yüz işlenirken geçici dosya hatası.")
             return jsonify({"message": "Yüz işleme sırasında geçici dosya hatası."}) , 500
        except Exception as e:
            current_app.logger.error(f"{student_id} ID'li öğrenci için yüz işlenirken hata: {e}")
            return jsonify({"message": "Yüz işleme veya kaydetme sırasında bir hata oluştu."}), 500
    else:
        # İzin verilmeyen dosya türü
        allowed_extensions_str = ", ".join(face_service.ALLOWED_EXTENSIONS)
        return jsonify({"message": f"Dosya türüne izin verilmiyor. İzin verilenler: {allowed_extensions_str}"}), 400


@students_bp.route('/<int:student_id>/courses', methods=['GET'])
@self_or_admin_required(resource_id_param='student_id', resource_type='student') # Öğrencinin kendisi veya Admin
def get_student_courses(student_id):
    """
    Belirli bir öğrencinin kayıtlı olduğu tüm dersleri getirir.
    Yalnızca öğrencinin kendisi veya Admin yetkilidir.
    ---    
    tags:
      - Öğrenciler (Students)
      - Dersler (Courses)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        type: integer
        required: true
        description: Dersleri listelenecek öğrencinin ID'si.
        example: 5
    responses:
      200:
        description: Öğrencinin kayıtlı olduğu derslerin listesi.
        schema:
          type: array
          items:
            $ref: '#/definitions/CourseResponse' # CourseResponse tanımını tekrar kullan
        examples:
          application/json:
            - id: 1
              code: "CS101"
              name: "Bilgisayar Bilimlerine Giriş"
              teacher_id: 1
              semester: "2024-Bahar"
              created_at: "2024-01-10T10:00:00Z"
              updated_at: "2024-01-10T10:00:00Z"
              # İsteğe bağlı: Yanıta öğretmen/ders saati detayları eklenebilir
              # teacher: { ... }
              # lesson_times: [ ... ] 
            - id: 3
              code: "PHYS101"
              name: "Fizik I"
              teacher_id: 4
              semester: "2024-Bahar"
              created_at: "2024-01-12T09:00:00Z"
              updated_at: "2024-01-12T09:00:00Z"
      401:
        description: Yetkisiz. Geçerli token sağlanmadı.
      403:
        description: Yasak. Kullanıcı bu bilgilere erişim yetkisine sahip değil.
      404:
        description: Belirtilen ID'ye sahip öğrenci bulunamadı.
    # CourseResponse tanımı başka bir yerde (örn. courses.py) olabilir,
    # burada tekrar tanımlamak yerine ona referans verilebilir.
    """
    # Öğrencinin varlığını kontrol et
    student = data_service.find_one(STUDENTS_FILE, id=student_id)
    if not student:
        return jsonify({"message": "Öğrenci bulunamadı"}), 404

    # Öğrenciyle ilişkili ders ID'lerini bul
    enrollments = data_service.find_many(STUDENT_COURSE_FILE, student_id=student_id)
    course_ids = [enrollment['course_id'] for enrollment in enrollments]

    if not course_ids:
        return jsonify([]), 200 # Ders bulunamazsa boş liste döndür

    # Bulunan ID'ler için ders detaylarını al
    all_courses = data_service.read_data(COURSES_FILE)
    student_courses_raw = [course for course in all_courses if course['id'] in course_ids]

    # İsteğe bağlı: Öğretmen detayları, Pydantic modeli ile yanıtı zenginleştir
    student_courses_detailed = []
    for course_dict in student_courses_raw:
         # courses.py içindeki _get_course_details gibi bir yardımcı kullanılabilir
         # Veya sadece temel bilgileri döndür
         # teacher = data_service.find_one(...) 
         # course_dict['teacher'] = ...
         student_courses_detailed.append(course_dict) # Şimdilik ham haliyle ekle

    return jsonify(student_courses_detailed), 200 