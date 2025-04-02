from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from collections import defaultdict
import datetime

from app.services import data_service
from app.schemas.attendance import (
    DailyAttendanceReportResponse, DailyAttendanceReportItem, 
    CourseEmotionReportResponse, StudentAttendanceReportResponse,
    StudentAttendanceCourseReport, AttendanceDetailResponse
)
from app.schemas.user import StudentResponse # Raporlardaki öğrenci bilgileri için
from app.utils.auth import teacher_required, admin_required, get_current_user_role_and_id # Erişim kontrolü ve get_current_user_role_and_id eklendi

reports_bp = Blueprint('reports_bp', __name__)

COURSES_FILE = 'courses.json'
STUDENTS_FILE = 'students.json'
STUDENT_COURSE_FILE = 'student_course.json'
ATTENDANCE_FILE = 'attendance.json'
ATTENDANCE_DETAILS_FILE = 'attendance_details.json'
# EMOTION_HISTORY_FILE = 'emotion_history.json' # Duygu raporları için gerekli
USERS_FILE = 'users.json' # Öğrenci kullanıcı detayları için

@reports_bp.route('/attendance/daily', methods=['GET'])
@teacher_required # Öğretmenler veya Adminler günlük raporları görebilir
def get_daily_attendance_report():
    """
    Tüm dersler veya belirli bir ders için günlük yoklama raporu alır.
    Tarih belirtilmezse varsayılan olarak bugünün tarihini kullanır.
    ---    
    tags:
      - Raporlar (Reports)
      - Yoklama (Attendance)
    security:
      - Bearer: []
    parameters:
      - in: query
        name: date
        type: string
        format: date
        required: false
        description: Rapor için tarih (YYYY-MM-DD formatında). Varsayılan olarak bugün.
        example: "2024-03-18"
      - in: query
        name: course_id
        type: integer
        required: false
        description: İsteğe bağlı. Raporu belirli bir ders ID'si için filtreler.
        example: 1
    responses:
      200:
        description: Günlük yoklama raporu başarıyla alındı.
        schema:
          $ref: '#/definitions/DailyAttendanceReportResponse'
        examples:
          application/json:
            date: "2024-03-18"
            reports:
              - course_id: 1
                course_code: "CS101"
                course_name: "Bilgisayar Bilimlerine Giriş"
                present_count: 19
                absent_count: 1
              - course_id: 3
                course_code: "PHYS101"
                course_name: "Fizik I"
                present_count: 25
                absent_count: 3
              - course_id: 5 # Bu ders için bugün yoklama alınmamışsa
                course_code: "CS305"
                course_name: "Veri Yapıları"
                present_count: 0
                absent_count: 0 # Veya kayıtlı öğrenci sayısı
      400:
        description: Geçersiz tarih formatı veya ders ID'si.
        examples:
          application/json (Date): { "message": "Geçersiz tarih formatı. YYYY-AA-GG kullanın." }
      401:
        description: Yetkisiz. Geçerli token sağlanmadı.
      403:
        description: Yasak. Bu raporu görme yetkiniz yok.
      404:
        description: Ders bulunamadı (eğer `course_id` sağlandıysa).
        examples:
          application/json: { "message": "999 ID'li ders bulunamadı." }
    definitions:
      DailyAttendanceReportItem:
        type: object
        description: Günlük rapordaki tek bir ders için yoklama özeti.
        properties:
          course_id:
            type: integer
            description: Dersin ID'si.
            example: 1
          course_code:
            type: string
            description: Dersin kodu.
            example: "CS101"
          course_name:
            type: string
            description: Dersin adı.
            example: "Bilgisayar Bilimlerine Giriş"
          present_count:
            type: integer
            description: O gün derste "VAR" olarak işaretlenen öğrenci sayısı.
            example: 19
          absent_count:
            type: integer
            description: O gün derste "YOK" olarak işaretlenen öğrenci sayısı.
            example: 1
          # İhtiyaç halinde geciken/izinli sayıları eklenebilir
      DailyAttendanceReportResponse:
        type: object
        description: Belirli bir tarih için tüm ilgili derslerin yoklama özetlerini içeren yanıt.
        properties:
          date:
            type: string
            format: date
            description: Raporun ait olduğu tarih.
            example: "2024-03-18"
          reports:
            type: array
            description: O tarihteki her ders için yoklama özeti listesi.
            items:
              $ref: '#/definitions/DailyAttendanceReportItem'
    """
    try:
        report_date_str = request.args.get('date')
        if report_date_str:
            # Tarih stringini date objesine çevir
            report_date = datetime.datetime.strptime(report_date_str, '%Y-%m-%d').date()
        else:
            # Varsayılan olarak bugünün tarihini kullan
            report_date = datetime.date.today()
        
        # Sorgulamalar için ISO formatında string kullan
        report_date_iso = report_date.isoformat()

        course_id_filter = request.args.get('course_id', type=int)

    except ValueError:
        return jsonify({"message": "Geçersiz tarih formatı. YYYY-AA-GG kullanın."}), 400

    # Belirtilen tarih için yoklama kayıtlarını bul
    query_params = {"date": report_date_iso}
    courses_to_report = {}

    if course_id_filter:
        # Dersin var olup olmadığını kontrol et
        course = data_service.find_one(COURSES_FILE, id=course_id_filter)
        if not course:
            return jsonify({"message": f"{course_id_filter} ID'li ders bulunamadı."}), 404
        query_params['course_id'] = course_id_filter
        courses_to_report = {course_id_filter: course} # Sadece bu dersi raporla
    else:
        # Potansiyel olarak raporlanacak tüm dersleri al (temel bilgileri önbelleğe al)
        all_courses = data_service.read_data(COURSES_FILE)
        courses_to_report = {c['id']: c for c in all_courses}

    daily_attendance_records = data_service.find_many(ATTENDANCE_FILE, **query_params)

    report_items = []
    processed_course_ids = set() # İşlenen ders ID'lerini takip et

    # Tarih için bulunan kayıtları işle
    for record in daily_attendance_records:
        c_id = record.get('course_id')
        # Eğer kurs filtresi varsa ve ID eşleşmiyorsa atla (find_many zaten filtreledi ama ekstra kontrol)
        if course_id_filter and c_id != course_id_filter:
             continue 
             
        if c_id not in courses_to_report:
             current_app.logger.warning(f"Yoklama kaydı {record.get('id')} bilinmeyen {c_id} ID'li derse ait.")
             continue

        course_info = courses_to_report[c_id]
        processed_course_ids.add(c_id)

        # Ana kayıttan sayıları al (detayları saymaktan daha verimli)
        # Not: Bu sayılar manuel güncellemelerle güncel tutulmalıdır.
        present_count = record.get('recognized_students', 0) # Tanınan = VAR varsayımı
        absent_count = record.get('unrecognized_students', 0) # Tanınmayan = YOK varsayımı

        # Alternatif: Ana kayıt sayıları güvenilir değilse detaylardan say
        # details = data_service.find_many(ATTENDANCE_DETAILS_FILE, attendance_id=record.get('id'))
        # present_count = sum(1 for d in details if d.get('status') == 'PRESENT')
        # absent_count = sum(1 for d in details if d.get('status') == 'ABSENT')

        report_items.append(
            DailyAttendanceReportItem(
                course_id=c_id,
                course_code=course_info.get('code', 'Bilinmiyor'),
                course_name=course_info.get('name', 'Bilinmiyor'),
                present_count=present_count,
                absent_count=absent_count
            ).dict()
        )
        
    # Eğer tüm dersler raporlanıyorsa, bu tarihte yoklama kaydı olmayan dersleri ekle
    if not course_id_filter:
        for c_id, course_info in courses_to_report.items():
            if c_id not in processed_course_ids:
                 # Bu gün yoklama kaydı olmayan dersler için 0 sayılarını raporla
                 report_items.append(
                     DailyAttendanceReportItem(
                         course_id=c_id,
                         course_code=course_info.get('code', 'Bilinmiyor'),
                         course_name=course_info.get('name', 'Bilinmiyor'),
                         present_count=0,
                         absent_count=0 # Veya toplam kayıtlı öğrenci sayısını alıp hepsini YOK mu raporlamalı?
                     ).dict()
                 )

    # Ders adına göre sırala (isteğe bağlı)
    report_items.sort(key=lambda x: x.get('course_name', ''))

    response = DailyAttendanceReportResponse(
        date=report_date, # date objesi olarak gönder
        reports=report_items
    )

    return jsonify(response.dict()), 200


