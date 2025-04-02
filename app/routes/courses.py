from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
import datetime
import os # Import the os module

from app.services import data_service
from app.schemas.course import (
    CourseResponse, CourseCreate, CourseUpdate, LessonTimeResponse, 
    StudentCourseLink, StudentCourseResponse, LessonTimeCreate # Ensure LessonTimeCreate is imported
)
from app.schemas.user import TeacherResponse, StudentResponse # Import related schemas
from app.schemas.attendance import AttendanceResponse # For listing attendance
from app.models.course import Course, LessonTime, StudentCourse, default_datetime
from app.utils.auth import jwt_required, teacher_required, admin_required, self_or_admin_required, get_jwt_identity, get_current_user_role_and_id

courses_bp = Blueprint('courses_bp', __name__)

COURSES_FILE = 'courses.json'
LESSON_TIMES_FILE = 'lesson_times.json'
TEACHERS_FILE = 'teachers.json'
USERS_FILE = 'users.json'
STUDENTS_FILE = 'students.json'
STUDENT_COURSE_FILE = 'student_course.json'
ATTENDANCE_FILE = 'attendance.json'
ATTENDANCE_DETAILS_FILE = 'attendance_details.json'
# EMOTION_HISTORY_FILE = 'emotion_history.json' # If needed later

def _get_course_details(course_dict):
    """Yardımcı fonksiyon: Bir dersin öğretmen ve ders saati detaylarını getirir."""
    if not course_dict:
        return None
    # Öğretmen detaylarını getir
    teacher = data_service.find_one(TEACHERS_FILE, id=course_dict.get('teacher_id'))
    if teacher:
        user = data_service.find_one(USERS_FILE, id=teacher.get('user_id'))
        if user:
            user.pop('password_hash', None)
            teacher['user'] = user
        course_dict['teacher'] = teacher
    
    # Ders saatlerini getir
    lesson_times = data_service.find_many(LESSON_TIMES_FILE, course_id=course_dict.get('id'))
    course_dict['lesson_times'] = lesson_times
    return course_dict

@courses_bp.route('/', methods=['GET'])
@jwt_required() # Giriş yapmış herhangi bir kullanıcı ders listesini görebilir
def get_courses():
    """
    Tüm derslerin listesini getirir.
    Her ders için öğretmen bilgileri (kullanıcı detayları dahil) ve ders saatleri (bu endpoint için özet) eklenir.
    ---    
    tags:
      - Dersler (Courses)
    security:
      - Bearer: []
    responses:
      200:
        description: Derslerin listesi (temel öğretmen bilgileriyle).
        schema:
          type: array
          items:
            $ref: '#/definitions/CourseResponse' 
        examples:
          application/json:
            - id: 1
              code: "CS101"
              name: "Bilgisayar Bilimlerine Giriş"
              teacher_id: 1
              semester: "2024-Bahar"
              created_at: "2024-01-10T10:00:00Z"
              updated_at: "2024-01-10T10:00:00Z"
              teacher:
                id: 1
                user_id: 2 
                department: "Bilgisayar Mühendisliği"
                title: "Profesör"
                user:
                    id: 2
                    email: "prof.ahmet@ornek.com"
                    first_name: "Ahmet"
                    last_name: "Yılmaz"
                    role: "TEACHER"
                    is_active: true
              lesson_times: [] # Liste görünümünde detay yok
            - id: 2
              code: "MATH201"
              name: "Lineer Cebir"
              teacher_id: 2
              semester: "2024-Bahar"
              created_at: "2024-01-11T11:00:00Z"
              updated_at: "2024-01-11T11:00:00Z"
              teacher:
                 # ... (öğretmen bilgileri) ...
                 id: 2
                 user_id: 3
                 department: "Matematik"
                 title: "Doçent"
                 user:
                     id: 3
                     email: "doc.ayse@ornek.com"
                     first_name: "Ayşe"
                     last_name: "Demir"
                     role: "TEACHER"
                     is_active: true
              lesson_times: []
      401:
        description: Yetkisiz. Geçerli bir token sağlanmadı.
    definitions:
      # Gerekirse CourseResponse ve iç içe geçmiş Teacher/User/LessonTime tanımları
      UserResponseShort:
          type: object
          description: Kullanıcının temel bilgileri (şifre hariç).
          properties:
            id:
                type: integer
                description: Kullanıcının benzersiz ID'si.
                example: 2
            email:
                type: string
                format: email
                description: Kullanıcının e-posta adresi.
                example: "prof.ahmet@ornek.com"
            first_name:
                type: string
                description: Kullanıcının adı.
                example: "Ahmet"
            last_name:
                type: string
                description: Kullanıcının soyadı.
                example: "Yılmaz"
            role:
                type: string
                enum: ["ADMIN", "TEACHER", "STUDENT"]
                description: Kullanıcının rolü.
                example: "TEACHER"
            is_active:
                type: boolean
                description: Hesap aktif mi?
                example: true
      TeacherResponseShort:
          type: object
          description: Öğretmenin temel profil bilgileri ve ilişkili kullanıcı detayları.
          properties:
             id:
                type: integer
                description: Öğretmen profilinin benzersiz ID'si.
                example: 1
             user_id:
                type: integer
                description: İlişkili kullanıcı hesabının ID'si.
                example: 2
             department:
                type: string
                description: Öğretmenin bölümü.
                example: "Bilgisayar Mühendisliği"
             title:
                type: string
                description: Öğretmenin unvanı.
                example: "Profesör"
             user:
                $ref: '#/definitions/UserResponseShort'
      LessonTimeResponseShort:
          type: object
          description: Bir dersin tek bir ders saati bilgisi.
          properties:
              id:
                type: integer
                description: Ders saatinin benzersiz ID'si.
                example: 10
              lesson_number:
                type: integer
                description: Dersin o günkü kaçıncı ders saati olduğunu belirtir (örn. 1, 2).
                example: 1
              day:
                type: string
                enum: ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
                description: Dersin yapıldığı gün.
                example: "TUESDAY"
              start_time:
                type: string
                pattern: "^[0-2][0-9]:[0-5][0-9]$"
                description: Ders başlangıç saati (HH:MM formatında).
                example: "10:00"
              end_time:
                type: string
                pattern: "^[0-2][0-9]:[0-5][0-9]$"
                description: Ders bitiş saati (HH:MM formatında).
                example: "11:50"
      CourseResponse:
          type: object
          description: Bir dersin tüm detaylarını içeren yanıt modeli.
          properties:
              id:
                  type: integer
                  description: Dersin benzersiz ID'si.
                  example: 1
              code:
                  type: string
                  description: Dersin kodu (örn. CS101). Benzersiz olmalı.
                  example: "CS101"
              name:
                  type: string
                  description: Dersin tam adı.
                  example: "Bilgisayar Bilimlerine Giriş"
              teacher_id:
                  type: integer
                  description: Dersi veren öğretmenin ID'si.
                  example: 1
              semester:
                  type: string
                  description: Dersin verildiği dönem (örn. 2024-Bahar).
                  example: "2024-Bahar"
              created_at:
                  type: string
                  format: date-time
                  description: Dersin oluşturulma zaman damgası.
                  example: "2024-01-10T10:00:00Z"
              updated_at:
                  type: string
                  format: date-time
                  description: Dersin son güncellenme zaman damgası.
                  example: "2024-01-10T10:00:00Z"
              teacher:
                  $ref: '#/definitions/TeacherResponseShort'
                  description: Dersi veren öğretmen detayları.
              lesson_times:
                  type: array
                  description: Derse ait tüm ders saatlerinin listesi.
                  items:
                      $ref: '#/definitions/LessonTimeResponseShort'
    """
    courses_list = data_service.read_data(COURSES_FILE)
    # Liste görünümü için öğretmen detaylarını ekle
    detailed_courses = []
    for course in courses_list:
        teacher = data_service.find_one(TEACHERS_FILE, id=course.get('teacher_id'))
        if teacher:
            user = data_service.find_one(USERS_FILE, id=teacher.get('user_id'))
            if user:
                user.pop('password_hash', None)
                teacher['user'] = user
            course['teacher'] = teacher
        # Liste görünümünü basit tutmak için ders saatlerini ekleme
        course['lesson_times'] = [] 
        detailed_courses.append(course)
        
    return jsonify(detailed_courses), 200

