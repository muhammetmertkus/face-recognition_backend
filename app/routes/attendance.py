import os
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from werkzeug.utils import secure_filename
import datetime
import traceback # Detaylı hata loglama için
import cv2 # OpenCV for image cropping
import numpy as np # NumPy for array operations
from collections import Counter # For counting emotions
from PIL import Image # To read image from filestorage
import io # To read image from filestorage
import face_recognition # Import face_recognition
from flask_jwt_extended import jwt_required # Import jwt_required

from app.services import data_service, face_service # Removed file_service import
# from app.services import emotion_service # Uygulanınca import edilecek
from app.schemas.attendance import (
    AttendanceResponse, AttendanceCreate, AttendanceDetailResponse, 
    AttendanceManualUpdate, AttendanceResultSummary, AttendanceResultDetail # Renamed from AttendanceResponseSummary
)
from app.schemas.user import StudentResponse # For student details
from app.models.attendance import Attendance, AttendanceDetail, default_datetime
from app.utils.auth import teacher_required, get_jwt_identity, self_or_admin_required, get_current_user_role_and_id

attendance_bp = Blueprint('attendance_bp', __name__)

COURSES_FILE = 'courses.json'
STUDENTS_FILE = 'students.json'
STUDENT_COURSE_FILE = 'student_course.json'
ATTENDANCE_FILE = 'attendance.json'
ATTENDANCE_DETAILS_FILE = 'attendance_details.json'
EMOTION_HISTORY_FILE = 'emotion_history.json' # Duygu geçmişi kullanılırsa eklenecek
TEACHERS_FILE = 'teachers.json'
USERS_FILE = 'users.json' # USERS_FILE tanımı eklendi

def _get_attendance_details(attendance_dict):
    """Yardımcı fonksiyon: Bir yoklama kaydı için detayları (öğrenciler, durum) getirir."""
    if not attendance_dict:
        return None
    details = data_service.find_many(ATTENDANCE_DETAILS_FILE, attendance_id=attendance_dict.get('id'))
    # İsteğe bağlı: Detayları öğrenci bilgileriyle zenginleştir
    detailed_list = []
    for detail in details:
        student = data_service.find_one(STUDENTS_FILE, id=detail.get('student_id'))
        if student:
             # Varsa ve gerekliyse students rotasından yardımcı fonksiyonu kullan
             # from app.routes.students import _get_student_with_user 
             # detail['student'] = _get_student_with_user(student)
             # Veya sadece temel bilgileri ekle
             student.pop('password_hash', None)
             student.pop('face_encodings', None)
             # Yanıtta sadece gerekli temel öğrenci bilgilerini döndür
             user = data_service.find_one(USERS_FILE, id=student.get('user_id'))
             user_info = None
             if user:
                 user_info = {
                     'id': user.get('id'),
                     'first_name': user.get('first_name'),
                     'last_name': user.get('last_name'),
                     'email': user.get('email'),
                 }
             detail['student'] = {
                 'id': student['id'], 
                 'student_number': student.get('student_number'), 
                 'user': user_info
             } 
        detailed_list.append(detail)

    attendance_dict['details'] = detailed_list
    return attendance_dict


