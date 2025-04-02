from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from werkzeug.security import generate_password_hash
import datetime

from app.services import data_service
from app.schemas.user import TeacherResponse, TeacherUpdate, UserCreate, UserResponse, TeacherCreate # Gerekli şemaları import et
from app.schemas.course import CourseResponse # CourseResponse'u import et
from app.models.user import Teacher, User, default_datetime
from app.utils.auth import admin_required, teacher_required, self_or_admin_required
# Ders saati bilgilerini çekmek için yardımcı fonksiyonu import edelim
from app.routes.courses import _get_course_details, LESSON_TIMES_FILE

teachers_bp = Blueprint('teachers_bp', __name__)

USERS_FILE = 'users.json'
TEACHERS_FILE = 'teachers.json'
COURSES_FILE = 'courses.json'

def _get_teacher_with_user(teacher_dict):
    """Yardımcı fonksiyon: Kullanıcı detaylarını alır ve öğretmen detaylarıyla birleştirir."""
    if not teacher_dict:
        return None
    user = data_service.find_one(USERS_FILE, id=teacher_dict.get('user_id'))
    if user:
        # Şifre hash'inin dahil edilmediğinden emin olun
        user.pop('password_hash', None)
        teacher_dict['user'] = user
    return teacher_dict

@teachers_bp.route('/', methods=['GET'])
@teacher_required # Admin ve Öğretmenlerin listeyi görmesine izin ver
def get_teachers():
    """
    Tüm öğretmenlerin listesini kullanıcı detaylarıyla birlikte getirir.
    ---    
    tags:
      - Öğretmenler (Teachers)
    security:
      - Bearer: []
    responses:
      200:
        description: Öğretmenlerin listesi.
        schema:
          type: array
          items:
            $ref: '#/definitions/TeacherResponse' 
        examples:
          application/json:
            - id: 1
              user_id: 2
              department: "Bilgisayar Mühendisliği"
              title: "Prof. Dr."
              created_at: "2024-01-10T09:00:00Z"
              updated_at: "2024-02-20T11:30:00Z"
              user:
                id: 2
                email: "prof.ahmet@ornek.edu"
                first_name: "Ahmet"
                last_name: "Yılmaz"
                role: "TEACHER"
                is_active: true
            - id: 4
              user_id: 7
              department: "Elektrik Mühendisliği"
              title: "Doç. Dr."
              created_at: "2024-01-12T15:00:00Z"
              updated_at: "2024-01-12T15:00:00Z"
              user:
                id: 7
                email: "doc.zeynep@ornek.edu"
                first_name: "Zeynep"
                last_name: "Demir"
                role: "TEACHER"
                is_active: true
      401:
        description: Yetkisiz. Geçerli token sağlanmadı.
      403:
        description: Yasak. Kullanıcı Admin veya Öğretmen değil.
    definitions:
      # TeacherResponse ve iç içe UserResponseShort tanımları (global değilse)
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
                example: "prof.ahmet@ornek.edu"
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
      TeacherResponse:
          type: object
          description: Bir öğretmenin detaylı bilgilerini içeren yanıt modeli.
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
                  description: Öğretmenin bağlı olduğu bölüm.
                  example: "Bilgisayar Mühendisliği"
              title:
                  type: string
                  description: Öğretmenin unvanı.
                  example: "Prof. Dr."
              created_at:
                  type: string
                  format: date-time
                  description: Öğretmen profilinin oluşturulma zaman damgası.
                  example: "2024-01-10T09:00:00Z"
              updated_at:
                  type: string
                  format: date-time
                  description: Öğretmen profilinin son güncellenme zaman damgası.
                  example: "2024-02-20T11:30:00Z"
              user:
                  $ref: '#/definitions/UserResponseShort'
                  description: Öğretmene ait kullanıcı hesabı detayları.
    """
    teachers_list = data_service.read_data(TEACHERS_FILE)
    detailed_teachers = [_get_teacher_with_user(t.copy()) for t in teachers_list] # Kopya kullan
    # Tutarlı yanıt yapısı için Pydantic kullan (isteğe bağlı ama iyi)
    # result = [TeacherResponse.from_orm(Teacher(**t)).dict() for t in detailed_teachers if t]
    return jsonify(detailed_teachers), 200