@courses_bp.route('/<int:course_id>', methods=['GET'])
@jwt_required() # Giriş yapmış herhangi bir kullanıcı detayları görebilir
def get_course(course_id):
    """
    Belirli bir dersin detaylarını (öğretmen ve ders saatleri dahil) getirir.
    ---    
    tags:
      - Dersler (Courses)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: course_id
        type: integer
        required: true
        description: Detayları alınacak dersin ID'si.
        example: 1
    responses:
      200:
        description: Ders detayları başarıyla alındı.
        schema:
          $ref: '#/definitions/CourseResponse' # Tanımı tekrar kullan
        examples:
          application/json:
            id: 1
            code: "CS101"
            name: "Bilgisayar Bilimlerine Giriş"
            teacher_id: 1
            semester: "2024-Bahar"
            created_at: "2024-01-10T10:00:00Z"
            updated_at: "2024-01-10T10:00:00Z"
            teacher:
              id: 1
              user_id: 2 
              department: "Bilgisayar Mühendisliği"
              title: "Profesör"
              user:
                  id: 2
                  email: "prof.ahmet@ornek.com"
                  first_name: "Ahmet"
                  last_name: "Yılmaz"
                  role: "TEACHER"
                  is_active: true
            lesson_times: 
              - id: 10
                lesson_number: 1
                day: "TUESDAY"
                start_time: "10:00"
                end_time: "11:50"
              - id: 11
                lesson_number: 2
                day: "THURSDAY"
                start_time: "14:00"
                end_time: "15:50"
      401:
        description: Yetkisiz. Geçerli bir token sağlanmadı.
      404:
        description: Belirtilen ID'ye sahip ders bulunamadı.
        examples:
           application/json: { "message": "Ders bulunamadı" }
    """
    course = data_service.find_one(COURSES_FILE, id=course_id)
    if not course:
        return jsonify({"message": "Ders bulunamadı"}), 404
    
    detailed_course = _get_course_details(course)
    return jsonify(detailed_course), 200