@attendance_bp.route('/', methods=['POST'])
@teacher_required
def create_attendance():
    """
    Bir fotoğraf yükleyerek ve yüzleri işleyerek yeni bir yoklama kaydı oluşturur.
    Yalnızca dersin öğretmeni yoklama alabilir (veya Admin).
    ---
    tags:
      - Yoklama (Attendance)
    security:
      - Bearer: []
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: Yoklama alınacak sınıfın fotoğrafı.
      - in: formData
        name: course_id
        type: integer
        required: true
        description: Yoklamanın ait olduğu dersin ID'si.
        example: 1
      - in: formData
        name: date
        type: string
        format: date
        required: true
        description: Yoklamanın alındığı tarih (YYYY-AA-GG formatında).
        example: "2024-05-20"
      - in: formData
        name: lesson_number
        type: integer
        required: true
        description: Yoklamanın ait olduğu ders saati numarası (örn. 1, 2).
        example: 1
      - in: formData
        name: type
        type: string
        required: true
        enum: ["FACE", "EMOTION", "FACE_EMOTION"]
        description: Yoklama türü (Şimdilik sadece FACE destekleniyor).
        example: "FACE"
    responses:
      201:
        description: Yoklama başarıyla oluşturuldu ve yüzler işlendi. Tanınan ve tanınmayan öğrenci sayıları döndürülür.
        schema:
          $ref: '#/definitions/AttendanceResultSummary' # Önceden tanımlanmış veya global şema
        examples:
          application/json:
            attendance_id: 25
            recognized_count: 18
            unrecognized_count: 2
            results:
              - student_id: 5
                status: "PRESENT"
                confidence: 0.95
                emotion: null
                emotion_confidence: null
              - student_id: 12
                status: "ABSENT"
                confidence: null
                emotion: null
                emotion_confidence: null
              # ... (diğer öğrenciler)
      400:
        description: Geçersiz istek (eksik dosya, eksik form alanı, geçersiz veri formatı, desteklenmeyen dosya türü, resimde yüz bulunamadı).
      401:
        description: Yetkisiz (Geçerli JWT token sağlanmadı).
      403:
        description: Yasak (Kullanıcı dersin öğretmeni veya Admin değil).
      404:
        description: Ders veya derse kayıtlı öğrenci bulunamadı.
      500:
        description: Sunucu hatası (Resim işleme hatası, veritabanı yazma hatası).
    """
    # --- Mevcut kullanıcı rolünü ve INT ID'sini al --- 
    current_role, current_user_id = get_current_user_role_and_id() 
    if current_role is None or current_user_id is None:
         return jsonify({"message": "Geçersiz token kimliği veya kullanıcı bulunamadı"}), 401
    # --- Bitiş --- 

    # --- 1. Form Verisini & Dosyayı Doğrula --- 
    if 'file' not in request.files:
        return jsonify({"message": "İstekte dosya bölümü yok"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "Seçili dosya yok"}), 400

    form_data = request.form.to_dict()
    try:
        # Form alanlarını doğrulamak için Pydantic modelini kullan (dosya hariç)
        attendance_input = AttendanceCreate(**form_data)
    except ValidationError as e:
        # Pydantic hatalarını daha okunabilir formatta döndür
        error_details = []
        for error in e.errors():
             field = ".".join(map(str, error.get('loc', [])))
             message = error.get('msg', 'Bilinmeyen hata')
             error_details.append({"field": field, "message": message})
        return jsonify({"message": "Geçersiz form verisi", "errors": error_details}), 400
    except Exception as e: # Olası tarih ayrıştırma hatalarını vb. yakala.
         return jsonify({"message": f"Geçersiz form verisi: {e}"}), 400

    # --- 2. İzinleri ve Ders/Saat Geçerliliğini Kontrol Et --- 
    course = data_service.find_one(COURSES_FILE, id=attendance_input.course_id)
    if not course:
        return jsonify({"message": "Ders bulunamadı"}), 404
    
    # Mevcut kullanıcının bu dersin öğretmeni olup olmadığını kontrol et
    teacher = data_service.find_one(TEACHERS_FILE, id=course.get('teacher_id'))
    # Kullanıcı ID'si (int) karşılaştırması
    is_teacher_of_course = teacher and teacher.get('user_id') == current_user_id
    # Rol karşılaştırması
    is_admin = current_role == "ADMIN"
    
    if not is_teacher_of_course and not is_admin: 
        return jsonify({"message": "Yasak: Sadece dersin öğretmeni veya admin yoklama alabilir."}), 403

    # İsteğe bağlı: lesson_number'ı dersin/tarihin mevcut ders saatlerine göre doğrula
    # lesson_time = data_service.find_one(LESSON_TIMES_FILE, course_id=course_id, lesson_number=lesson_number)
    # if not lesson_time: return jsonify(...), 404

    # --- 3. Resmi İşle: Yüzleri Bul & Kodlamaları Çıkar --- 
    face_locations = []
    image_encodings = []
    img_array = None # Initialize img_array
    face_analysis_results = [] # Store analysis results for each detected face
    all_detected_emotions = [] # Collect all emotions for stats

    try:
        if not face_service.allowed_file(file.filename):
             allowed_ext_str = ", ".join(face_service.ALLOWED_EXTENSIONS)
             return jsonify({"message": f"Dosya türüne izin verilmiyor. İzin verilenler: {allowed_ext_str}"}), 400

        # Read the image file into memory (once)
        file.seek(0)
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes))
        # Convert PIL image to numpy array (RGB format)
        # Ensure image is in RGB format for face_recognition and potentially DeepFace
        img_array = np.array(img.convert('RGB')) 

        # Find face locations (use the same array)
        # model can be 'cnn' or 'hog'
        face_locations = face_recognition.face_locations(img_array, model="hog")

        if not face_locations:
            return jsonify({"message": "Yüklenen resimde yüz tespit edilemedi."}), 400
            
        current_app.logger.info(f"{attendance_input.course_id} ID'li ders için yüklenen yoklama fotoğrafında {len(face_locations)} yüz bulundu.")

        # Extract face encodings for the found locations
        image_encodings = face_recognition.face_encodings(img_array, known_face_locations=face_locations)
        
        # --- Perform Age/Gender/Emotion Analysis for each detected face --- 
        if attendance_input.type in ["EMOTION", "FACE_EMOTION"]: # Only analyze if requested
            current_app.logger.info(f"Performing analysis (age, gender, emotion) for {len(face_locations)} faces...")
            actions_to_perform = ['age', 'gender', 'emotion']
            for i, (top, right, bottom, left) in enumerate(face_locations):
                # Crop the face from the image (NumPy slicing)
                # Add some padding maybe? For now, use exact coordinates
                face_image = img_array[top:bottom, left:right]
                
                # Analyze the cropped face
                # Pass the NumPy array directly
                analysis_result = face_service.analyze_face_attributes(face_image, actions=actions_to_perform)
                face_analysis_results.append(analysis_result) # Store result (or None if failed)
                
                if analysis_result and analysis_result.get('emotion'):
                    all_detected_emotions.append(analysis_result['emotion'])
                    current_app.logger.debug(f"Face {i}: Analysis Result: {analysis_result}")
                else:
                     current_app.logger.debug(f"Face {i}: Analysis failed or no emotion detected.")
            current_app.logger.info(f"Analysis complete. Found emotions: {len(all_detected_emotions)}")
        else:
             # Ensure face_analysis_results has the same length as face_locations, filled with None
             face_analysis_results = [None] * len(face_locations)

    except ValueError as ve: # face_service'den dosya türü hatası
        return jsonify({"message": str(ve)}), 400 
    except Exception as e:
        current_app.logger.error(f"Yoklama resmi işlenirken veya analiz edilirken hata: {e}\n{traceback.format_exc()}")
        return jsonify({"message": "Yoklama resmi işlenirken veya analiz edilirken hata oluştu."}), 500

    # --- 4. Kayıtlı Öğrencileri ve Kodlamalarını Al --- 
    enrollments = data_service.find_many(STUDENT_COURSE_FILE, course_id=attendance_input.course_id)
    enrolled_student_ids = [enrollment['student_id'] for enrollment in enrollments]

    if not enrolled_student_ids:
        return jsonify({"message": "Bu derse kayıtlı öğrenci bulunamadı."}), 404

    all_students = data_service.read_data(STUDENTS_FILE)
    enrolled_students = [s for s in all_students if s['id'] in enrolled_student_ids]
    
    known_encodings = []
    student_id_map = [] # Hangi ID'nin hangi bilinen kodlama indeksine karşılık geldiğini takip et
    for student in enrolled_students:
        encoding_str = student.get('face_encodings')
        if encoding_str:
            try:
                decoded = face_service.decode_encodings_from_json(encoding_str)
                if decoded:
                    known_encodings.extend(decoded) # Öğrenci için tüm bilinen kodlamaları ekle
                    student_id_map.extend([student['id'] for _ in decoded])
            except Exception as decode_e:
                 current_app.logger.error(f"Öğrenci {student['id']} için yüz kodlaması çözülürken hata: {decode_e}")
        else:
            current_app.logger.warning(f"Öğrenci {student['id']} için kayıtlı yüz verisi yok. Tanınamaz.")
            
    if not known_encodings:
         return jsonify({"message": "Derse kayıtlı öğrencilerin hiçbirinde kayıtlı yüz verisi bulunamadı."}), 400

    # --- 5. Yüzleri Karşılaştır, Analiz Sonuçlarını Eşleştir --- 
    # Store details per recognized student { student_id: {'confidence': float, 'analysis': dict_or_none} }
    recognized_student_details = {} 
    # Keep track of which image encoding index maps to which best match student
    encoding_match_map = {} # { encoding_index: student_id }

    face_recognition_tolerance = current_app.config.get('FACE_RECOGNITION_TOLERANCE', 0.6)

    # Iterate through detected faces (encodings and their analysis results)
    for idx, img_encoding in enumerate(image_encodings):
        matches = []
        distances = []
        if known_encodings:
            matches = face_service.compare_faces(known_encodings, img_encoding, tolerance=face_recognition_tolerance)
            distances = face_service.face_distance(known_encodings, img_encoding)
        
        best_match_index = -1
        min_distance = 1.0 

        for i, match in enumerate(matches):
            if match and distances[i] < min_distance:
                # Check if this known encoding (student) has already been matched with a *better* distance by another face
                prospective_student_id = student_id_map[i]
                existing_match = recognized_student_details.get(prospective_student_id)
                if not existing_match or distances[i] < (1.0 - existing_match['confidence']): # Compare distances
                    min_distance = distances[i]
                    best_match_index = i
        
        if best_match_index != -1:
            recognized_student_id = student_id_map[best_match_index]
            confidence = max(0.0, 1.0 - min_distance)
            current_analysis = face_analysis_results[idx] # Get analysis for this face
            
            # If this student is already recognized, only update if current match is better
            existing_match = recognized_student_details.get(recognized_student_id)
            if not existing_match or confidence > existing_match['confidence']:
                recognized_student_details[recognized_student_id] = {
                    'confidence': confidence,
                    'analysis': current_analysis
                }
                encoding_match_map[idx] = recognized_student_id # Store which encoding matched this student best
                current_app.logger.info(f"Student {recognized_student_id} matched (Conf: {confidence:.4f}) with face {idx}. Analysis: {current_analysis}")
            else:
                current_app.logger.info(f"Student {recognized_student_id} already matched with better confidence ({existing_match['confidence']:.4f}). Skipping face {idx} match (Conf: {confidence:.4f}).")
        else:
             # Face did not match any known student well enough
             log_min_distance = min(distances) if distances else 'N/A'
             current_app.logger.info(f"Face {idx} did not match known students (min distance: {log_min_distance}). Analysis: {face_analysis_results[idx]}")
             # If no match, the analysis result for this face isn't associated with a student

    # --- Calculate Overall Emotion Statistics --- 
    emotion_statistics = dict(Counter(all_detected_emotions)) if all_detected_emotions else None
    current_app.logger.info(f"Overall Emotion Stats: {emotion_statistics}")

    # --- 6. Yoklama Kayıtlarını Oluştur (Ana ve Detaylar) --- 
    now = default_datetime()
    attendance_id = data_service.get_next_id(ATTENDANCE_FILE)
    recognized_count = len(recognized_student_details) # Count of unique students recognized
    total_enrolled = len(enrolled_student_ids)
    absent_count = total_enrolled - recognized_count 

    # --- Yoklama Fotoğrafını Kaydet --- 
    photo_url = None
    saved_photo_path = None
    try:
        file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
        filename = secure_filename(f"attendance_{attendance_input.course_id}_{attendance_input.date.isoformat()}_{attendance_input.lesson_number}_{datetime.datetime.now().strftime('%H%M%S')}.{file_extension}")
        upload_dir = current_app.config.get('ATTENDANCE_UPLOAD_FOLDER')
        if not upload_dir:
             raise ValueError("ATTENDANCE_UPLOAD_FOLDER yapılandırılmamış.")
        if not os.path.exists(upload_dir): os.makedirs(upload_dir)
        file_path = os.path.join(upload_dir, filename)
        
        file.seek(0) 
        file.save(file_path)
        saved_photo_path = file_path # Potansiyel silme için tam yolu sakla
        # Web erişimi için göreceli URL oluştur (örn. /uploads/attendance/dosya.jpg)
        # Bu URL'nin uygulamanızın statik dosya sunumuyla eşleştiğinden emin olun
        static_url_path = current_app.static_url_path or '' # Genellikle /static
        relative_upload_dir = os.path.relpath(upload_dir, current_app.static_folder if current_app.static_folder else current_app.root_path)
        photo_url = f"{static_url_path}/{relative_upload_dir}/{filename}".replace("\\", "/").replace("//", "/") # Windows ve çift // düzeltmesi
         
        current_app.logger.info(f"Yoklama fotoğrafı kaydedildi: {saved_photo_path}, URL: {photo_url}")
    except Exception as e:
        current_app.logger.error(f"Yoklama fotoğrafı kaydedilemedi: {e}")
        photo_url = None 
        saved_photo_path = None
        # Hata durumunda devam etmeli mi? Yoksa 500 döndürmeli mi?
        # Şimdilik devam et, fotoğrafsız bir kayıt oluşsun.
    # --- Fotoğraf Kaydetme Sonu --- 

    main_attendance_record = {
        "id": attendance_id,
        "course_id": attendance_input.course_id,
        "date": attendance_input.date.isoformat(),
        "lesson_number": attendance_input.lesson_number,
        "type": attendance_input.type.upper(),
        "photo_path": photo_url,
        "total_students": total_enrolled, 
        "recognized_students": recognized_count,
        "unrecognized_students": absent_count,
        "emotion_statistics": emotion_statistics, # Add overall stats here
        "created_by": current_user_id,
        "created_at": now,
        "updated_at": now
    }

    created_main_record_dict = None
    created_detail_ids = []
    final_summary_results = [] # Use AttendanceResultDetail structure

    try:
        # Adım 6a: Ana yoklama kaydını oluştur
        created_main_record_dict = data_service.add_item(ATTENDANCE_FILE, main_attendance_record, assign_id=False)
        current_app.logger.info(f"Ana yoklama kaydı {attendance_id} başarıyla oluşturuldu")

        # Adım 6b: TÜM kayıtlı öğrenciler için detay kayıtları ve özet sonuçları oluştur
        current_app.logger.info(f"{len(enrolled_student_ids)} kayıtlı öğrenci için yoklama detayları ve özet oluşturuluyor.")
        
        # Öğrenci detaylarını hazırla - tümünü tek seferde alalım
        students_dict = {}
        users_dict = {}
        
        # Önce öğrenci bilgilerini yükle
        for student in enrolled_students:
            students_dict[student['id']] = student
            
        # Kullanıcı bilgilerini yükle (öğrenci-kullanıcı ilişkisini kurabilmek için)
        user_ids = [s.get('user_id') for s in enrolled_students if s.get('user_id')]
        if user_ids:
            all_users = data_service.read_data(USERS_FILE)
            for user in all_users:
                if user['id'] in user_ids:
                    users_dict[user['id']] = user
        
        for student_id in enrolled_student_ids:
            status = "ABSENT"
            confidence = None
            emotion = None
            estimated_age = None
            estimated_gender = None

            student_match_details = recognized_student_details.get(student_id)
            if student_match_details:
                status = "PRESENT"
                confidence = student_match_details['confidence']
                analysis = student_match_details['analysis']
                if analysis:
                    emotion = analysis.get('emotion')
                    estimated_age = analysis.get('age')
                    estimated_gender = analysis.get('gender')
            
            # Create detail record for database
            detail_record = {
                "attendance_id": attendance_id,
                "student_id": student_id,
                "status": status,
                "confidence": confidence,
                "emotion": emotion,
                "estimated_age": estimated_age, # Save to DB
                "estimated_gender": estimated_gender, # Save to DB
                # "emotion_confidence": None, # Add if available from analysis
                # "emotion_statistics": None, # Per-student stats if needed
                "created_at": now,
                "updated_at": now
            }
            try:
                created_detail = data_service.add_item(ATTENDANCE_DETAILS_FILE, detail_record)
                created_detail_ids.append(created_detail['id'])
                current_app.logger.debug(f"Öğrenci {student_id} için yoklama detayı kaydedildi (Durum: {status}) - ID: {created_detail['id']}")
            except Exception as detail_e:
                 current_app.logger.error(f"Öğrenci {student_id} için yoklama detayı kaydedilemedi (Yoklama ID: {attendance_id}): {detail_e}")
                 raise detail_e 

            # Öğrenci ve kullanıcı bilgilerini al
            student_info = None
            student = students_dict.get(student_id)
            
            if student:
                user_id = student.get('user_id')
                user = users_dict.get(user_id) if user_id else None
                
                student_info = {
                    "id": student_id,
                    "student_number": student.get('student_number'),
                    "first_name": user.get('first_name') if user else None,
                    "last_name": user.get('last_name') if user else None,
                    "email": user.get('email') if user else None
                }

            # Create summary result for the final response (using AttendanceResultDetail structure)
            summary_detail = AttendanceResultDetail(
                student_id=student_id,
                status=status,
                confidence=confidence,
                emotion=emotion,
                estimated_age=estimated_age,
                estimated_gender=estimated_gender,
                student=student_info  # Öğrenci bilgilerini ekle
            )
            final_summary_results.append(summary_detail)

        # Adım 6c: Başarılı yanıt özetini hazırla (using AttendanceResultSummary)
        response_summary = AttendanceResultSummary(
            attendance_id=attendance_id,
            recognized_count=recognized_count,
            unrecognized_count=absent_count,
            total_students=total_enrolled,  # Toplam öğrenci sayısını ekle
            emotion_statistics=emotion_statistics, # Add overall stats to summary
            results=final_summary_results # Pass the list of AttendanceResultDetail objects
        )
        current_app.logger.info(f"Yoklama ID {attendance_id} için oluşturma başarılı")
        # Pydantic models are automatically converted to dicts by jsonify
        return jsonify(response_summary.dict()), 201 

    except Exception as e:
        current_app.logger.error(f"Yoklama ID {attendance_id} için yoklama kaydı kaydetme işlemi sırasında hata: {e}\n{traceback.format_exc()}")
        
        # --- Geri Alma Mantığı --- 
        current_app.logger.warning(f"Hata nedeniyle yoklama ID {attendance_id} için geri alma başlatılıyor.")
        # 1. Başarıyla oluşturulan detay kayıtlarını sil
        if created_detail_ids:
            current_app.logger.warning(f"Deleting {len(created_detail_ids)} created attendance detail records.")
            deleted_detail_count = 0
            for detail_id in created_detail_ids:
                if data_service.delete_item(ATTENDANCE_DETAILS_FILE, detail_id):
                    deleted_detail_count += 1
            current_app.logger.warning(f"Deleted {deleted_detail_count} detail records during rollback.")
            
        # 2. Oluşturulduysa ana yoklama kaydını sil
        if created_main_record_dict:
            current_app.logger.warning(f"Deleting main attendance record {attendance_id}.")
            if data_service.delete_item(ATTENDANCE_FILE, attendance_id):
                current_app.logger.warning(f"Deleted main attendance record {attendance_id} during rollback.")
            else:
                current_app.logger.error(f"Failed to delete main attendance record {attendance_id} during rollback.")
                
        # 3. Varsa kaydedilen fotoğrafı sil
        if saved_photo_path and os.path.exists(saved_photo_path):
            current_app.logger.warning(f"Deleting saved attendance photo: {saved_photo_path}")
            try:
                os.remove(saved_photo_path)
                current_app.logger.warning(f"Deleted attendance photo during rollback.")
            except OSError as photo_e:
                current_app.logger.error(f"Failed to delete attendance photo {saved_photo_path} during rollback: {photo_e}")
                
        return jsonify({"message": "Yoklama kayıtları kaydedilirken bir hata oluştu. Lütfen logları kontrol edin."}), 500