@teachers_bp.route('/<int:teacher_id>', methods=['GET'])
@teacher_required # Admin ve Öğretmenlerin detayları görmesine izin ver
def get_teacher(teacher_id):
    """
    Belirli bir öğretmenin detaylarını getirir.
    ---    
    tags:
      - Öğretmenler (Teachers)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: teacher_id
        type: integer
        required: true
        description: Detayları alınacak öğretmenin ID'si.
        example: 1
    responses:
      200:
        description: Öğretmen detayları başarıyla alındı.
        schema:
          $ref: '#/definitions/TeacherResponse' # Tanımı tekrar kullan
        examples:
          application/json:
            id: 1
            user_id: 2
            department: "Bilgisayar Mühendisliği"
            title: "Prof. Dr."
            created_at: "2024-01-10T09:00:00Z"
            updated_at: "2024-02-20T11:30:00Z"
            user:
              id: 2
              email: "prof.ahmet@ornek.edu"
              first_name: "Ahmet"
              last_name: "Yılmaz"
              role: "TEACHER"
              is_active: true
      401:
        description: Yetkisiz. Geçerli token sağlanmadı.
      403:
        description: Yasak. Kullanıcı bu öğretmenin bilgilerini görme yetkisine sahip değil.
      404:
        description: Belirtilen ID'ye sahip öğretmen bulunamadı.
        examples:
          application/json: { "message": "Öğretmen bulunamadı" }
    """
    teacher = data_service.find_one(TEACHERS_FILE, id=teacher_id)
    if not teacher:
        return jsonify({"message": "Öğretmen bulunamadı"}), 404
    
    detailed_teacher = _get_teacher_with_user(teacher.copy()) # Kopya kullan
    # result = TeacherResponse.from_orm(Teacher(**detailed_teacher)).dict()
    return jsonify(detailed_teacher), 200

# POST / endpoint ile öğretmen oluşturma /api/auth/register altında
# role="TEACHER" ile yapılır.

@teachers_bp.route('/<int:teacher_id>', methods=['PUT'])
@self_or_admin_required(resource_id_param='teacher_id', resource_type='teacher') # Öğretmenin kendisi veya Admin
def update_teacher(teacher_id):
    """
    Bir öğretmenin profilini (bölüm, unvan) günceller. Sadece Admin veya öğretmenin kendisi yetkilidir.
    Kullanıcı bilgilerini (ad, soyad vb.) güncellemek için /api/auth/me (PUT) endpoint'i kullanılmalıdır.
    ---    
    tags:
      - Öğretmenler (Teachers)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: teacher_id
        type: integer
        required: true
        description: Güncellenecek öğretmenin ID'si.
        example: 1
      - in: body
        name: body
        required: true
        description: Güncellenecek öğretmen profili bilgileri.
        schema:
          $ref: '#/definitions/TeacherUpdate'
    responses:
      200:
        description: Öğretmen profili başarıyla güncellendi. Güncellenmiş öğretmen detaylarını döndürür.
        schema:
          $ref: '#/definitions/TeacherResponse' # Tanımı tekrar kullan
        examples:
          application/json:
            id: 1
            user_id: 2
            department: "Yazılım Mühendisliği"
            title: "Doç. Dr." # Unvan güncellendi varsayalım
            created_at: "2024-01-10T09:00:00Z"
            updated_at: "2024-03-11T10:00:00Z" # Yeni güncelleme zamanı
            user:
              id: 2
              email: "prof.ahmet@ornek.edu"
              first_name: "Ahmet"
              last_name: "Yılmaz"
              role: "TEACHER"
              is_active: true
      400:
        description: |-
          Geçersiz girdi verisi veya işlem hatası. Sebepleri:
          - İstek gövdesi eksik veya geçersiz.
          - Güncellenecek alan sağlanmadı.
        examples:
          application/json (Validation): { "message": "Doğrulama Hatası", "errors": [{"field": "title", "message": "Bu alan boş olamaz"}] }
          application/json (No Data): { "message": "Güncellenecek alan sağlanmadı" }
      401:
        description: Yetkisiz. Geçerli token sağlanmadı.
      403:
        description: Yasak. Kullanıcı bu işlemi yapmaya yetkili değil (Admin veya kendisi değil).
      404:
        description: Belirtilen ID'ye sahip öğretmen bulunamadı.
    definitions:
      TeacherUpdate:
        type: object
        description: Öğretmen profili güncelleme için istek gövdesi modeli.
        properties:
          department:
            type: string
            description: Öğretmenin yeni bölümü.
            example: "Yazılım Mühendisliği"
          title:
            type: string
            description: Öğretmenin yeni unvanı.
            example: "Doç. Dr."
    """
    teacher = data_service.find_one(TEACHERS_FILE, id=teacher_id)
    if not teacher:
        return jsonify({"message": "Öğretmen bulunamadı"}), 404

    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "Girdi verisi sağlanmadı"}), 400

    try:
        update_data = TeacherUpdate(**json_data)
    except ValidationError as e:
        # --- Pydantic hatalarını JSON serileştirmesi için formatla --- 
        error_details = []
        for error in e.errors():
            field = ".".join(map(str, error.get('loc', [])))
            message = error.get('msg', 'Bilinmeyen hata')
            error_details.append({"field": field, "message": message})
        current_app.logger.warning(f"{teacher_id} ID'li öğretmen güncellemesi için doğrulama başarısız: {error_details}")
        return jsonify({"message": "Doğrulama Hatası", "errors": error_details}), 400
        # --- Formatlama sonu --- 

    updates = update_data.dict(exclude_unset=True) # Sadece gönderilen alanları al
    if not updates:
        return jsonify({"message": "Güncellenecek alan sağlanmadı"}), 400

    # Güncelleme için zaman damgası ekle
    updates['updated_at'] = default_datetime()

    updated_teacher_dict = data_service.update_item(TEACHERS_FILE, teacher_id, updates)

    if not updated_teacher_dict:
        # Bu durum, update_item içindeki bir yarış durumunu veya başka bir hatayı gösterebilir
        return jsonify({"message": "Öğretmen güncelleme başarısız"}), 500

    detailed_teacher = _get_teacher_with_user(updated_teacher_dict.copy()) # Kopya kullan
    # result = TeacherResponse.from_orm(Teacher(**detailed_teacher)).dict()
    return jsonify(detailed_teacher), 200