@reports_bp.route('/emotions/course/<int:course_id>', methods=['GET'])
@teacher_required # Sadece Öğretmen/Admin duygu raporlarını görebilir
def get_course_emotion_report(course_id):
    """
    Yoklama verilerine dayanarak belirli bir ders için genel duygu istatistiklerini alır.
    (Yer tutucu - Duygu analizi uygulamasını gerektirir).
    ---    
    tags:
      - Raporlar (Reports)
      - Duygular (Emotions)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: course_id
        type: integer
        required: true
        description: Dersin ID'si.
        example: 1
    responses:
      200:
        description: Ders için duygu istatistikleri raporu.
        schema:
          $ref: '#/definitions/CourseEmotionReportResponse'
        examples:
          application/json:
            course_id: 1
            course_code: "CS101"
            course_name: "Bilgisayar Bilimlerine Giriş"
            overall_emotion_stats:
              HAPPY: 150
              NEUTRAL: 85
              SAD: 20
              SURPRISED: 10
            timeline:
              - date: "2024-03-15"
                lesson_number: 1
                attendance_id: 15
                emotion_stats:
                  HAPPY: 15
                  NEUTRAL: 3
              - date: "2024-03-18"
                lesson_number: 1
                attendance_id: 18
                emotion_stats:
                  HAPPY: 12
                  NEUTRAL: 5
                  SAD: 2
      401:
        description: Yetkisiz.
      403:
        description: Yasak.
      404:
        description: Ders bulunamadı.
      501:
        description: Duygu analizi veya raporlama henüz uygulanmadı.
        examples:
          application/json: { "message": "Duygu raporlama henüz uygulanmadı." }
    definitions:
      CourseEmotionReportResponse:
        type: object
        description: Belirli bir ders için zaman içindeki ve genel duygu istatistikleri.
        properties:
          course_id:
            type: integer
            description: Dersin ID'si.
            example: 1
          course_code:
            type: string
            description: Dersin kodu.
            example: "CS101"
          course_name:
            type: string
            description: Dersin adı.
            example: "Bilgisayar Bilimlerine Giriş"
          overall_emotion_stats:
            type: object
            description: Tüm oturumlar boyunca her duygunun toplam sayısı.
            additionalProperties:
                type: integer
            example:
              HAPPY: 150
              NEUTRAL: 85
              SAD: 20
          timeline:
            type: array
            description: Her yoklama oturumu için duygu istatistikleri.
            items:
              type: object
              properties:
                date:
                  type: string
                  format: date
                  description: Yoklama oturumunun tarihi.
                  example: "2024-03-18"
                lesson_number:
                    type: integer
                    description: Yoklama oturumunun ders saati numarası.
                    example: 1
                attendance_id:
                    type: integer
                    description: Yoklama oturumunun ID'si.
                    example: 18
                emotion_stats:
                  type: object
                  description: O oturumda algılanan her duygunun sayısı.
                  additionalProperties:
                    type: integer
                  example:
                    HAPPY: 12
                    NEUTRAL: 5
                    SAD: 2
    """
    course = data_service.find_one(COURSES_FILE, id=course_id)
    if not course:
        return jsonify({"message": "Ders bulunamadı"}), 404
        
    # --- Yer Tutucu --- 
    # Bu, yoklama detaylarının duygu verilerini güvenilir bir şekilde saklamasını gerektirir.
    # 1. Ders için tüm yoklama kayıtlarını bul.
    # 2. Her kayıt için detaylarını bul.
    # 3. Her oturum ve genel için detaylardan duygu sayılarını topla.
    
    # Örnek yapı (gerçek veri toplama ile değiştirin)
    overall_stats = defaultdict(int)
    timeline = []
    
    attendance_records = data_service.find_many(ATTENDANCE_FILE, course_id=course_id)
    # Tarihe göre sırala
    attendance_records.sort(key=lambda x: (x.get('date', ''), x.get('lesson_number', 0)))

    for record in attendance_records:
        session_stats = defaultdict(int)
        # İlgili yoklama ID'sine ait detayları getir
        details = data_service.find_many(ATTENDANCE_DETAILS_FILE, attendance_id=record.get('id'))
        emotions_found_in_session = False
        for detail in details:
            emotion = detail.get('emotion') # Detay kaydından duygu bilgisini al
            if emotion: # Duygu verisi varsa kontrol et
                # Duygu adını tutarlılık için büyük harfe çevir
                emotion_key = emotion.upper()
                session_stats[emotion_key] += 1
                overall_stats[emotion_key] += 1
                emotions_found_in_session = True
        
        # Sadece duygu kaydedilmişse zaman çizelgesine ekle
        if emotions_found_in_session:
            timeline.append({
                "date": record.get('date'),
                "lesson_number": record.get('lesson_number'),
                "attendance_id": record.get('id'),
                "emotion_stats": dict(session_stats) # defaultdict'u dict'e çevir
            })

    # Eğer hiç duygu verisi kaydedilmemişse, 501 Not Implemented veya boş istatistik döndür
    if not overall_stats and not timeline:
         # Geliştirme aşamasında boş döndürmek daha iyi olabilir
         # return jsonify({"message": "Bu ders için duygu analizi verisi mevcut değil."}), 501
         pass # Boş istatistiklerle devam et

    response = CourseEmotionReportResponse(
        course_id=course_id,
        course_code=course.get('code', 'Bilinmiyor'),
        course_name=course.get('name', 'Bilinmiyor'),
        overall_emotion_stats=dict(overall_stats), # defaultdict'u dict'e çevir
        timeline=timeline
    )
    
    return jsonify(response.dict()), 200
    # return jsonify({"message": "Duygu raporlama henüz uygulanmadı."}), 501

