# Yoklama API Endpoint'leri

Bu dokümantasyon, yoklama sistemi için mevcut tüm API endpoint'lerini içermektedir. Frontend geliştiricileri için referans olarak hazırlanmıştır.

## Kimlik Doğrulama

Tüm endpoint'ler JWT tabanlı kimlik doğrulama gerektirmektedir. İstekleri yaparken `Authorization` başlığı aşağıdaki şekilde ayarlanmalıdır:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 1. Yoklama Oluşturma

Bir sınıf fotoğrafı yükleyerek ve yüzleri işleyerek yeni bir yoklama kaydı oluşturur. EMOTION türü seçilirse yaş, cinsiyet ve duygu analizi de yapılır.

### İstek

```
POST /api/attendance/
```

**Yetki**: Sadece dersin öğretmeni veya Admin kullanabilir.

**İçerik Tipi**: multipart/form-data

**Form Parametreleri**:

| Alan          | Tip      | Zorunlu | Açıklama                                                |
|---------------|----------|---------|----------------------------------------------------------|
| file          | file     | Evet    | Sınıf fotoğrafı (png, jpg, jpeg)                        |
| course_id     | integer  | Evet    | Dersin ID'si                                            |
| date          | string   | Evet    | Yoklama tarihi, YYYY-MM-DD formatında (örn. "2024-06-01") |
| lesson_number | integer  | Evet    | Ders saati numarası (örn. 1, 2)                         |
| type          | string   | Evet    | "FACE", "EMOTION", "FACE_EMOTION" değerlerinden biri     |

**Örnek İstek (curl)**:

```bash
curl -X POST "http://localhost:5000/api/attendance/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sinif_fotografi.jpg" \
  -F "course_id=1" \
  -F "date=2024-06-01" \
  -F "lesson_number=1" \
  -F "type=EMOTION"
```

**Örnek İstek (JavaScript)**:

```javascript
const formData = new FormData();
formData.append('file', fotoğrafDosyası); // File nesnesi
formData.append('course_id', 1);
formData.append('date', '2024-06-01');
formData.append('lesson_number', 1);
formData.append('type', 'EMOTION');

const response = await fetch('http://localhost:5000/api/attendance/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
  },
  body: formData
});
```

### Yanıt

**Başarılı Yanıt (201 Created)**:

```json
{
  "attendance_id": 25,
  "recognized_count": 18,
  "unrecognized_count": 2,
  "total_students": 20,
  "emotion_statistics": {
    "happy": 15,
    "neutral": 3,
    "sad": 2
  },
  "results": [
    {
      "student_id": 5,
      "status": "PRESENT",
      "confidence": 0.95,
      "emotion": "happy",
      "estimated_age": 21,
      "estimated_gender": "Woman",
      "student": {
        "id": 5,
        "student_number": "S12345",
        "first_name": "Ayşe",
        "last_name": "Kaya",
        "email": "ayse.kaya@ornek.com"
      }
    },
    {
      "student_id": 12,
      "status": "PRESENT",
      "confidence": 0.87,
      "emotion": "neutral",
      "estimated_age": 20,
      "estimated_gender": "Man",
      "student": {
        "id": 12,
        "student_number": "S54321",
        "first_name": "Ali",
        "last_name": "Veli",
        "email": "ali.veli@ornek.com"
      }
    },
    {
      "student_id": 8,
      "status": "ABSENT",
      "confidence": null,
      "emotion": null,
      "estimated_age": null,
      "estimated_gender": null,
      "student": {
        "id": 8,
        "student_number": "S98765",
        "first_name": "Mehmet",
        "last_name": "Yılmaz",
        "email": "mehmet.yilmaz@ornek.com"
      }
    }
    // ... diğer öğrenciler
  ]
}
```

**Olası Hata Yanıtları**:

- `400 Bad Request`: Geçersiz istek (eksik dosya, yanlış form alanları, resimde yüz yok)
- `401 Unauthorized`: Kimlik doğrulama hatası
- `403 Forbidden`: Yetki hatası (kullanıcı dersin öğretmeni değil)
- `404 Not Found`: Ders veya derse kayıtlı öğrenci bulunamadı
- `500 Internal Server Error`: Sunucu hatası

## 2. Yoklama Kaydını Getirme

Belirli bir yoklama kaydının tüm detaylarını (öğrenci durumları dahil) getirir.

### İstek

```
GET /api/attendance/{attendance_id}
```

**Yetki**: Sadece dersin öğretmeni veya Admin kullanabilir.

**URL Parametreleri**:

| Parametre    | Tip      | Açıklama                         |
|--------------|----------|----------------------------------|
| attendance_id | integer  | Getirilecek yoklama kaydının ID'si |