@teachers_bp.route('/<int:teacher_id>', methods=['DELETE'])
@admin_required # Sadece Admin öğretmen silebilir
def delete_teacher(teacher_id):
    """
    Bir öğretmeni ve ilişkili kullanıcı hesabını siler. (Sadece Admin yetkilidir)
    DİKKAT: Bu işlem, öğretmenin sorumlu olduğu dersler varsa başarısız olur. Önce derslerin başka bir öğretmene atanması gerekir.
    ---    
    tags:
      - Öğretmenler (Teachers)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: teacher_id
        type: integer
        required: true
        description: Silinecek öğretmenin ID'si.
        example: 4
    responses:
      200:
        description: Öğretmen ve ilişkili kullanıcı hesabı başarıyla silindi.
        schema:
            type: object
            properties:
                message:
                    type: string
                    example: "Öğretmen 4 ve ilişkili kullanıcı 7 başarıyla silindi"
      400:
        description: Öğretmen, sorumlu olduğu dersler bulunduğu için silinemedi.
        schema:
            type: object
            properties:
                message:
                    type: string
                    example: "Sorumlu olduğu dersler olan öğretmen silinemez. Önce dersleri yeniden atayın."
      401:
        description: Yetkisiz. Geçerli token sağlanmadı.
      403:
        description: Yasak. Kullanıcı Admin değil.
      404:
        description: Belirtilen ID'ye sahip öğretmen bulunamadı.
      500:
        description: Silme işlemi sırasında bir sunucu hatası oluştu.
    """
    teacher = data_service.find_one(TEACHERS_FILE, id=teacher_id)
    if not teacher:
        return jsonify({"message": "Öğretmen bulunamadı"}), 404

    user_id = teacher.get('user_id')

    # Öğretmenin sorumlu olduğu ders var mı kontrol et
    assigned_courses = data_service.find_many(COURSES_FILE, teacher_id=teacher_id)
    if assigned_courses:
        return jsonify({"message": "Sorumlu olduğu dersler olan öğretmen silinemez. Önce dersleri yeniden atayın."}), 400

    try:
        # Önce öğretmen profilini sil
        deleted_teacher = data_service.delete_item(TEACHERS_FILE, teacher_id)
        if not deleted_teacher:
             # Eğer find_one başarılıysa burası olmamalı ama loglamak iyi olabilir
             current_app.logger.error(f"Öğretmen profili {teacher_id} silinemedi (önce bulunmuştu).")
             return jsonify({"message": "Öğretmen profili silinemedi"}), 500 

        # Sonra ilişkili kullanıcı hesabını sil
        if user_id:
            deleted_user = data_service.delete_item(USERS_FILE, user_id)
            if not deleted_user:
                # Bu tutarsızlığı logla - öğretmen profili silindi ama kullanıcı bulunamadı/silinemedi
                current_app.logger.warning(f"Öğretmen profili {teacher_id} silindi, ancak ilişkili kullanıcı {user_id} silinemedi.")
                # Öğretmen silme işlemi başarılı olsa da kullanıcı sorununu belirt
                return jsonify({"message": f"Öğretmen profili {teacher_id} silindi, ancak ilişkili kullanıcı {user_id} kalmış olabilir."}), 200

        return jsonify({"message": f"Öğretmen {teacher_id} ve ilişkili kullanıcı {user_id} başarıyla silindi"}), 200

    except Exception as e:
        current_app.logger.error(f"Öğretmen {teacher_id} veya kullanıcı {user_id} silinirken hata: {e}")
        # Potansiyel geri alma gerekli mi? İstenen atomisiteye bağlı.
        return jsonify({"message": "Silme sırasında bir hata oluştu."}), 500