@reports_bp.route('/attendance/student/<int:student_id>', methods=['GET'])
@teacher_required # Öğretmen veya Admin öğrenci raporlarını görebilir (Öğrencinin kendisi?)
def get_student_attendance_report(student_id):
    """
    Belirli bir öğrenci için genel yoklama raporunu alır, isteğe bağlı olarak derse göre filtreler.
    ---    
    tags:
      - Raporlar (Reports)
      - Yoklama (Attendance)
      - Öğrenciler (Students)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        type: integer
        required: true
        description: Öğrencinin ID'si.
        example: 5
      - in: query
        name: course_id
        type: integer
        required: false
        description: İsteğe bağlı. Raporu belirli bir ders ID'si için filtreler.
        example: 1
    responses:
      200:
        description: Öğrenci yoklama raporu başarıyla alındı.
        schema:
          $ref: '#/definitions/StudentAttendanceReportResponse'
        examples:
          application/json:
            student_info:
              id: 5
              user_id: 10
              student_number: "S12345"
              department: "Bilgisayar Mühendisliği"
              face_photo_url: "/static/faces/student_5_foto.jpg"
              created_at: "2024-01-15T14:00:00Z"
              updated_at: "2024-01-16T09:30:00Z"
              user:
                id: 10
                email: "ayse.kaya@ornek.com"
                first_name: "Ayşe"
                last_name: "Kaya"
                role: "STUDENT"
                is_active: true
            overall_attendance_rate: 0.92 # Örnek genel katılım oranı
            course_reports:
              - course_id: 1
                course_code: "CS101"
                course_name: "Bilgisayar Bilimlerine Giriş"
                rate: 0.95 # Bu dersteki katılım oranı
                total_sessions: 20
                present_sessions: 19
                details:
                  - attendance_id: 15
                    date: "2024-03-15"
                    status: "PRESENT"
                    # ... diğer kısa detay alanları ...
                  - attendance_id: 18
                    date: "2024-03-18"
                    status: "PRESENT"
                  - attendance_id: 22 # Bu derste YOK olduğu varsayılan bir oturum
                    date: "2024-03-20"
                    status: "ABSENT"
              - course_id: 3
                course_code: "PHYS101"
                course_name: "Fizik I"
                rate: 0.88
                total_sessions: 16
                present_sessions: 14
                details:
                  # ... bu ders için detaylar ...
      400:
        description: Geçersiz ders ID'si veya öğrenci belirtilen derse kayıtlı değil (eğer `course_id` sağlandıysa).
        examples:
           application/json: { "message": "Öğrenci belirtilen derse kayıtlı değil" }
      401:
        description: Yetkisiz.
      403:
        description: Yasak. Bu raporu görme yetkiniz yok.
      404:
        description: Öğrenci veya Ders bulunamadı.
        examples:
          application/json (Student): { "message": "Öğrenci bulunamadı" }
          application/json (Course): { "message": "Ders bulunamadı" }
    definitions:
      # Globalde yoksa StudentResponse veya basitleştirilmiş hali
      # Örnek olarak StudentResponse kullanılıyor, ama sadece gerekli alanlar da seçilebilir.
      StudentResponseShort: # Aslında StudentResponse'a referans verilebilir, ama şema netliği için bazen kopyalanır
         type: object
         description: Öğrencinin temel bilgileri.
         properties:
            id: { type: integer }
            user_id: { type: integer }
            student_number: { type: string }
            department: { type: string }
            face_photo_url: { type: string, nullable: true }
            created_at: { type: string, format: date-time }
            updated_at: { type: string, format: date-time }
            user: 
                type: object
                properties:
                   id: { type: integer }
                   email: { type: string, format: email }
                   first_name: { type: string }
                   last_name: { type: string }
                   role: { type: string }
                   is_active: { type: boolean }
      # Bu rapor için basitleştirilmiş yoklama detayı
      AttendanceDetailResponseShort:
          type: object
          description: Öğrenci raporu için basitleştirilmiş yoklama detayı.
          properties:
              attendance_id:
                type: integer
                description: Ana yoklama kaydının ID'si.
                example: 15
              date:
                type: string
                format: date
                description: Yoklamanın tarihi.
                example: "2024-03-15"
              status:
                type: string
                enum: ["PRESENT", "ABSENT", "LATE", "EXCUSED"]
                description: Öğrencinin o oturumdaki durumu.
                example: "PRESENT"
              # İstenirse güven/duygu eklenebilir
      # Tek bir ders için öğrenci yoklama raporu
      StudentAttendanceCourseReport:
        type: object
        description: Belirli bir dersteki öğrenci yoklama özeti ve detayları.
        properties:
          course_id:
            type: integer
            description: Dersin ID'si.
            example: 1
          course_code:
            type: string
            description: Dersin kodu.
            example: "CS101"
          course_name:
            type: string
            description: Dersin adı.
            example: "Bilgisayar Bilimlerine Giriş"
          rate:
            type: number
            format: float
            nullable: true
            description: Bu dersteki katılım oranı (VAR / Toplam Oturum).
            example: 0.95
          total_sessions:
             type: integer
             description: Bu ders için yapılan toplam yoklama oturumu sayısı.
             example: 20
          present_sessions:
             type: integer
             description: Öğrencinin "VAR" olduğu oturum sayısı.
             example: 19
          details:
            type: array
            description: Öğrencinin bu dersteki her yoklama oturumu için durumu.
            items:
              $ref: '#/definitions/AttendanceDetailResponseShort'
      # Öğrenci için genel rapor yanıtı
      StudentAttendanceReportResponse:
        type: object
        description: Belirli bir öğrenci için yoklama raporu.
        properties:
          student_info:
            # $ref: '#/definitions/StudentResponseShort' # Veya tam StudentResponse
            $ref: '#/definitions/StudentResponse' # Tam öğrenci bilgisi için
            description: Raporun ait olduğu öğrencinin bilgileri.
          overall_attendance_rate:
            type: number
            format: float
            nullable: true
            description: Raporlanan tüm derslerdeki genel katılım oranı.
            example: 0.92
          course_reports:
            type: array
            description: Öğrencinin kayıtlı olduğu (veya filtrelenen) her ders için ayrı rapor.
            items:
              $ref: '#/definitions/StudentAttendanceCourseReport'
    """
    # --- Yetkilendirme (Önce yapılmalı) --- 
    current_role, current_user_id = get_current_user_role_and_id()
    if current_role is None or current_user_id is None:
        return jsonify({"message": "Geçersiz token kimliği"}), 401
    # Şu an sadece Teacher/Admin erişebilir, öğrencinin kendisi erişemez.
    if current_role not in ["ADMIN", "TEACHER"]:
         return jsonify({"message": "Yasak: Bu raporu görme yetkiniz yok."}), 403
    # --- Yetkilendirme Sonu --- 

    student = data_service.find_one(STUDENTS_FILE, id=student_id)
    if not student: return jsonify({"message": "Öğrenci bulunamadı"}), 404
    
    course_id_filter = request.args.get('course_id', type=int)
    target_course_ids = []
    courses_info = {}

    if course_id_filter:
        course = data_service.find_one(COURSES_FILE, id=course_id_filter)
        if not course: return jsonify({"message": "Ders bulunamadı"}), 404
        # Öğrencinin bu derse kayıtlı olup olmadığını kontrol et
        enrollment = data_service.find_one(STUDENT_COURSE_FILE, student_id=student_id, course_id=course_id_filter)
        if not enrollment: return jsonify({"message": "Öğrenci belirtilen derse kayıtlı değil"}), 400
        target_course_ids.append(course_id_filter)
        courses_info = {course_id_filter: course}
    else:
        # Öğrencinin kayıtlı olduğu tüm dersleri al
        enrollments = data_service.find_many(STUDENT_COURSE_FILE, student_id=student_id)
        if not enrollments:
             # Öğrenci hiçbir derse kayıtlı değilse boş rapor döndür
              from app.routes.students import _get_student_with_user
              student_info_response = _get_student_with_user(student.copy())
              response = StudentAttendanceReportResponse(
                    student_info=student_info_response,
                    overall_attendance_rate=None,
                    course_reports=[]
              )
              return jsonify(response.dict()), 200
              
        target_course_ids = [e['course_id'] for e in enrollments]
        # Hedef derslerin temel bilgilerini getir
        all_courses = data_service.read_data(COURSES_FILE)
        courses_info = {c['id']: c for c in all_courses if c['id'] in target_course_ids}

    # Öğrenci için TÜM yoklama detaylarını getir
    all_student_details = data_service.find_many(ATTENDANCE_DETAILS_FILE, student_id=student_id)
    
    # İlgili ana yoklama kayıtlarını getir (ders_id ve tarih için)
    # Sadece öğrencinin detaylarının ait olduğu ana kayıtları almak daha verimli olabilir
    relevant_attendance_ids = {d['attendance_id'] for d in all_student_details}
    all_attendance_records = data_service.read_data(ATTENDANCE_FILE)
    # Sadece ilgili olanları map'te tut
    attendance_record_map = {att['id']: att for att in all_attendance_records if att['id'] in relevant_attendance_ids}

    course_reports = []
    total_present = 0
    total_sessions = 0

    present_statuses = ["PRESENT", "LATE"] # VAR sayılacak durumlar

    for course_id in target_course_ids:
        course_info = courses_info.get(course_id)
        if not course_info: continue # Ders bilgisi bulunamazsa atla (tutarlılık sorunu)

        course_details_short = []
        course_present_count = 0
        course_session_count = 0

        # *Bu derse* ait yoklama oturumlarını bul
        # Ana kayıtları ders ID'sine göre filtrele
        course_attendance_sessions = {att_id: att_rec for att_id, att_rec in attendance_record_map.items() if att_rec.get('course_id') == course_id}
        course_attendance_ids = set(course_attendance_sessions.keys())
        
        if course_attendance_ids:
             course_session_count = len(course_attendance_ids)
             # Öğrencinin detaylarını bu dersin oturumları için filtrele
             student_details_for_course = [
                 detail for detail in all_student_details 
                 if detail.get('attendance_id') in course_attendance_ids
             ]
             
             for detail in student_details_for_course:
                 att_record = course_attendance_sessions.get(detail['attendance_id'])
                 # AttendanceDetailResponseShort şemasına uygun kısa rapor oluştur
                 detail_short_report = {
                      "attendance_id": detail.get('attendance_id'),
                      "date": att_record.get('date') if att_record else None,
                      "status": detail.get('status')
                      # İstenirse başka alanlar eklenebilir (örn. confidence)
                 }
                 # Schema None değerlere izin vermiyorsa kaldır (isteğe bağlı)
                 # detail_short_report = {k: v for k, v in detail_short_report.items() if v is not None}
                 
                 course_details_short.append(detail_short_report)
                 # VAR sayılacak durumlardan biri mi kontrol et (.get ile güvenli)
                 if detail.get('status') in present_statuses:
                     course_present_count += 1

        # Ders için katılım oranını hesapla
        course_rate = (course_present_count / course_session_count * 100) if course_session_count > 0 else None # Yüzde olarak
        total_present += course_present_count
        total_sessions += course_session_count

        # Detayları tarihe göre sırala (en yeniden eskiye)
        course_details_short.sort(key=lambda x: x.get('date') or '', reverse=True)

        course_reports.append(
            StudentAttendanceCourseReport(
                course_id=course_id,
                course_code=course_info.get('code', 'Bilinmiyor'),
                course_name=course_info.get('name', 'Bilinmiyor'),
                rate=round(course_rate, 2) if course_rate is not None else None, # Oranı yuvarla
                total_sessions=course_session_count,
                present_sessions=course_present_count,
                details=course_details_short
            ).dict()
        )

    # Genel katılım oranını hesapla
    overall_rate = (total_present / total_sessions * 100) if total_sessions > 0 else None

    # Yanıt için öğrenci bilgilerini hazırla
    from app.routes.students import _get_student_with_user # Yardımcıyı yeniden kullan
    student_info_response = _get_student_with_user(student.copy()) # Kopya kullan
    # Pydantic modeline dönüştür veya dict olarak kullan
    # student_pydantic = StudentResponse.parse_obj(student_info_response) if student_info_response else None

    # Ders adına göre raporları sırala (isteğe bağlı)
    course_reports.sort(key=lambda x: x.get('course_name', ''))

    response = StudentAttendanceReportResponse(
        student_info=student_info_response, # Hazırlanan dict'i kullan
        overall_attendance_rate=round(overall_rate, 2) if overall_rate is not None else None, # Oranı yuvarla
        course_reports=course_reports
    )

    return jsonify(response.dict()), 200 