@courses_bp.route('/', methods=['POST'])
@teacher_required # Sadece Öğretmenler veya Adminler ders oluşturabilir
def create_course():
    """
    Yeni bir ders oluşturur (isteğe bağlı olarak ders saatleriyle birlikte).
    Giriş yapan kullanıcı Öğretmen ise `teacher_id` otomatik olarak atanır.
    Giriş yapan kullanıcı Admin ise `teacher_id` istek gövdesinde sağlanmalıdır.
    ---    
    tags:
      - Dersler (Courses)
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        description: Oluşturulacak dersin detayları.
        schema:
          $ref: '#/definitions/CourseCreate'
    responses:
      201:
        description: Ders başarıyla oluşturuldu. Oluşturulan dersin detaylarını döndürür.
        schema:
          $ref: '#/definitions/CourseResponse' # Tanımı tekrar kullan
      400:
        description: |-
          Geçersiz girdi verisi. Sebepleri:
          - Eksik veya geçersiz alanlar (Pydantic doğrulama hatası).
          - Belirtilen `code` ile başka bir ders zaten mevcut.
          - Admin kullanıcı `teacher_id` sağlamadı.
          - Sağlanan `teacher_id` geçersiz.
        examples:
           application/json (Validation): { "message": "Doğrulama Hatası", "errors": [{"field": "code", "message": "Bu değerin en az 3 karakter olduğundan emin olun"}] }
           application/json (Conflict): { "message": "Ders kodu 'CS101' zaten mevcut" }
           application/json (Admin Needs Teacher): { "message": "Doğrulama Hatası", "errors": [{"field": "teacher_id", "message": "Admin kullanıcılar için alan gerekli"}] }
      401:
        description: Yetkisiz. Geçerli bir token sağlanmadı veya token geçersiz.
      403:
        description: Yasak. Kullanıcı Öğretmen veya Admin değil.
      404:
        description: Admin tarafından belirtilen `teacher_id` ile eşleşen öğretmen bulunamadı veya giriş yapan öğretmenin profili bulunamadı (tutarlılık sorunu).
    definitions:
      LessonTimeCreate:
        type: object
        required:
          - lesson_number
          - day
          - start_time
          - end_time
        properties:
          lesson_number:
            type: integer
            description: Dersin o günkü kaçıncı ders saati (örn. 1, 2).
            example: 1
          day:
            type: string
            enum: ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
            description: Dersin yapılacağı gün.
            example: "TUESDAY"
          start_time:
            type: string
            pattern: "^[0-2][0-9]:[0-5][0-9]$"
            description: Ders başlangıç saati (HH:MM).
            example: "10:00"
          end_time:
            type: string
            pattern: "^[0-2][0-9]:[0-5][0-9]$"
            description: Ders bitiş saati (HH:MM).
            example: "11:50"
      CourseCreate:
        type: object
        required:
          - code
          - name
          - semester
        properties:
          code:
            type: string
            minLength: 3
            description: Dersin benzersiz kodu (örn. CS101).
            example: "HIST101"
          name:
            type: string
            minLength: 3
            description: Dersin tam adı.
            example: "Tarihe Giriş"
          semester:
            type: string
            description: Dersin verildiği dönem.
            example: "2024-Güz"
          teacher_id:
            type: integer
            description: Giriş yapan kullanıcı Admin ise zorunludur. Öğretmen ise bu alan yok sayılır.
            example: 5
          lesson_times:
            type: array
            description: Derse ait ders saatleri listesi (isteğe bağlı).
            items:
              $ref: '#/definitions/LessonTimeCreate'
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "Girdi verisi sağlanmadı"}), 400

    # Önce mevcut kullanıcı rolünü ve INT ID'sini al
    current_role, current_user_id = get_current_user_role_and_id() 
    if current_role is None or current_user_id is None:
         return jsonify({"message": "Geçersiz token kimliği veya kullanıcı bulunamadı"}), 401

    try:
        # Temel yapıyı ve alan türlerini doğrula
        course_data = CourseCreate(**json_data)
    except ValidationError as e:
        # Pydantic hatalarını JSON serileştirmesi için formatla 
        error_details = []
        for error in e.errors():
            field = ".".join(map(str, error.get('loc', [])))
            message = error.get('msg', 'Bilinmeyen hata')
            error_details.append({"field": field, "message": message})
        current_app.logger.warning(f"Ders oluşturma için doğrulama başarısız: {error_details}")
        return jsonify({"message": "Doğrulama Hatası", "errors": error_details}), 400

    # --- Doğrulamadan SONRA role dayalı teacher_id mantığı --- 
    teacher_id = None
    teacher_profile = None # Öğretmen profilini daha sonra kullanmak üzere sakla

    if current_role == "TEACHER":
        # Öğretmenler için kendi öğretmen profil ID'lerini bul
        teacher_profile = data_service.find_one(TEACHERS_FILE, user_id=current_user_id)
        if not teacher_profile:
             # Kayıt doğruysa idealde bu olmamalı
             current_app.logger.error(f"Giriş yapan öğretmen kullanıcı {current_user_id} için öğretmen profili bulunamadı.")
             return jsonify({"message": "Giriş yapan kullanıcı için öğretmen profili bulunamadı."}), 404 
        teacher_id = teacher_profile['id']
        # İstekteki teacher_id'nin (eğer sağlandıysa) yok sayıldığından veya eşleştiğinden emin ol
        # course_data.teacher_id = teacher_id 
    elif current_role == "ADMIN":
        # Adminler için teacher_id istekte sağlanmalı
        if not course_data.teacher_id:
            current_app.logger.warning("Admin, teacher_id sağlamadan ders oluşturmaya çalıştı.")
            return jsonify({"message": "Doğrulama Hatası", "errors": [{"field": "teacher_id", "message": "Admin kullanıcılar için alan gerekli"}]}), 400
        
        # Sağlanan teacher_id'yi doğrula
        teacher_profile = data_service.find_one(TEACHERS_FILE, id=course_data.teacher_id)
        if not teacher_profile:
             current_app.logger.warning(f"Admin, ders oluşturma için var olmayan teacher_id {course_data.teacher_id} belirtti.")
             return jsonify({"message": f"ID'si {course_data.teacher_id} olan öğretmen bulunamadı."}), 404
        teacher_id = course_data.teacher_id
    # 'else' gerekmez, çünkü @teacher_required decorator diğer rolleri halleder
    # --- Role dayalı mantık sonu --- 

    # Ders kodunun zaten var olup olmadığını kontrol et
    if data_service.find_one(COURSES_FILE, code=course_data.code):
        return jsonify({"message": f"Ders kodu '{course_data.code}' zaten mevcut"}), 400

    now = default_datetime()
    new_course_dict = {
        "code": course_data.code,
        "name": course_data.name,
        "teacher_id": teacher_id, # Doğrulanmış/belirlenmiş teacher_id'yi kullan
        "semester": course_data.semester,
        "created_at": now,
        "updated_at": now
    }

    created_course_dict = None
    created_lesson_times_ids = [] # Başarıyla oluşturulan ders saati ID'lerini takip et
    try:
        # Adım 1: Ana ders kaydını oluştur
        created_course_dict = data_service.add_item(COURSES_FILE, new_course_dict)
        course_id = created_course_dict['id']
        current_app.logger.info(f"{course_data.code} kodu için ana ders kaydı {course_id} oluşturuldu")

        # Adım 2: Ders saatlerini oluştur
        created_lesson_times = []
        if course_data.lesson_times:
            for i, lt_data in enumerate(course_data.lesson_times):
                current_app.logger.debug(f"{course_id} dersi için {i+1}. ders saati oluşturulmaya çalışılıyor")
                # Gerekirse ders saati verilerini burada açıkça doğrula (Pydantic temel tipleri halleder)
                new_lt_dict = lt_data.dict()
                new_lt_dict['course_id'] = course_id
                new_lt_dict['created_at'] = now
                new_lt_dict['updated_at'] = now
                try:
                    created_lt = data_service.add_item(LESSON_TIMES_FILE, new_lt_dict)
                    created_lesson_times.append(created_lt)
                    created_lesson_times_ids.append(created_lt['id']) 
                    current_app.logger.debug(f"{course_id} dersi için {created_lt['id']} ID'li ders saati başarıyla oluşturuldu")
                except Exception as lt_e:
                    current_app.logger.error(f"{course_id} dersi için {i+1}. ders saatini oluştururken hata: {lt_e}")
                    raise lt_e # Hatayı yukarı taşıyarak rollback tetikle
        
        # Adım 3: Başarılı yanıtı hazırla
        created_course_dict['lesson_times'] = created_lesson_times
        # Daha önce alınan teacher_profile'ı kullan
        if teacher_profile:
            # İlişkili kullanıcı bilgilerini ekle (şifre hariç)
            user = data_service.find_one(USERS_FILE, id=teacher_profile.get('user_id'))
            if user: user.pop('password_hash', None); teacher_profile['user'] = user
            created_course_dict['teacher'] = teacher_profile
        else: # Yukarıdaki mantık doğruysa öğretmen profili olmalı
             created_course_dict['teacher'] = None 

        current_app.logger.info(f"{course_id} dersi ve {len(created_lesson_times)} ders saati başarıyla oluşturuldu.")
        return jsonify(created_course_dict), 201

    except Exception as e:
        current_app.logger.error(f"{course_data.code} kodu için ders oluşturma sürecinde hata: {e}")
        # --- Geri Alma Mantığı --- 
        # Başarıyla oluşturulan ders saatlerini silmeye çalış
        if created_lesson_times_ids:
            current_app.logger.warning(f"Başarısız ders oluşturma (Ders Kodu: {course_data.code}) için ders saatleri geri alınıyor. Silinen ders saati ID'leri: {created_lesson_times_ids}")
            deleted_lt_count = 0
            for lt_id in created_lesson_times_ids:
                if data_service.delete_item(LESSON_TIMES_FILE, lt_id):
                    deleted_lt_count += 1
            current_app.logger.warning(f"Geri alma sırasında {deleted_lt_count} ders saati kaydı silindi.")
        
        # Eğer oluşturulduysa ana ders kaydını silmeye çalış
        if created_course_dict and 'id' in created_course_dict:
            course_id_to_delete = created_course_dict['id']
            current_app.logger.warning(f"Hata nedeniyle ana ders kaydı {course_id_to_delete} (Kod: {course_data.code}) geri alınıyor.")
            if data_service.delete_item(COURSES_FILE, course_id_to_delete):
                 current_app.logger.warning(f"Geri alma sırasında ana ders kaydı {course_id_to_delete} başarıyla silindi.")
            else:
                 current_app.logger.error(f"Geri alma sırasında ana ders kaydı {course_id_to_delete} silinemedi.")
       
        return jsonify({"message": "Ders oluşturma sırasında bir hata oluştu. Lütfen logları kontrol edin."}), 500


@courses_bp.route('/<int:course_id>', methods=['PUT'])
@self_or_admin_required(resource_id_param='course_id', resource_type='course') # Sadece dersin öğretmeni veya Admin güncelleyebilir
def update_course(course_id):
    """
    Bir dersin detaylarını (kod, ad, dönem, ders saatleri) günceller.
    Yalnızca dersin sahibi (öğretmen) veya Admin yetkilidir.
    `lesson_times` alanını güncellemek, ders için VAR OLAN TÜM ders saatlerini SİLER ve yenilerini ekler.
    ---    
    tags:
      - Dersler (Courses)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: course_id
        type: integer
        required: true
        description: Güncellenecek dersin ID'si.
        example: 1
      - in: body
        name: body
        required: true
        description: Güncellenecek ders bilgileri. `lesson_times` sağlanırsa mevcutları değiştirir.
        schema:
          $ref: '#/definitions/CourseUpdate'
    responses:
      200:
        description: Ders başarıyla güncellendi. Güncellenmiş ders detaylarını döndürür.
        schema:
          $ref: '#/definitions/CourseResponse' # Tanımı tekrar kullan
      400:
        description: |-
          Geçersiz girdi verisi. Sebepleri:
          - Eksik veya geçersiz alanlar (Pydantic doğrulama hatası).
          - Güncellenecek alan sağlanmadı.
          - Güncellenen `code` başka bir derse ait.
        examples:
           application/json (Validation): { "message": "Doğrulama Hatası", "errors": [{"field": "name", "message": "Bu değerin en az 3 karakter olduğundan emin olun"}] }
           application/json (Conflict): { "message": "Ders kodu 'CS102' zaten mevcut" }
           application/json (No Data): { "message": "Güncellenecek alan sağlanmadı" }
      401:
        description: Yetkisiz. Geçerli bir token sağlanmadı.
      403:
        description: Yasak. Kullanıcı bu dersi güncelleme yetkisine sahip değil.
      404:
        description: Belirtilen ID'ye sahip ders bulunamadı.
    definitions:
      CourseUpdate:
        type: object
        description: Ders güncelleme için istek modeli. Sadece değiştirilmek istenen alanlar gönderilmelidir.
        properties:
          code:
            type: string
            minLength: 3
            description: Dersin yeni benzersiz kodu.
            example: "CS101-UPDATED"
          name:
            type: string
            minLength: 3
            description: Dersin yeni tam adı.
            example: "Bilgisayar Bilimlerine Giriş (Güncellenmiş)"
          semester:
            type: string
            description: Dersin yeni dönemi.
            example: "2024-Bahar-Güncel"
          # teacher_id: # Öğretmen değiştirme genellikle ayrı bir admin işlemidir
          lesson_times:
            type: array
            description: Eğer sağlanırsa, dersin TÜM mevcut ders saatlerini bu liste ile DEĞİŞTİRİR. Sağlanmazsa ders saatleri değişmez.
            items:
              $ref: '#/definitions/LessonTimeCreate' # Tanımı tekrar kullan
            example: 
              - day: "MONDAY"
                start_time: "09:00"
                end_time: "10:50"
                lesson_number: 1
              - day: "WEDNESDAY"
                start_time: "13:00"
                end_time: "14:50"
                lesson_number: 2
    """
    course = data_service.find_one(COURSES_FILE, id=course_id)
    if not course:
        return jsonify({"message": "Ders bulunamadı"}), 404

    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "Girdi verisi sağlanmadı"}), 400

    try:
        update_data = CourseUpdate(**json_data)
    except ValidationError as e:
        # --- Pydantic hatalarını JSON serileştirmesi için formatla --- 
        error_details = []
        for error in e.errors():
            field = ".".join(map(str, error.get('loc', [])))
            message = error.get('msg', 'Bilinmeyen hata')
            error_details.append({"field": field, "message": message})
        current_app.logger.warning(f"{course_id} ID'li ders güncellemesi için doğrulama başarısız: {error_details}")
        return jsonify({"message": "Doğrulama Hatası", "errors": error_details}), 400
        # --- Formatlama sonu --- 

    updates = update_data.dict(exclude_unset=True) # Sadece gönderilen alanları al
    if not updates:
        return jsonify({"message": "Güncellenecek alan sağlanmadı"}), 400

    # Eğer kod güncelleniyorsa ders kodu çakışmasını kontrol et
    new_code = updates.get('code')
    if new_code and new_code != course.get('code'):
        existing_course = data_service.find_one(COURSES_FILE, code=new_code)
        if existing_course and existing_course.get('id') != course_id:
            return jsonify({"message": f"Ders kodu '{new_code}' zaten mevcut"}), 400

    now = default_datetime()
    updates['updated_at'] = now

    # Ders saatleri güncellemesini işle (mevcutları değiştir)
    new_lesson_times_data = updates.pop('lesson_times', None) # lesson_times'ı updates'ten çıkar, varsa alır
    updated_lesson_times = []

    try:
        # Önce temel ders bilgilerini güncelle
        updated_course_dict = data_service.update_item(COURSES_FILE, course_id, updates)
        if not updated_course_dict:
            return jsonify({"message": "Ders güncelleme başarısız"}), 500 # update_item başarısız oldu

        # Eğer yeni ders saatleri sağlandıysa, eskilerini sil ve yenilerini ekle
        if new_lesson_times_data is not None: # lesson_times isteğe dahil edilmişse (boş liste bile olsa)
            # Bu ders için mevcut ders saatlerini sil
            num_deleted = data_service.delete_many(LESSON_TIMES_FILE, course_id=course_id)
            current_app.logger.info(f"{course_id} ID'li ders için {num_deleted} eski ders saati silindi.")
            # Yeni ders saatlerini ekle
            for lt_model in new_lesson_times_data: # new_lesson_times_data Pydantic modellerinin listesi
                # HATA DÜZELTME: lt_model zaten dict olabilir, Pydantic modeli değil
                # Bu durumda dict() metodu bulunamaz
                
                # Eğer lt_model bir Pydantic model nesnesi ise
                if hasattr(lt_model, 'dict'):
                    new_lt_dict = lt_model.dict()
                else:
                    # Zaten bir dictionary ise direkt kullan
                    new_lt_dict = lt_model.copy()
                    
                new_lt_dict['course_id'] = course_id
                new_lt_dict['created_at'] = now # Yeni kayıtlar olarak değerlendir
                new_lt_dict['updated_at'] = now
                created_lt = data_service.add_item(LESSON_TIMES_FILE, new_lt_dict)
                updated_lesson_times.append(created_lt)
        else:
            # Eğer lesson_times güncellenmiyorsa, yanıt için mevcut olanları al
            updated_lesson_times = data_service.find_many(LESSON_TIMES_FILE, course_id=course_id)

        # Yanıtı hazırla
        updated_course_dict['lesson_times'] = updated_lesson_times
        # Öğretmen detaylarını ekle
        teacher = data_service.find_one(TEACHERS_FILE, id=updated_course_dict.get('teacher_id'))
        if teacher: 
            user = data_service.find_one(USERS_FILE, id=teacher.get('user_id'))
            if user: user.pop('password_hash', None); teacher['user'] = user
            updated_course_dict['teacher'] = teacher

        return jsonify(updated_course_dict), 200

    except Exception as e:
        current_app.logger.error(f"{course_id} ID'li ders güncellenirken hata: {e}")
        # Kısmi güncellemeler olduysa daha karmaşık geri alma gerekebilir
        return jsonify({"message": "Ders güncelleme sırasında bir hata oluştu."}), 500


@courses_bp.route('/<int:course_id>', methods=['DELETE'])
@self_or_admin_required(resource_id_param='course_id', resource_type='course') # Sadece dersin öğretmeni veya Admin silebilir
def delete_course(course_id):
    """
    Bir dersi ve ilişkili tüm verilerini (ders saatleri, kayıtlar, yoklamalar vb.) siler.
    Yalnızca dersin sahibi (öğretmen) veya Admin yetkilidir. DİKKAT: Bu işlem geri alınamaz!
    ---    
    tags:
      - Dersler (Courses)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: course_id
        type: integer
        required: true
        description: Silinecek dersin ID'si.
        example: 1
    responses:
      200:
        description: Ders ve ilişkili tüm veriler başarıyla silindi.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "1 ID'li ders ve ilişkili tüm veriler başarıyla silindi."
      401:
        description: Yetkisiz. Geçerli bir token sağlanmadı.
      403:
        description: Yasak. Kullanıcı bu dersi silme yetkisine sahip değil.
      404:
        description: Belirtilen ID'ye sahip ders bulunamadı.
      500:
        description: Silme işlemi sırasında bir sunucu hatası oluştu.
    """
    course = data_service.find_one(COURSES_FILE, id=course_id)
    if not course:
        return jsonify({"message": "Ders bulunamadı"}), 404

    try:
        # 1. Dersle ilişkili Ders Saatlerini sil
        num_lt_deleted = data_service.delete_many(LESSON_TIMES_FILE, course_id=course_id)
        current_app.logger.info(f"{course_id} ID'li ders için {num_lt_deleted} ders saati silindi.")

        # 2. Öğrenci Kayıtlarını (StudentCourse bağlantıları) sil
        num_enroll_deleted = data_service.delete_many(STUDENT_COURSE_FILE, course_id=course_id)
        current_app.logger.info(f"{course_id} ID'li ders için {num_enroll_deleted} kayıt silindi.")

        # 3. Yoklama Kayıtlarını (ve dolaylı/doğrudan detayları) sil
        #    Önce ders için tüm yoklama kayıtlarını bul
        attendance_records = data_service.find_many(ATTENDANCE_FILE, course_id=course_id)
        attendance_ids = [att['id'] for att in attendance_records]
        
        if attendance_ids:
            # Bu kayıtlara ait Yoklama Detaylarını sil
            num_details_deleted = 0
            for att_id in attendance_ids:
                # Belirli bir yoklama ID'sine ait tüm detayları sil
                num_details_deleted += data_service.delete_many(ATTENDANCE_DETAILS_FILE, attendance_id=att_id)
            current_app.logger.info(f"{course_id} ID'li ders için {num_details_deleted} yoklama detayı silindi.")

            # TODO: Varsa Emotion History kayıtlarını sil (attendance_id veya course_id ile)
            # num_emotion_deleted = data_service.delete_many(EMOTION_HISTORY_FILE, course_id=course_id) # veya attendance_id ile döngü
            # current_app.logger.info(f"{course_id} ID'li ders için {num_emotion_deleted} duygu geçmişi kaydı silindi.")
            
            # Ana Yoklama Kayıtlarını sil
            num_att_deleted = 0
            for att_id in attendance_ids:
                 if data_service.delete_item(ATTENDANCE_FILE, att_id):
                      num_att_deleted += 1
            # Alternatif: data_service.delete_many(ATTENDANCE_FILE, course_id=course_id) # Eğer destekliyorsa
            current_app.logger.info(f"{course_id} ID'li ders için {num_att_deleted} yoklama kaydı silindi.")
            
            # İsteğe bağlı: İlişkili yoklama fotoğraflarını dosya sisteminden sil
            for att_record in attendance_records:
                photo_path = att_record.get('photo_path')
                if photo_path:
                    # Tam yolu dikkatlice oluştur
                    # photo_path'ın /uploads/attendance/file.jpg gibi köke göre veya 
                    # sadece file.jpg gibi yüklendiği klasöre göre saklandığını varsayalım
                    try:
                        if photo_path.startswith('/'):
                            # Köke göre göreceli yol ise (örn. /uploads/...)
                            # current_app.root_path genellikle uygulama kök dizinidir
                            full_path = os.path.join(current_app.root_path, photo_path.lstrip('/')) 
                        else:
                            # Sadece dosya adı ise, yapılandırmadan klasörü al
                            full_path = os.path.join(current_app.config['ATTENDANCE_UPLOAD_FOLDER'], photo_path)
                             
                        if os.path.exists(full_path):
                            os.remove(full_path)
                            current_app.logger.info(f"Silinen yoklama fotoğrafı: {full_path}")
                    except OSError as e:
                        current_app.logger.error(f"Yoklama fotoğrafı {photo_path} silinirken hata: {e}")
                    except KeyError:
                         current_app.logger.error("ATTENDANCE_UPLOAD_FOLDER yapılandırması eksik, fotoğraf silinemedi.")


        # 4. Dersin Kendisini sil
        deleted_course = data_service.delete_item(COURSES_FILE, course_id)
        if not deleted_course:
             # Bu bir soruna işaret eder, belki loglanır, ancak işlem kısmen tamamlanmış olabilir
             current_app.logger.error(f"İlişkili veriler silindikten sonra ana ders kaydı {course_id} silinemedi.")
             # Hata mesajı döndür ama 500 vermek daha uygun olabilir
             return jsonify({"message": "Ders kaydı silme başarısız oldu, ancak ilişkili veriler silinmiş olabilir."}), 500

        return jsonify({"message": f"{course_id} ID'li ders ve ilişkili tüm veriler başarıyla silindi."}), 200

    except Exception as e:
        current_app.logger.error(f"{course_id} ID'li ders ve ilişkili veriler silinirken hata: {e}")
        # JSON dosyalarıyla burada geri alma zordur. 
        return jsonify({"message": "Ders silme sırasında bir hata oluştu."}), 500


@courses_bp.route('/<int:course_id>/students', methods=['GET'])
@teacher_required # Sadece Öğretmen veya Admin kayıtlı öğrencileri görebilir
def get_course_students(course_id):
    """
    Belirli bir derse kayıtlı öğrencilerin listesini getirir.
    ---    
    tags:
      - Dersler (Courses)
      - Öğrenciler (Students)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: course_id
        type: integer
        required: true
        description: Öğrencileri listelenecek dersin ID'si.
        example: 1
    responses:
      200:
        description: Derse kayıtlı öğrencilerin listesi (detaylı).
        schema:
          type: array
          items:
            $ref: '#/definitions/StudentResponse' # StudentResponse tanımını tekrar kullan
        examples:
          application/json:
            - id: 5 # Öğrenci ID'si
              user_id: 10 
              student_number: "S12345"
              department: "Bilgisayar Mühendisliği"
              face_photo_url: "/uploads/faces/student_5_....jpg" 
              created_at: "2024-01-15T14:00:00Z"
              updated_at: "2024-01-16T09:30:00Z"
              user:
                id: 10
                email: "ayse.kaya@ornek.com"
                first_name: "Ayşe"
                last_name: "Kaya"
                role: "STUDENT"
                is_active: true
            # ... (diğer öğrenciler) ...
      401:
        description: Yetkisiz. Geçerli bir token sağlanmadı.
      403:
        description: Yasak. Kullanıcı bu bilgiyi görme yetkisine sahip değil.
      404:
        description: Belirtilen ID'ye sahip ders bulunamadı.
    """
    course = data_service.find_one(COURSES_FILE, id=course_id)
    if not course:
        return jsonify({"message": "Ders bulunamadı"}), 404

    enrollments = data_service.find_many(STUDENT_COURSE_FILE, course_id=course_id)
    student_ids = [enrollment['student_id'] for enrollment in enrollments]

    if not student_ids:
        return jsonify([]), 200 # Boş liste döndür

    all_students = data_service.read_data(STUDENTS_FILE)
    enrolled_students_details = []
    # StudentResponse tanımını global olarak ekle (varsa)
    # users.py veya schemas/user.py içinde tanımlanmış olmalı
    # Swagger UI'ın doğru modeli göstermesi için bu gerekli
    from app.schemas.user import StudentResponse as PydanticStudentResponse 
    from app.routes.students import _get_student_with_user # Yardımcı fonksiyonu kullan

    for student_dict in all_students:
        if student_dict['id'] in student_ids:
            detailed_student = _get_student_with_user(student_dict.copy()) # Orijinali bozmamak için kopya kullan
            if detailed_student:
                 # Pydantic modeline dönüştürerek şemaya uygunluğu garanti et (isteğe bağlı)
                 try:
                    # validated_student = PydanticStudentResponse(**detailed_student).dict()
                    enrolled_students_details.append(detailed_student) # Şimdilik dict olarak ekle
                 except ValidationError as p_err:
                     current_app.logger.error(f"Öğrenci {student_dict['id']} verisi StudentResponse şemasına uymuyor: {p_err}")
                     # Hatalı veriyi atla veya logla
            
    return jsonify(enrolled_students_details), 200

@courses_bp.route('/<int:course_id>/students', methods=['POST'])
@teacher_required # Sadece Öğretmen veya Admin öğrenci ekleyebilir
def add_student_to_course(course_id):
    """
    Bir öğrenciyi belirli bir derse kaydeder.
    ---    
    tags:
      - Dersler (Courses)
      - Öğrenciler (Students)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: course_id
        type: integer
        required: true
        description: Öğrencinin kaydedileceği dersin ID'si.
        example: 1
      - in: body
        name: body
        required: true
        description: Kaydedilecek öğrencinin ID'sini içeren veri.
        schema:
          $ref: '#/definitions/StudentCourseLink'
    responses:
      201:
        description: Öğrenci derse başarıyla kaydedildi. Oluşturulan kayıt bağlantısını döndürür.
        schema:
          $ref: '#/definitions/StudentCourseResponse' # Oluşturulan bağlantıyı gösteren yanıt
        examples:
          application/json:
            id: 50 # StudentCourse kaydının ID'si
            student_id: 5
            course_id: 1
            created_at: "2024-01-18T16:00:00Z" 
            # updated_at eklenebilir
      400:
        description: |-
          Geçersiz girdi veya işlem hatası. Sebepleri:
          - İstek gövdesi eksik veya geçersiz.
          - Öğrenci zaten bu derse kayıtlı.
          - Veri ekleme sırasında hata oluştu (örn. ID çakışması - olmamalı).
        examples:
           application/json (Validation): { "message": "Doğrulama Hatası", "errors": [{"field": "student_id", "message": "alan gerekli"}] }
           application/json (Conflict): { "message": "Öğrenci 5 zaten 1 ID'li derse kayıtlı" }
      401:
        description: Yetkisiz. Geçerli bir token sağlanmadı.
      403:
        description: Yasak. Kullanıcı bu işlemi yapmaya yetkili değil.
      404:
        description: Belirtilen ID'ye sahip Ders veya Öğrenci bulunamadı.
        examples:
           application/json (Course): { "message": "Ders bulunamadı" }
           application/json (Student): { "message": "ID'si 5 olan öğrenci bulunamadı" }
    definitions:
      StudentCourseLink:
        type: object
        required:
          - student_id
        properties:
          student_id:
            type: integer
            description: Derse kaydedilecek öğrencinin ID'si.
            example: 5
      StudentCourseResponse: # Eğer global olarak tanımlı değilse tanımla
        type: object
        description: Öğrenci ve ders arasındaki başarılı kayıt bağlantısı.
        properties:
          id: 
            type: integer
            description: Oluşturulan kayıt bağlantısının ID'si.
            example: 50
          student_id:
            type: integer
            description: Kaydedilen öğrencinin ID'si.
            example: 5
          course_id:
            type: integer
            description: Öğrencinin kaydedildiği dersin ID'si.
            example: 1
          # created_at/updated_at eklenebilir
          created_at:
            type: string
            format: date-time
            example: "2024-01-18T16:00:00Z" 
    """
    course = data_service.find_one(COURSES_FILE, id=course_id)
    if not course:
        return jsonify({"message": "Ders bulunamadı"}), 404

    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "Girdi verisi sağlanmadı"}), 400

    try:
        link_data = StudentCourseLink(**json_data)
        student_id = link_data.student_id
    except ValidationError as e:
         # Pydantic hatalarını formatla
         error_details = [{"field": ".".join(map(str, err.get('loc',[]))), "message": err.get('msg','')} for err in e.errors()]
         return jsonify({"message": "Doğrulama Hatası", "errors": error_details}), 400

    # Öğrencinin var olup olmadığını kontrol et
    student = data_service.find_one(STUDENTS_FILE, id=student_id)
    if not student:
        return jsonify({"message": f"ID'si {student_id} olan öğrenci bulunamadı"}), 404

    # Öğrencinin zaten kayıtlı olup olmadığını kontrol et
    existing_enrollment = data_service.find_one(STUDENT_COURSE_FILE, course_id=course_id, student_id=student_id)
    if existing_enrollment:
        return jsonify({"message": f"Öğrenci {student_id} zaten {course_id} ID'li derse kayıtlı"}), 400

    # Kayıt bağlantısını oluştur
    now = default_datetime()
    enrollment_data = {
        "student_id": student_id,
        "course_id": course_id,
        "created_at": now, # Zaman damgası ekle
        "updated_at": now
    }

    try:
        # Kayıt için otomatik ID atamasına izin vererek öğeyi ekle
        created_enrollment = data_service.add_item(STUDENT_COURSE_FILE, enrollment_data) # assign_id=True varsayılan
        # Yanıta ID'yi ve diğer alanları dahil et (created_enrollment zaten dict)
        return jsonify(created_enrollment), 201
    except ValueError as ve: # add_item'dan gelebilecek potansiyel hataları yakala
         current_app.logger.error(f"Kayıt eklenirken hata: {ve}")
         return jsonify({"message": str(ve)}), 400
    except Exception as e:
        current_app.logger.error(f"{student_id} ID'li öğrenci {course_id} ID'li derse kaydedilirken hata: {e}")
        return jsonify({"message": "Kayıt sırasında bir hata oluştu."}), 500


@courses_bp.route('/<int:course_id>/students/<int:student_id>', methods=['DELETE'])
@teacher_required # Sadece Öğretmen veya Admin öğrenciyi silebilir
def remove_student_from_course(course_id, student_id):
    """
    Bir öğrencinin belirli bir dersteki kaydını siler.
    ---    
    tags:
      - Dersler (Courses)
      - Öğrenciler (Students)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: course_id
        type: integer
        required: true
        description: Öğrencinin kaydının silineceği dersin ID'si.
        example: 1
      - in: path
        name: student_id
        type: integer
        required: true
        description: Dersten kaydı silinecek öğrencinin ID'si.
        example: 5
    responses:
      200:
        description: Öğrenci dersten başarıyla çıkarıldı.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Öğrenci 5, ders 1'den başarıyla çıkarıldı."
      401:
        description: Yetkisiz. Geçerli bir token sağlanmadı.
      403:
        description: Yasak. Kullanıcı bu işlemi yapmaya yetkili değil.
      404:
        description: Ders, Öğrenci veya Öğrencinin dersteki Kaydı bulunamadı.
        examples:
           application/json (Course): { "message": "Ders bulunamadı" }
           application/json (Student): { "message": "Öğrenci bulunamadı" }
           application/json (Enrollment): { "message": "Öğrenci 5 için ders 1 kaydı bulunamadı." }
    """
    # Ders ve öğrencinin varlığını kontrol et (isteğe bağlı, delete_many eşleşmeyeni atlar)
    course = data_service.find_one(COURSES_FILE, id=course_id)
    if not course: return jsonify({"message": "Ders bulunamadı"}), 404
    student = data_service.find_one(STUDENTS_FILE, id=student_id)
    if not student: return jsonify({"message": "Öğrenci bulunamadı"}), 404
    
    # Belirli kayıt bağlantısını silmeye çalış
    num_deleted = data_service.delete_many(STUDENT_COURSE_FILE, course_id=course_id, student_id=student_id)

    if num_deleted > 0:
        return jsonify({"message": f"Öğrenci {student_id}, ders {course_id}'den başarıyla çıkarıldı."}), 200
    else:
        # Bu, kaydın zaten var olmadığı anlamına gelir
        return jsonify({"message": f"Öğrenci {student_id} için ders {course_id} kaydı bulunamadı."}), 404


@courses_bp.route('/<int:course_id>/attendance', methods=['GET'])
@self_or_admin_required(resource_id_param='course_id', resource_type='course') # Sadece dersin öğretmeni veya admin
def get_course_attendance_records(course_id):
    """
    Belirli bir ders için tüm ana yoklama kayıtlarını getirir.
    Liste görünümünde kısalık için varsayılan olarak detayları (öğrenci listesi) içermez.
    ---    
    tags:
      - Dersler (Courses)
      - Yoklama (Attendance)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: course_id
        type: integer
        required: true
        description: Yoklama kayıtları alınacak dersin ID'si.
        example: 1
    responses:
      200:
        description: Ders için yoklama kayıtlarının listesi (özet görünüm).
        schema:
          type: array
          items:
            # Burada basitleştirilmiş bir AttendanceResponse daha iyi olabilir
            $ref: '#/definitions/AttendanceResponse' # Attendance şemasını kullan
        examples:
          application/json:
            - id: 101
              course_id: 1
              date: "2024-03-05"
              lesson_number: 1
              type: "FACE"
              photo_path: "/uploads/attendance/attendance_1_...jpg"
              total_students: 25
              recognized_students: 23
              unrecognized_students: 2
              emotion_statistics: null
              created_by: 2 # Öğretmen kullanıcı ID'si
              created_at: "2024-03-05T10:05:00Z"
              # details: [] # Bu endpointte detaylar genellikle dışarıda bırakılır
            # ... (diğer yoklama kayıtları) ...
      401:
        description: Yetkisiz. Geçerli bir token sağlanmadı.
      403:
        description: Yasak. Kullanıcı bu kayıtları görme yetkisine sahip değil.
      404:
        description: Belirtilen ID'ye sahip ders bulunamadı.
    definitions:
        # Eğer global olarak tanımlı değilse AttendanceResponse tanımını ekle
        # Bu tanım attendance.py içinde de olabilir, tutarlılık önemli
        AttendanceResponse: 
            type: object
            description: Bir yoklama kaydının detayları (özet veya tam).
            properties:
                id:
                  type: integer
                  description: Yoklama kaydının benzersiz ID'si.
                  example: 101
                course_id:
                  type: integer
                  description: Yoklamanın ait olduğu dersin ID'si.
                  example: 1
                date:
                  type: string
                  format: date
                  description: Yoklamanın alındığı tarih (YYYY-AA-GG).
                  example: "2024-03-05"
                lesson_number:
                  type: integer
                  description: Yoklamanın ilgili dersin o günkü kaçıncı dersi olduğu.
                  example: 1
                type:
                  type: string
                  enum: ["FACE", "EMOTION", "FACE_EMOTION", "MANUAL"] # MANUEL eklenebilir
                  description: Yoklamanın türü (Yüz tanıma, Duygu analizi vb.).
                  example: "FACE"
                photo_path:
                  type: string
                  nullable: true
                  description: Yoklama için kullanılan fotoğrafın sunucudaki göreceli yolu (varsa).
                  example: "/uploads/attendance/attendance_1_20240305_1_....jpg"
                total_students:
                  type: integer
                  nullable: true
                  description: Yoklama anında derse kayıtlı toplam öğrenci sayısı.
                  example: 25
                recognized_students:
                  type: integer
                  nullable: true
                  description: Yüz tanıma ile tanınan (genellikle 'VAR' kabul edilen) öğrenci sayısı. Manuel güncellemelerle değişebilir.
                  example: 23
                unrecognized_students:
                  type: integer
                  nullable: true
                  description: Derse kayıtlı olup yoklamada 'VAR' olarak işaretlenmeyen öğrenci sayısı (genellikle 'YOK' kabul edilir). Manuel güncellemelerle değişebilir.
                  example: 2
                emotion_statistics:
                  type: object
                  nullable: true
                  description: Yoklama sırasındaki genel duygu istatistikleri (eğer toplandıysa).
                  example: {"HAPPY": 15, "NEUTRAL": 7, "SAD": 1}
                created_by:
                  type: integer
                  description: Yoklamayı oluşturan kullanıcının (öğretmen/admin) ID'si.
                  example: 2
                created_at:
                  type: string
                  format: date-time
                  description: Yoklama kaydının oluşturulma zaman damgası.
                  example: "2024-03-05T10:05:00Z"
                # details: # Detay listesi, bu özel endpoint için genellikle dışarıda bırakılır
                #   type: array
                #   items:
                #       $ref: '#/definitions/AttendanceDetailResponse'
                # course: # Ders detayları, ana kaynak olduğu için dışarıda bırakılır
                #   type: object

    """
    course = data_service.find_one(COURSES_FILE, id=course_id)
    if not course:
        return jsonify({"message": "Ders bulunamadı"}), 404

    # Yetkilendirme decorator tarafından halledilir

    attendance_records = data_service.find_many(ATTENDANCE_FILE, course_id=course_id)
    # İsteğe bağlı: Tarih/ders numarasına göre sırala
    attendance_records.sort(key=lambda x: (x.get('date',''), x.get('lesson_number', 0)))
    
    # İsteğe bağlı: Yanıtı şekillendirmek için Pydantic modeli kullan (örn. detayları hariç tut)
    # response_models = [AttendanceResponse(**rec).dict(exclude={'details'}) for rec in attendance_records]
    # return jsonify(response_models), 200

    return jsonify(attendance_records), 200 # Şimdilik ham listeyi döndür 