@attendance_bp.route('/<int:attendance_id>', methods=['GET'])
@teacher_required # Dersin Öğretmeni veya Admin erişebilir
def get_attendance_record(attendance_id):
    """
    Belirli bir yoklama kaydının detaylarını (öğrenci durumları dahil) getirir.
    ---    
    tags:
      - Yoklama (Attendance)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: attendance_id
        type: integer
        required: true
        description: Detayları alınacak yoklama kaydının ID'si.
        example: 15
    responses:
      200:
        description: Yoklama kaydı detayları başarıyla alındı.
        schema:
          $ref: '#/definitions/AttendanceResponse' # Detayları içeren tam yanıt
        examples:
          application/json:
            id: 15
            course_id: 1
            date: "2024-03-15"
            lesson_number: 1
            type: "FACE"
            photo_path: "/static/attendance/attendance_1_2024-03-15_1_103000.jpg"
            total_students: 20
            recognized_students: 18
            unrecognized_students: 2
            emotion_statistics: null
            created_by: 2 # Öğretmen Kullanıcı ID'si
            created_at: "2024-03-15T10:30:05Z"
            updated_at: "2024-03-15T10:30:05Z"
            details:
              - id: 101
                attendance_id: 15
                student_id: 5
                status: "PRESENT"
                confidence: 0.95
                emotion: null
                emotion_confidence: null
                emotion_statistics: null
                created_at: "2024-03-15T10:30:05Z"
                updated_at: "2024-03-15T10:30:05Z"
                student:
                  id: 5
                  student_number: "S12345"
                  user:
                    id: 10
                    first_name: "Ayşe"
                    last_name: "Kaya"
                    email: "ayse.kaya@ornek.com"
              - id: 102
                attendance_id: 15
                student_id: 12
                status: "ABSENT"
                confidence: null
                emotion: null
                emotion_confidence: null
                emotion_statistics: null
                created_at: "2024-03-15T10:30:05Z"
                updated_at: "2024-03-18T14:00:00Z" # Yeni güncelleme zamanı
                student:
                  id: 12
                  student_number: "S54321"
                  user:
                    id: 15
                    first_name: "Ali"
                    last_name: "Veli"
                    email: "ali.veli@ornek.com"
              # ... (diğer öğrenci detayları)
      401:
        description: Yetkisiz. Geçerli token sağlanmadı veya kullanıcı bulunamadı.
      403:
        description: Yasak. Kullanıcının bu yoklama kaydını görme yetkisi yok (dersin öğretmeni veya Admin değil).
      404:
        description: Belirtilen ID'ye sahip yoklama kaydı bulunamadı.
        examples:
          application/json: { "message": "Yoklama kaydı bulunamadı" }
      500:
        description: Yoklama kaydıyla ilişkili ders bilgisi bulunamadı (veri tutarsızlığı).
    """
    attendance_record = data_service.find_one(ATTENDANCE_FILE, id=attendance_id)
    if not attendance_record:
        return jsonify({"message": "Yoklama kaydı bulunamadı"}), 404

    # Yetkilendirme kontrolü: Kullanıcının dersin öğretmeni veya admin olduğundan emin ol
    # --- Mevcut kullanıcı rolünü ve INT ID'sini al --- 
    current_role, current_user_id = get_current_user_role_and_id() 
    if current_role is None or current_user_id is None:
         return jsonify({"message": "Geçersiz token kimliği veya kullanıcı bulunamadı"}), 401
    # --- Bitiş --- 

    course_id = attendance_record.get('course_id')
    course = data_service.find_one(COURSES_FILE, id=course_id)
    if not course: 
        current_app.logger.error(f"Attendance record {attendance_id}, var olmayan {course_id} ID'li derse bağlı.")
        return jsonify({"message": "İç tutarsızlık: Bu yoklama kaydı için ders bulunamadı."}), 500
        
    teacher = data_service.find_one(TEACHERS_FILE, id=course.get('teacher_id'))
    # Karşılaştırma için current_user_id (int) kullan
    is_teacher_of_course = teacher and teacher.get('user_id') == current_user_id
    # Karşılaştırma için current_role kullan
    is_admin = current_role == "ADMIN"

    if not is_teacher_of_course and not is_admin:
        return jsonify({"message": "Yasak: Bu yoklama kaydını görme yetkiniz yok."}), 403

    # _get_attendance_details ile detayları al ve zenginleştir
    detailed_record = _get_attendance_details(attendance_record.copy()) # Ana kaydı değiştirmemek için kopya kullan
    return jsonify(detailed_record), 200