**Örnek İstek (curl)**:

```bash
curl -X GET "http://localhost:5000/api/attendance/15" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Örnek İstek (JavaScript)**:

```javascript
const response = await fetch('http://localhost:5000/api/attendance/15', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
  }
});
```

### Yanıt

**Başarılı Yanıt (200 OK)**:

```json
{
  "id": 15,
  "course_id": 1,
  "date": "2024-03-15",
  "lesson_number": 1,
  "type": "FACE",
  "photo_path": "/static/attendance/attendance_1_2024-03-15_1_103000.jpg",
  "total_students": 20,
  "recognized_students": 18,
  "unrecognized_students": 2,
  "emotion_statistics": {
    "happy": 10,
    "neutral": 6,
    "sad": 2,
    "angry": 0
  },
  "created_by": 2,
  "created_at": "2024-03-15T10:30:05Z",
  "updated_at": "2024-03-15T10:30:05Z",
  "details": [
    {
      "id": 101,
      "attendance_id": 15,
      "student_id": 5,
      "status": "PRESENT",
      "confidence": 0.95,
      "emotion": "happy",
      "estimated_age": 21,
      "estimated_gender": "Woman",
      "created_at": "2024-03-15T10:30:05Z",
      "updated_at": "2024-03-15T10:30:05Z",
      "student": {
        "id": 5,
        "student_number": "S12345",
        "user": {
          "id": 10,
          "first_name": "Ayşe",
          "last_name": "Kaya",
          "email": "ayse.kaya@ornek.com"
        }
      }
    },
    // ... diğer öğrenciler
  ]
}
```

**Olası Hata Yanıtları**:

- `401 Unauthorized`: Kimlik doğrulama hatası
- `403 Forbidden`: Yetki hatası (kullanıcı dersin öğretmeni değil)
- `404 Not Found`: Yoklama kaydı bulunamadı
- `500 Internal Server Error`: Sunucu hatası

## 3. Derse Ait Yoklama Kayıtlarını Getirme

Belirli bir derse ait tüm yoklama kayıtlarını (özet görünüm, detaylar hariç) getirir.

### İstek

```
GET /api/attendance/course/{course_id}
```

**Yetki**: Sadece dersin öğretmeni veya Admin kullanabilir.

**URL Parametreleri**:

| Parametre  | Tip      | Açıklama                                   |
|------------|----------|------------------------------------------|
| course_id  | integer  | Yoklama kayıtları getirilecek dersin ID'si |

**Örnek İstek (curl)**:

```bash
curl -X GET "http://localhost:5000/api/attendance/course/1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Örnek İstek (JavaScript)**:

```javascript
const response = await fetch('http://localhost:5000/api/attendance/course/1', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
  }
});
```

### Yanıt

**Başarılı Yanıt (200 OK)**:

```json
[
  {
    "id": 15,
    "course_id": 1,
    "date": "2024-03-15",
    "lesson_number": 1,
    "type": "FACE",
    "photo_path": "/static/attendance/attendance_1_2024-03-15_1_103000.jpg",
    "total_students": 20,
    "recognized_students": 18,
    "unrecognized_students": 2,
    "created_by": 2,
    "created_at": "2024-03-15T10:30:05Z",
    "updated_at": "2024-03-15T10:30:05Z"
  },
  {
    "id": 18,
    "course_id": 1,
    "date": "2024-03-18",
    "lesson_number": 1,
    "type": "FACE",
    "photo_path": "/static/attendance/attendance_1_2024-03-18_1_103215.jpg",
    "total_students": 20,
    "recognized_students": 19,
    "unrecognized_students": 1,
    "created_by": 2,
    "created_at": "2024-03-18T10:32:20Z",
    "updated_at": "2024-03-18T10:32:20Z"
  }
  // ... diğer yoklama kayıtları
]
```

**Olası Hata Yanıtları**:

- `401 Unauthorized`: Kimlik doğrulama hatası
- `403 Forbidden`: Yetki hatası (kullanıcı dersin öğretmeni değil)
- `404 Not Found`: Ders bulunamadı
- `500 Internal Server Error`: Sunucu hatası

## 4. Öğrencinin Dersteki Yoklama Bilgilerini Getirme

Belirli bir öğrencinin belirli bir dersteki tüm yoklama detaylarını getirir.

### İstek

```
GET /api/attendance/course/{course_id}/student/{student_id}
```

**Yetki**: Sadece dersin öğretmeni veya Admin kullanabilir.

**URL Parametreleri**:

| Parametre  | Tip      | Açıklama                                |
|------------|----------|----------------------------------------|
| course_id  | integer  | Dersin ID'si                           |
| student_id | integer  | Öğrencinin ID'si                       |