@teachers_bp.route('/<int:teacher_id>/courses', methods=['GET'])
@self_or_admin_required(resource_id_param='teacher_id', resource_type='teacher') # Öğretmenin kendisi veya Admin
def get_teacher_courses(teacher_id):
    """
    Belirli bir öğretmenin verdiği tüm dersleri, ders saati bilgileriyle birlikte getirir. (Admin veya öğretmenin kendisi).
    ---    
    tags:
      - Öğretmenler (Teachers)
      - Dersler (Courses)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: teacher_id
        type: integer
        required: true
        description: Dersleri listelenecek öğretmenin ID'si.
        example: 1
    responses:
      200:
        description: Öğretmenin verdiği derslerin listesi (ders saati bilgileri dahil).
        schema:
          type: array
          items:
            $ref: '#/definitions/CourseResponse' # CourseResponse'un tanımlı olduğunu varsayıyoruz
        examples:
          application/json:
            - id: 1
              code: "CS101"
              name: "Bilgisayar Bilimlerine Giriş"
              teacher_id: 1
              semester: "2024-Bahar"
              created_at: "2024-01-10T10:00:00Z"
              updated_at: "2024-01-10T10:00:00Z"
              lesson_times: [
                {
                  "id": 10,
                  "lesson_number": 1,
                  "day": "TUESDAY",
                  "start_time": "10:00",
                  "end_time": "11:50"
                },
                {
                  "id": 11,
                  "lesson_number": 2,
                  "day": "THURSDAY", 
                  "start_time": "14:00",
                  "end_time": "15:50"
                }
              ]
            - id: 5
              code: "CS305"
              name: "Veri Yapıları"
              teacher_id: 1
              semester: "2024-Bahar"
              created_at: "2024-01-15T11:00:00Z"
              updated_at: "2024-01-15T11:00:00Z"
              lesson_times: [
                {
                  "id": 15,
                  "lesson_number": 1,
                  "day": "MONDAY",
                  "start_time": "13:00",
                  "end_time": "14:50"
                }
              ]
      401:
        description: Yetkisiz. Geçerli token sağlanmadı.
      403:
        description: Yasak. Kullanıcı bu bilgilere erişim yetkisine sahip değil.
      404:
        description: Belirtilen ID'ye sahip öğretmen bulunamadı.
    definitions:
        CourseResponse: # Global olarak mevcut değilse tanımla
            type: object
            description: Bir dersin detaylarını içeren yanıt modeli.
            properties:
                id:
                    type: integer
                    description: Dersin benzersiz ID'si.
                    example: 1
                code:
                    type: string
                    description: Dersin kodu.
                    example: "CS101"
                name:
                    type: string
                    description: Dersin adı.
                    example: "Bilgisayar Bilimlerine Giriş"
                teacher_id:
                    type: integer
                    description: Dersi veren öğretmenin ID'si.
                    example: 1
                semester:
                    type: string
                    description: Dersin verildiği dönem.
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
                lesson_times:
                    type: array
                    description: Derse ait ders saatleri listesi.
                    items:
                        type: object
                        properties:
                            id:
                                type: integer
                                description: Ders saati kaydının ID'si.
                                example: 10
                            lesson_number:
                                type: integer
                                description: Günlük ders saati numarası.
                                example: 1
                            day:
                                type: string
                                enum: ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
                                description: Ders günü.
                                example: "TUESDAY"
                            start_time:
                                type: string
                                pattern: "^[0-2][0-9]:[0-5][0-9]$"
                                description: Başlangıç saati.
                                example: "10:00"
                            end_time:
                                type: string
                                pattern: "^[0-2][0-9]:[0-5][0-9]$"
                                description: Bitiş saati.
                                example: "11:50"
    """
    # Öğretmenin varlığını kontrol et (decorator'da zaten yapılıyor ama iyi pratik)
    teacher = data_service.find_one(TEACHERS_FILE, id=teacher_id)
    if not teacher:
        return jsonify({"message": "Öğretmen bulunamadı"}), 404

    # Öğretmene ait tüm dersleri bul
    courses = data_service.find_many(COURSES_FILE, teacher_id=teacher_id)
    
    # Her ders için ders saati bilgilerini ekle
    detailed_courses = []
    for course in courses:
        # Her bir course dictionary'si için kopyasını al
        course_copy = course.copy()
        
        # Ders saatlerini bul
        lesson_times = data_service.find_many(LESSON_TIMES_FILE, course_id=course['id'])
        
        # Ders saatlerini ekle
        course_copy['lesson_times'] = lesson_times
        
        # Detaylı ders listesine ekle
        detailed_courses.append(course_copy)
    
    # Alternatif olarak _get_course_details fonksiyonunu kullanabilirsiniz:
    # detailed_courses = [_get_course_details(course.copy()) for course in courses]
    # Bu durumda öğretmen bilgisi de eklenecektir (muhtemelen gereksiz)
    
    return jsonify(detailed_courses), 200 