@attendance_bp.route('/course/<int:course_id>', methods=['GET'])
# Burada teacher_required kullan, çünkü dersin öğretmeni veya admin görmeli.
# self_or_admin_required is tricky when the function is called indirectly.
@teacher_required 
def get_attendance_for_course(course_id):
    """
    Belirli bir derse ait tüm yoklama kayıtlarını getirir (özet görünüm, detaylar hariç).
    Yalnızca dersin öğretmeni veya Admin erişebilir.
    ---    
    tags:
      - Yoklama (Attendance)
      - Dersler (Courses)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: course_id
        type: integer
        required: true
        description: Yoklama kayıtları listelenecek dersin ID'si.
        example: 1
    responses:
      200:
        description: Ders için yoklama kayıtlarının listesi (detaysız).
        schema:
          type: array
          items: 
            # Ana yoklama kaydının temel alanlarını içeren basitleştirilmiş bir tanım
            # veya tam AttendanceResponse (ama details olmadan)
            $ref: '#/definitions/AttendanceResponseSummary' # Veya yeni bir şema tanımla
        examples:
          application/json:
            - id: 15
              course_id: 1
              date: "2024-03-15"
              lesson_number: 1
              type: "FACE"
              photo_path: "/static/attendance/attendance_1_2024-03-15_1_103000.jpg"
              total_students: 20
              recognized_students: 18
              unrecognized_students: 2
              created_by: 2
              created_at: "2024-03-15T10:30:05Z"
              updated_at: "2024-03-15T10:30:05Z"
            - id: 18
              course_id: 1
              date: "2024-03-18"
              lesson_number: 1
              type: "FACE"
              photo_path: "/static/attendance/attendance_1_2024-03-18_1_103215.jpg"
              total_students: 20
              recognized_students: 19
              unrecognized_students: 1
              created_by: 2
              created_at: "2024-03-18T10:32:20Z"
              updated_at: "2024-03-18T10:32:20Z"
      401:
        description: Yetkisiz. Geçerli token sağlanmadı.
      403:
        description: Yasak. Bu dersin kayıtlarını görme yetkiniz yok.
      404:
        description: Belirtilen ID'ye sahip ders bulunamadı.
    definitions:
      # Yanıtı basitleştirmek için yeni bir şema (details olmadan)
      AttendanceResponseSummary:
         type: object
         description: Bir yoklama kaydının öğrenci detayları hariç özet bilgileri.
         properties:
            id:
              type: integer
              example: 15
            course_id:
              type: integer
              example: 1
            date:
              type: string
              format: date
              example: "2024-03-15"
            lesson_number:
              type: integer
              example: 1
            type:
              type: string
              enum: ["FACE", "EMOTION", "FACE_EMOTION"]
              example: "FACE"
            photo_path:
              type: string
              nullable: true
              example: "/static/attendance/att_1.jpg"
            total_students:
              type: integer
              example: 20
            recognized_students:
              type: integer
              example: 18
            unrecognized_students:
              type: integer
              example: 2
            created_by:
              type: integer
              example: 2
            created_at:
              type: string
              format: date-time
            updated_at:
              type: string
              format: date-time
    """
    # Önce dersin varlığını kontrol et
    course = data_service.find_one(COURSES_FILE, id=course_id)
    if not course:
        return jsonify({"message": "Ders bulunamadı"}), 404

    # --- Yetkilendirme kontrolü: Giriş yapan kullanıcının bu dersin öğretmeni veya Admin olduğundan emin ol --- 
    current_role, current_user_id = get_current_user_role_and_id() 
    if current_role is None or current_user_id is None:
         return jsonify({"message": "Geçersiz token kimliği veya kullanıcı bulunamadı"}), 401

    teacher = data_service.find_one(TEACHERS_FILE, id=course.get('teacher_id'))
    is_teacher_of_course = teacher and teacher.get('user_id') == current_user_id
    is_admin = current_role == "ADMIN"

    if not is_teacher_of_course and not is_admin:
        return jsonify({"message": "Yasak: Sadece dersin öğretmeni veya admin bu kayıtları görebilir."}), 403
    # --- Yetkilendirme Sonu --- 
    
    # Ders için yoklama kayıtlarını getir
    attendance_records = data_service.find_many(ATTENDANCE_FILE, course_id=course_id)
    # İsteğe bağlı: Tarih/ders numarasına göre sırala
    attendance_records.sort(key=lambda x: (x.get('date', ''), x.get('lesson_number', 0)), reverse=True) # En yeniden eskiye
    
    # Yanıtı şekillendirmek için Pydantic modelini kullan (örn. detayları hariç tut)
    # Şimdilik, data_service'den gelen ham listeyi döndür
    # VEYA tanımlanan AttendanceResultSummary şemasına uydur:
    summary_list = []
    for record in attendance_records:
         summary_data = {
            key: record.get(key) for key in AttendanceResultSummary.__fields__.keys() # Renamed from AttendanceResponseSummary
         }
         summary_list.append(summary_data)

    return jsonify(summary_list), 200