**Örnek İstek (curl)**:

```bash
curl -X GET "http://localhost:5000/api/attendance/course/1/student/5" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Örnek İstek (JavaScript)**:

```javascript
const response = await fetch('http://localhost:5000/api/attendance/course/1/student/5', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
  }
});
```

### Yanıt

**Başarılı Yanıt (200 OK)**:

```json
{
  "course_info": {
    "id": 1,
    "code": "CS101",
    "name": "Bilgisayar Bilimlerine Giriş"
  },
  "student_info": {
    "id": 5,
    "student_number": "S12345",
    "user": {
      "id": 10,
      "first_name": "Ayşe",
      "last_name": "Kaya",
      "email": "ayse.kaya@ornek.com"
    }
  },
  "attendance_details": [
    {
      "id": 101,
      "attendance_id": 15,
      "student_id": 5,
      "status": "PRESENT",
      "confidence": 0.95,
      "emotion": "happy",
      "estimated_age": 21,
      "estimated_gender": "Woman",
      "created_at": "2024-03-15T10:30:05Z",
      "updated_at": "2024-03-15T10:30:05Z",
      "date": "2024-03-15",
      "lesson_number": 1
    },
    {
      "id": 115,
      "attendance_id": 18,
      "student_id": 5,
      "status": "PRESENT",
      "confidence": 0.91,
      "emotion": "neutral",
      "estimated_age": 21, 
      "estimated_gender": "Woman",
      "created_at": "2024-03-18T10:32:20Z",
      "updated_at": "2024-03-18T10:32:20Z",
      "date": "2024-03-18",
      "lesson_number": 1
    }
    // ... diğer yoklama kayıtları
  ]
}
```

**Olası Hata Yanıtları**:

- `400 Bad Request`: Öğrenci derse kayıtlı değil
- `401 Unauthorized`: Kimlik doğrulama hatası
- `403 Forbidden`: Yetki hatası (kullanıcı dersin öğretmeni değil)
- `404 Not Found`: Ders veya öğrenci bulunamadı
- `500 Internal Server Error`: Sunucu hatası

## 5. Öğrenci Yoklama Durumu Manuel Güncelleme

Belirli bir yoklama kaydındaki bir öğrencinin durumunu manuel olarak günceller.

### İstek

```
POST /api/attendance/{attendance_id}/students/{student_id}
```

**Yetki**: Sadece dersin öğretmeni veya Admin kullanabilir.

**URL Parametreleri**:

| Parametre     | Tip      | Açıklama                               |
|---------------|----------|----------------------------------------|
| attendance_id | integer  | Güncellenecek yoklama kaydının ID'si   |
| student_id    | integer  | Durumu güncellenecek öğrencinin ID'si  |

**İçerik Tipi**: application/json

**Body Parametreleri**:

```json
{
  "status": "PRESENT" 
}
```

`status` değeri şunlardan biri olmalıdır: "PRESENT", "ABSENT", "LATE", "EXCUSED"

**Örnek İstek (curl)**:

```bash
curl -X POST "http://localhost:5000/api/attendance/15/students/12" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"status": "PRESENT"}'
```

**Örnek İstek (JavaScript)**:

```javascript
const response = await fetch('http://localhost:5000/api/attendance/15/students/12', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    status: 'PRESENT'
  })
});
```

### Yanıt

**Başarılı Yanıt (200 OK)** - Varolan kayıt güncellendi:

```json
{
  "id": 102,
  "attendance_id": 15,
  "student_id": 12,
  "status": "PRESENT",
  "confidence": null,
  "emotion": null,
  "estimated_age": null,
  "estimated_gender": null,
  "created_at": "2024-03-15T10:30:05Z",
  "updated_at": "2024-03-18T14:00:00Z",
  "student": {
    "id": 12,
    "student_number": "S54321",
    "user": {
      "id": 15,
      "first_name": "Ali",
      "last_name": "Veli",
      "email": "ali.veli@ornek.com"
    }
  }
}
```

**Başarılı Yanıt (201 Created)** - Yeni kayıt oluşturuldu:

Yanıt formatı 200 yanıtı ile aynıdır, fakat HTTP durumu 201'dir.

**Olası Hata Yanıtları**:

- `400 Bad Request`: Geçersiz durum değeri veya öğrenci derse kayıtlı değil
- `401 Unauthorized`: Kimlik doğrulama hatası
- `403 Forbidden`: Yetki hatası (kullanıcı dersin öğretmeni değil)
- `404 Not Found`: Yoklama kaydı veya öğrenci bulunamadı
- `500 Internal Server Error`: Sunucu hatası