@attendance_bp.route('/course/<int:course_id>/student/<int:student_id>', methods=['GET'])
@jwt_required() # JWT token'ının gerekli olduğunu belirtmek için eklendi
def get_student_attendance_for_course(course_id, student_id):
    """
    Belirli bir dersteki belirli bir öğrencinin tüm yoklama detaylarını getirir.
    Dersin öğretmeni, Admin veya öğrencinin kendisi erişebilir.
    ---    
    tags:
      - Yoklama (Attendance)
      - Öğrenciler (Students)
      - Dersler (Courses)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: course_id
        type: integer
        required: true
        description: Dersin ID'si.
        example: 1
      - in: path
        name: student_id
        type: integer
        required: true
        description: Öğrencinin ID'si.
        example: 5
    responses:
      200:
        description: Öğrencinin dersteki yoklama detaylarının listesi.
        schema:
          $ref: '#/definitions/StudentAttendanceReportResponse' # Raporlar bölümündeki tanım kullanılabilir veya benzeri
        examples:
          application/json:
            course_info:
              id: 1
              code: "CS101"
              name: "Bilgisayar Bilimlerine Giriş"
            student_info:
              id: 5
              student_number: "S12345"
              user:
                id: 10
                first_name: "Ayşe"
                last_name: "Kaya"
                email: "ayse.kaya@ornek.com"
            attendance_details:
              - id: 101
                attendance_id: 15
                student_id: 5
                status: "PRESENT"
                confidence: 0.95
                emotion: null
                # ... diğer detay alanları ...
                date: "2024-03-15"
              - id: 115
                attendance_id: 18
                student_id: 5
                status: "PRESENT"
                confidence: 0.91
                emotion: null
                # ... diğer detay alanları ...
                date: "2024-03-18"
              # ... (öğrencinin diğer yoklama kayıtları)
      400:
        description: Öğrenci belirtilen derse kayıtlı değil.
      401:
        description: Yetkisiz. Geçerli token sağlanmadı veya geçersiz.
      403:
        description: Yasak. Bu bilgilere erişim yetkiniz yok.
      404:
        description: Belirtilen ID'ye sahip Ders veya Öğrenci bulunamadı.
    definitions:
      # Basitleştirilmiş Kurs Şeması (eğer globalde yoksa)
      CourseResponseShort:
         type: object
         properties:
             id:
               type: integer
             code:
               type: string
             name:
               type: string
    """
    # --- Yeni Yetkilendirme Kontrolü ---
    # Artık @jwt_required() olduğu için get_current_user_role_and_id() güvenle çağrılabilir
    current_role, current_user_id = get_current_user_role_and_id()
    if current_role is None or current_user_id is None:
        # Bu durum normalde @jwt_required() sonrası olmamalı ama yine de kontrol edilebilir
        return jsonify({"message": "Geçersiz token kimliği veya kullanıcı bulunamadı"}), 401

    course = data_service.find_one(COURSES_FILE, id=course_id)
    if not course: return jsonify({"message": "Ders bulunamadı"}), 404

    is_allowed = False
    if current_role == "ADMIN":
        is_allowed = True
    elif current_role == "TEACHER":
        teacher = data_service.find_one(TEACHERS_FILE, id=course.get('teacher_id'))
        if teacher and teacher.get('user_id') == current_user_id:
            is_allowed = True
    elif current_role == "STUDENT":
        # İstek yapan öğrencinin user_id'si ile ilişkili student_id'yi bulmamız lazım
        student_profile = data_service.find_one(STUDENTS_FILE, user_id=current_user_id)
        # URL'deki student_id ile istek yapanın student_id'si eşleşiyor mu?
        if student_profile and student_profile.get('id') == student_id:
            is_allowed = True

    if not is_allowed:
        return jsonify({"message": "Yasak: Bu bilgilere erişim yetkiniz yok."}), 403
    # --- Yetkilendirme Sonu ---

    student = data_service.find_one(STUDENTS_FILE, id=student_id)
    if not student: return jsonify({"message": "Öğrenci bulunamadı"}), 404

    # Kayıt kontrolü (Öğrencinin derse kayıtlı olduğundan emin ol)
    enrollment = data_service.find_one(STUDENT_COURSE_FILE, course_id=course_id, student_id=student_id)
    if not enrollment:
        # Öğrencinin kendisi bile olsa, kayıtlı değilse 400 döndürmek mantıklı olabilir.
        # Ya da belki sadece öğretmene/admin'e 400 döndürülür, öğrenci boş liste alır?
        # Şimdilik tutarlılık için 400 döndürelim.
        return jsonify({"message": "Öğrenci bu derse kayıtlı değil"}), 400

    # Ders için tüm yoklama ID'lerini bul
    course_attendance_records = data_service.find_many(ATTENDANCE_FILE, course_id=course_id)
    course_attendance_ids = [att['id'] for att in course_attendance_records]

    # Öğrenci bilgisi için yardımcı fonksiyonu import et
    from app.routes.students import _get_student_with_user
    # Yanıt için temel öğrenci ve kurs bilgilerini hazırla
    student_info = _get_student_with_user(student.copy()) # Kopya kullan
    course_info = { # Sadece temel bilgileri al
        "id": course.get('id'),
        "code": course.get('code'),
        "name": course.get('name')
    }

    if not course_attendance_ids:
        # Henüz yoklama alınmamışsa boş liste döndür
        return jsonify({
            "course_info": course_info, 
            "student_info": student_info, 
            "attendance_details": []
        }), 200

    # Bu öğrencinin o yoklama kayıtlarındaki detaylarını bul
    all_details = data_service.read_data(ATTENDANCE_DETAILS_FILE)
    student_details_raw = [
        detail for detail in all_details 
        if detail.get('attendance_id') in course_attendance_ids and detail.get('student_id') == student_id
    ]

    # Detaylara bağlam için tarih bilgisini ekle
    att_id_to_info = {att['id']: {'date': att['date'], 'lesson_number': att['lesson_number']} for att in course_attendance_records}
    student_details_final = []
    for detail in student_details_raw:
         att_info = att_id_to_info.get(detail['attendance_id'])
         if att_info:
             detail['date'] = att_info.get('date')
             detail['lesson_number'] = att_info.get('lesson_number')
         # Detay yanıtına öğrenci bilgisini (tekrar) eklemeye gerek yok, ana yanıtta var
         student_details_final.append(detail)
    
    # İsteğe bağlı: Detayları tarihe göre sırala
    student_details_final.sort(key=lambda x: (x.get('date') or '', x.get('lesson_number') or 0), reverse=True)

    return jsonify({
        "course_info": course_info, 
        "student_info": student_info,
        "attendance_details": student_details_final
        }), 200


@attendance_bp.route('/<int:attendance_id>/students/<int:student_id>', methods=['POST'])
@teacher_required # Sadece dersin öğretmeni veya Admin
def manually_update_student_attendance(attendance_id, student_id):
    """
    Belirli bir yoklama kaydındaki bir öğrencinin durumunu manuel olarak günceller.
    (Örn: Yüz tanıma hatasını düzeltme, izinli ekleme vb.)
    Yalnızca dersin öğretmeni veya Admin tarafından yapılabilir.
    ---    
    tags:
      - Yoklama (Attendance)
      - Öğrenciler (Students)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: attendance_id
        type: integer
        required: true
        description: Güncellenecek ana yoklama kaydının ID'si.
        example: 15
      - in: path
        name: student_id
        type: integer
        required: true
        description: Durumu güncellenecek öğrencinin ID'si.
        example: 12
      - in: body
        name: body
        required: true
        description: Öğrencinin yeni yoklama durumu.
        schema:
          $ref: '#/definitions/AttendanceManualUpdate'
    responses:
      200:
        description: Durum başarıyla güncellendi. Güncellenmiş yoklama detayını döndürür.
        schema:
          $ref: '#/definitions/AttendanceDetailResponse' # Güncellenmiş detayı döndür
        examples:
          application/json:
              id: 102 # Güncellenen veya oluşturulan detay ID'si
              attendance_id: 15
              student_id: 12
              status: "PRESENT" # Yeni durum
              confidence: null # Manuel güncelleme, güven yok
              emotion: null
              emotion_confidence: null
              emotion_statistics: null
              created_at: "2024-03-15T10:30:05Z"
              updated_at: "2024-03-18T14:00:00Z" # Yeni güncelleme zamanı
              student:
                  id: 12
                  student_number: "S54321"
                  user:
                    id: 15
                    first_name: "Ali"
                    last_name: "Veli"
                    email: "ali.veli@ornek.com"
      201:
        description: Öğrenci için daha önce detay kaydı yoktu, manuel olarak oluşturuldu ve durum ayarlandı.
        schema:
          $ref: '#/definitions/AttendanceDetailResponse'
      400:
        description: |-
          Geçersiz durum bilgisi veya öğrenci yoklamanın ilişkili olduğu derse kayıtlı değil.
          Sebepleri:
          - İstek gövdesi (`body`) eksik veya geçersiz.
          - Sağlanan `status` değeri geçersiz (izin verilenler: PRESENT, ABSENT, LATE, EXCUSED).
          - Öğrenci, bu yoklama kaydının ait olduğu derse kayıtlı değil.
        examples:
          application/json (Invalid Status): { "message": "Doğrulama Hatası", "errors": [{"field": "status", "message": "Geçersiz durum değeri"}] }
          application/json (Not Enrolled): { "message": "Öğrenci, bu yoklama kaydının ait olduğu derse kayıtlı değil" }
      401:
        description: Yetkisiz. Geçerli token sağlanmadı.
      403:
        description: Yasak. Bu kaydı değiştirme yetkiniz yok.
      404:
        description: Belirtilen ID'ye sahip Yoklama kaydı veya Öğrenci bulunamadı.
    definitions:
      AttendanceManualUpdate:
        type: object
        description: Manuel yoklama güncellemesi için istek gövdesi.
        required:
          - status
        properties:
          status:
            type: string
            enum: ["PRESENT", "ABSENT", "LATE", "EXCUSED"]
            description: Öğrencinin yeni durumu.
            example: "PRESENT"
    """
    attendance_record = data_service.find_one(ATTENDANCE_FILE, id=attendance_id)
    if not attendance_record: return jsonify({"message": "Yoklama kaydı bulunamadı"}), 404

    # Yetkilendirme kontrolü (GET /attendance/{id} ile aynı)
    # --- Mevcut kullanıcı rolünü ve INT ID'sini al --- 
    current_role, current_user_id = get_current_user_role_and_id() 
    if current_role is None or current_user_id is None:
         return jsonify({"message": "Geçersiz token kimliği veya kullanıcı bulunamadı"}), 401
    # --- Bitiş --- 

    course_id = attendance_record.get('course_id')
    course = data_service.find_one(COURSES_FILE, id=course_id)
    if not course: return jsonify({"message": "İç tutarsızlık: Ders bulunamadı."}), 500
    
    teacher = data_service.find_one(TEACHERS_FILE, id=course.get('teacher_id'))
    # Use current_user_id (int) for comparison
    is_teacher_of_course = teacher and teacher.get('user_id') == current_user_id
    # Use current_role for comparison
    is_admin = current_role == "ADMIN"
    if not is_teacher_of_course and not is_admin:
        return jsonify({"message": "Forbidden: You do not have permission to modify this record."}), 403

    # Validate input status
    json_data = request.get_json()
    if not json_data: return jsonify({"message": "No input data provided"}), 400
    try:
        update_data = AttendanceManualUpdate(**json_data)
        new_status = update_data.status.upper()
    except ValidationError as e:
        return jsonify({"message": "Validation Error", "errors": e.errors()}), 400

    # Check if student exists and is enrolled in this course
    student = data_service.find_one(STUDENTS_FILE, id=student_id)
    if not student: return jsonify({"message": "Student not found"}), 404
    enrollment = data_service.find_one(STUDENT_COURSE_FILE, course_id=course_id, student_id=student_id)
    if not enrollment:
        return jsonify({"message": "Student is not enrolled in the course for this attendance record"}), 400

    # Find the existing detail record for this student in this attendance
    existing_detail = data_service.find_one(ATTENDANCE_DETAILS_FILE, attendance_id=attendance_id, student_id=student_id)

    now = default_datetime()
    updates = {"status": new_status, "updated_at": now}
    
    if existing_detail:
        detail_id = existing_detail['id']
        updated_detail = data_service.update_item(ATTENDANCE_DETAILS_FILE, detail_id, updates)
        if not updated_detail:
             return jsonify({"message": "Failed to update attendance detail."}), 500
        response_status = 200
    else:
        # If no detail record exists, create one (e.g., manually marking present/excused someone missed by face rec)
        new_detail = {
            "attendance_id": attendance_id,
            "student_id": student_id,
            "status": new_status,
            "confidence": None, # Manual update
            "emotion": None,
            "emotion_confidence": None,
            "emotion_statistics": None,
            "created_at": now,
            "updated_at": now
        }
        try:
             updated_detail = data_service.add_item(ATTENDANCE_DETAILS_FILE, new_detail) 
             response_status = 201
        except Exception as e:
             current_app.logger.error(f"Failed to add manual attendance detail: {e}")
             return jsonify({"message": "Failed to add manual attendance detail."}), 500
    
    # ** Important: Update the summary counts in the main attendance record **
    all_details_for_att = data_service.find_many(ATTENDANCE_DETAILS_FILE, attendance_id=attendance_id)
    present_count = sum(1 for d in all_details_for_att if d.get('status') == 'PRESENT')
    total_enrolled = attendance_record.get('total_students', len(data_service.find_many(STUDENT_COURSE_FILE, course_id=course_id)))
    absent_count = total_enrolled - present_count # Recalculate based on PRESENT count

    main_updates = {
        "recognized_students": present_count, # Assuming recognized ~ present for summary
        "unrecognized_students": absent_count,
        "updated_at": now
    }
    data_service.update_item(ATTENDANCE_FILE, attendance_id, main_updates)
    # --- End summary update ---

    # Add student info to response
    if updated_detail:
        from app.routes.students import _get_student_with_user
        student_info = _get_student_with_user(student.copy())
        if student_info:
             updated_detail['student'] = student_info.get('user', {}) # Add basic user info
    
    return jsonify(updated_detail), response_status 