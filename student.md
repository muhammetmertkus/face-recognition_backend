# Öğrenci API Endpoint'leri

Bu dokümantasyon, öğrencilerle ilgili tüm API endpoint'lerini içermektedir. Frontend geliştiricileri için öğrenci işlemleri referans olarak hazırlanmıştır.

## Kimlik Doğrulama

Tüm endpoint'ler JWT tabanlı kimlik doğrulama gerektirmektedir. İstekleri yaparken `Authorization` başlığı aşağıdaki şekilde ayarlanmalıdır:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 1. Öğrenci Listesini Getirme

Sistemdeki tüm öğrencilerin listesini kullanıcı detaylarıyla birlikte getirir.

### İstek

```
GET /api/students/
```

**Yetki**: Sadece Öğretmen ve Admin kullanabilir.

**Örnek İstek (curl)**:

```bash
curl -X GET "http://localhost:5000/api/students/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Örnek İstek (JavaScript)**:

```javascript
const response = await fetch('http://localhost:5000/api/students/', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
  }
});

const students = await response.json();
```

### Yanıt

**Başarılı Yanıt (200 OK)**:

```json
[
  {
    "id": 5,
    "user_id": 10,
    "student_number": "S12345",
    "department": "Bilgisayar Mühendisliği",
    "face_photo_url": "/uploads/faces/student_5_foto.jpg",
    "created_at": "2024-01-15T14:00:00Z",
    "updated_at": "2024-01-16T09:30:00Z",
    "user": {
      "id": 10,
      "email": "ayse.kaya@ornek.com",
      "first_name": "Ayşe",
      "last_name": "Kaya",
      "role": "STUDENT",
      "is_active": true
    }
  },
  {
    "id": 6,
    "user_id": 11,
    "student_number": "S67890",
    "department": "Elektrik Mühendisliği",
    "face_photo_url": null,
    "created_at": "2024-01-16T11:20:00Z",
    "updated_at": "2024-01-16T11:20:00Z",
    "user": {
      "id": 11,
      "email": "mehmet.can@ornek.com",
      "first_name": "Mehmet",
      "last_name": "Can",
      "role": "STUDENT",
      "is_active": true
    }
  }
]
```

**Olası Hata Yanıtları**:

- `401 Unauthorized`: Kimlik doğrulama hatası
- `403 Forbidden`: Yetki hatası (kullanıcı öğretmen veya admin değil)

## 2. Öğrenci Detaylarını Getirme

Belirli bir öğrencinin detaylarını getirir (yaş/cinsiyet tahminleri dahil).

### İstek

```
GET /api/students/{student_id}
```

**Yetki**: Öğrencinin kendisi, Öğretmen veya Admin kullanabilir.

**URL Parametreleri**:

| Parametre  | Tip      | Açıklama                         |
|------------|----------|----------------------------------|
| student_id | integer  | Detayları alınacak öğrencinin ID'si |

**Örnek İstek (curl)**:

```bash
curl -X GET "http://localhost:5000/api/students/5" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Örnek İstek (JavaScript)**:

```javascript
const response = await fetch('http://localhost:5000/api/students/5', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
  }
});

const studentDetails = await response.json();
```

### Yanıt

**Başarılı Yanıt (200 OK)**:

```json
{
  "id": 5,
  "user_id": 10,
  "student_number": "S12345",
  "department": "Bilgisayar Mühendisliği",
  "face_photo_url": "/uploads/faces/student_5_foto.jpg",
  "estimated_age": 22,
  "estimated_gender": "Woman",
  "created_at": "2024-01-15T14:00:00Z",
  "updated_at": "2024-01-16T09:30:00Z",
  "user": {
    "id": 10,
    "email": "ayse.kaya@ornek.com",
    "first_name": "Ayşe",
    "last_name": "Kaya",
    "role": "STUDENT",
    "is_active": true
  }
}
```

**Olası Hata Yanıtları**:

- `401 Unauthorized`: Kimlik doğrulama hatası
- `403 Forbidden`: Yetki hatası (kullanıcı öğrencinin kendisi, öğretmen veya admin değil)
- `404 Not Found`: Belirtilen ID'ye sahip öğrenci bulunamadı

## 3. Öğrenci Oluşturma

Yeni bir öğrenci oluşturur. Bu işlem auth endpoint'i üzerinden gerçekleştirilir.

### İstek

```
POST /api/auth/register
```

**Yetki**: Admin yetkilendirmesi gereklidir.

**İçerik Tipi**: application/json

**Body Parametreleri**:

```json
{
  "email": "yeni.ogrenci@ornek.com",
  "password": "GucluSifre123!",
  "first_name": "Yeni",
  "last_name": "Öğrenci",
  "role": "STUDENT",
  "student_number": "S123456",
  "department": "Yazılım Mühendisliği"
}
```

**Örnek İstek (curl)**:

```bash
curl -X POST "http://localhost:5000/api/auth/register" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "email": "yeni.ogrenci@ornek.com",
    "password": "GucluSifre123!",
    "first_name": "Yeni",
    "last_name": "Öğrenci",
    "role": "STUDENT",
    "student_number": "S123456",
    "department": "Yazılım Mühendisliği"
  }'
```

**Örnek İstek (JavaScript)**:

```javascript
const response = await fetch('http://localhost:5000/api/auth/register', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'yeni.ogrenci@ornek.com',
    password: 'GucluSifre123!',
    first_name: 'Yeni',
    last_name: 'Öğrenci',
    role: 'STUDENT',
    student_number: 'S123456',
    department: 'Yazılım Mühendisliği'
  })
});

const result = await response.json();
```

### Yanıt

**Başarılı Yanıt (201 Created)**:

```json
{
  "message": "Kullanıcı başarıyla oluşturuldu",
  "user": {
    "id": 25,
    "email": "yeni.ogrenci@ornek.com",
    "first_name": "Yeni",
    "last_name": "Öğrenci",
    "role": "STUDENT",
    "is_active": true
  },
  "student": {
    "id": 12,
    "user_id": 25,
    "student_number": "S123456",
    "department": "Yazılım Mühendisliği",
    "face_photo_url": null,
    "created_at": "2024-06-01T15:20:30Z",
    "updated_at": "2024-06-01T15:20:30Z"
  }
}
```

## 4. Öğrenci Profili Güncelleme

Bir öğrencinin profil bilgilerini günceller.

### İstek

```
PUT /api/students/{student_id}
```

**Yetki**: Sadece Admin kullanabilir.

**URL Parametreleri**:

| Parametre  | Tip      | Açıklama                         |
|------------|----------|----------------------------------|
| student_id | integer  | Güncellenecek öğrencinin ID'si    |

**İçerik Tipi**: application/json

**Body Parametreleri**:

```json
{
  "student_number": "S12345-NEW",
  "department": "Yazılım Mühendisliği"
}
```

Tüm alanlar isteğe bağlıdır, sadece değiştirilmek istenen alanlar gönderilmelidir.

**Örnek İstek (curl)**:

```bash
curl -X PUT "http://localhost:5000/api/students/5" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "student_number": "S12345-NEW",
    "department": "Yazılım Mühendisliği"
  }'
```

**Örnek İstek (JavaScript)**:

```javascript
const response = await fetch('http://localhost:5000/api/students/5', {
  method: 'PUT',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    student_number: 'S12345-NEW',
    department: 'Yazılım Mühendisliği'
  })
});

const updatedStudent = await response.json();
```

### Yanıt

**Başarılı Yanıt (200 OK)**:

```json
{
  "id": 5,
  "user_id": 10,
  "student_number": "S12345-NEW",
  "department": "Yazılım Mühendisliği",
  "face_photo_url": "/uploads/faces/student_5_foto.jpg",
  "created_at": "2024-01-15T14:00:00Z",
  "updated_at": "2024-06-01T10:15:20Z",
  "user": {
    "id": 10,
    "email": "ayse.kaya@ornek.com",
    "first_name": "Ayşe",
    "last_name": "Kaya",
    "role": "STUDENT",
    "is_active": true
  }
}
```

**Olası Hata Yanıtları**:

- `400 Bad Request`: Geçersiz istek (örn. başka bir öğrenciye ait öğrenci numarası)
- `401 Unauthorized`: Kimlik doğrulama hatası
- `403 Forbidden`: Yetki hatası (kullanıcı Admin değil)
- `404 Not Found`: Belirtilen ID'ye sahip öğrenci bulunamadı

## 5. Öğrenci Silme

Bir öğrenciyi ve ilişkili kullanıcı hesabını siler.

### İstek

```
DELETE /api/students/{student_id}
```

**Yetki**: Sadece Admin kullanabilir.

**URL Parametreleri**:

| Parametre  | Tip      | Açıklama                     |
|------------|----------|-----------------------------|
| student_id | integer  | Silinecek öğrencinin ID'si   |

**Örnek İstek (curl)**:

```bash
curl -X DELETE "http://localhost:5000/api/students/6" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Örnek İstek (JavaScript)**:

```javascript
const response = await fetch('http://localhost:5000/api/students/6', {
  method: 'DELETE',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
  }
});

const result = await response.json();
```

### Yanıt

**Başarılı Yanıt (200 OK)**:

```json
{
  "message": "Öğrenci 6 ve ilişkili veriler başarıyla silindi"
}
```

**Olası Hata Yanıtları**:

- `401 Unauthorized`: Kimlik doğrulama hatası
- `403 Forbidden`: Yetki hatası (kullanıcı Admin değil)
- `404 Not Found`: Belirtilen ID'ye sahip öğrenci bulunamadı
- `500 Internal Server Error`: Silme işlemi sırasında bir sunucu hatası oluştu

## 6. Yüz Fotoğrafı Yükleme

Belirli bir öğrenci için yüz fotoğrafı yükler ve yüz tanıma kodlamalarını oluşturur.

### İstek

```
POST /api/students/{student_id}/face
```

**Yetki**: Öğrencinin kendisi, Öğretmen veya Admin kullanabilir.

**URL Parametreleri**:

| Parametre  | Tip      | Açıklama                          |
|------------|----------|-----------------------------------|
| student_id | integer  | Fotoğrafı yüklenecek öğrencinin ID'si |

**İçerik Tipi**: multipart/form-data

**Form Parametreleri**:

| Alan | Tip  | Zorunlu | Açıklama              |
|------|------|---------|------------------------|
| file | file | Evet    | Öğrencinin yüz fotoğrafı |

**Örnek İstek (curl)**:

```bash
curl -X POST "http://localhost:5000/api/students/5/face" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: multipart/form-data" \
  -F "file=@ogrenci_foto.jpg"
```

**Örnek İstek (JavaScript)**:

```javascript
const formData = new FormData();
formData.append('file', fotografDosyasi); // File nesnesi

const response = await fetch('http://localhost:5000/api/students/5/face', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
  },
  body: formData
});

const result = await response.json();
```

### Yanıt

**Başarılı Yanıt (200 OK)**:

```json
{
  "message": "Yüz fotoğrafı başarıyla işlendi ve kodlama kaydedildi.",
  "face_photo_url": "/uploads/faces/student_5_face_20240601152030.jpg",
  "encodings_count": 1,
  "student_id": 5
}
```

**Olası Hata Yanıtları**:

- `400 Bad Request`: Geçersiz istek (örn. fotoğraf yüz içermiyor, dosya türü desteklenmiyor)
- `401 Unauthorized`: Kimlik doğrulama hatası
- `403 Forbidden`: Yetki hatası (kullanıcı öğrencinin kendisi, öğretmen veya admin değil)
- `404 Not Found`: Belirtilen ID'ye sahip öğrenci bulunamadı
- `500 Internal Server Error`: Yüz işleme veya kaydetme sırasında bir sunucu hatası oluştu

## 7. Öğrencinin Kayıtlı Olduğu Dersleri Getirme

Belirli bir öğrencinin kayıtlı olduğu tüm dersleri getirir.

### İstek

```
GET /api/students/{student_id}/courses
```

**Yetki**: Öğrencinin kendisi veya Admin kullanabilir.

**URL Parametreleri**:

| Parametre  | Tip      | Açıklama                        |
|------------|----------|----------------------------------|
| student_id | integer  | Dersleri getirilecek öğrencinin ID'si |

**Örnek İstek (curl)**:

```bash
curl -X GET "http://localhost:5000/api/students/5/courses" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Örnek İstek (JavaScript)**:

```javascript
const response = await fetch('http://localhost:5000/api/students/5/courses', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
  }
});

const courses = await response.json();
```

### Yanıt

**Başarılı Yanıt (200 OK)**:

```json
[
  {
    "id": 1,
    "code": "CS101",
    "name": "Bilgisayar Bilimlerine Giriş",
    "teacher_id": 1,
    "semester": "2024-Bahar",
    "created_at": "2024-01-10T10:00:00Z",
    "updated_at": "2024-01-10T10:00:00Z"
  },
  {
    "id": 3,
    "code": "PHYS101",
    "name": "Fizik I",
    "teacher_id": 4,
    "semester": "2024-Bahar",
    "created_at": "2024-01-12T09:00:00Z",
    "updated_at": "2024-01-12T09:00:00Z"
  }
]
```

**Olası Hata Yanıtları**:

- `401 Unauthorized`: Kimlik doğrulama hatası
- `403 Forbidden`: Yetki hatası (kullanıcı öğrencinin kendisi veya admin değil)
- `404 Not Found`: Belirtilen ID'ye sahip öğrenci bulunamadı

## Frontend Uygulaması İçin Yönlendirmeler

### Öğrenci Listesi Sayfası

Öğrencilerin listelendiği bu sayfada şu API'ler kullanılır:

1. `GET /api/students/` - Tüm öğrencilerin listesini getirir

**Örnek İmplementasyon**:

```javascript
async function loadStudents() {
  try {
    const response = await fetch('http://localhost:5000/api/students/', {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    });
    
    if (!response.ok) {
      throw new Error('Öğrenciler getirilemedi');
    }
    
    const students = await response.json();
    
    // Öğrenci listesini HTML tablosuna dönüştür
    const tableBody = document.getElementById('studentsTableBody');
    tableBody.innerHTML = '';
    
    students.forEach(student => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${student.id}</td>
        <td>${student.student_number}</td>
        <td>${student.user.first_name} ${student.user.last_name}</td>
        <td>${student.department}</td>
        <td>${student.face_photo_url ? 'Var' : 'Yok'}</td>
        <td>
          <button class="btn btn-info btn-sm" onclick="viewStudent(${student.id})">Görüntüle</button>
          <button class="btn btn-primary btn-sm" onclick="editStudent(${student.id})">Düzenle</button>
          <button class="btn btn-danger btn-sm" onclick="deleteStudent(${student.id})">Sil</button>
        </td>
      `;
      tableBody.appendChild(row);
    });
    
  } catch (error) {
    console.error('Hata:', error);
    showError('Öğrenciler yüklenirken bir hata oluştu.');
  }
}
```

### Öğrenci Ekleme Sayfası

Yeni öğrenci eklemek için kullanılan bu sayfada şu API kullanılır:

1. `POST /api/auth/register` - Yeni bir öğrenci oluşturur

**Örnek İmplementasyon**:

```javascript
async function addStudent(event) {
  event.preventDefault();
  
  const formData = {
    email: document.getElementById('email').value,
    password: document.getElementById('password').value,
    first_name: document.getElementById('firstName').value,
    last_name: document.getElementById('lastName').value,
    role: 'STUDENT',
    student_number: document.getElementById('studentNumber').value,
    department: document.getElementById('department').value
  };
  
  try {
    const response = await fetch('http://localhost:5000/api/auth/register', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Öğrenci eklenirken bir hata oluştu');
    }
    
    const result = await response.json();
    showSuccess('Öğrenci başarıyla eklendi!');
    
    // Yeni oluşturulan öğrencinin ID'si ile yüz fotoğrafı yükleme sayfasına yönlendir
    window.location.href = `/students/${result.student.id}/upload-face`;
    
  } catch (error) {
    console.error('Hata:', error);
    showError(error.message);
  }
}
```

### Öğrenci Detay/Düzenleme Sayfası

Öğrenci detaylarını görüntülemek ve düzenlemek için kullanılan sayfada şu API'ler kullanılır:

1. `GET /api/students/{student_id}` - Öğrenci detaylarını getirir
2. `PUT /api/students/{student_id}` - Öğrenci bilgilerini günceller
3. `POST /api/students/{student_id}/face` - Öğrenci için yüz fotoğrafı yükler

**Örnek İmplementasyon**:

```javascript
// Öğrenci detaylarını getir
async function loadStudentDetails(studentId) {
  try {
    const response = await fetch(`http://localhost:5000/api/students/${studentId}`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    });
    
    if (!response.ok) {
      throw new Error('Öğrenci detayları getirilemedi');
    }
    
    const student = await response.json();
    
    // Form alanlarını doldur
    document.getElementById('studentNumber').value = student.student_number;
    document.getElementById('department').value = student.department;
    document.getElementById('firstName').value = student.user.first_name;
    document.getElementById('lastName').value = student.user.last_name;
    document.getElementById('email').value = student.user.email;
    
    // Yüz fotoğrafı varsa göster
    if (student.face_photo_url) {
      document.getElementById('studentPhoto').src = student.face_photo_url;
      document.getElementById('photoContainer').style.display = 'block';
    }
    
  } catch (error) {
    console.error('Hata:', error);
    showError('Öğrenci detayları yüklenirken bir hata oluştu.');
  }
}

// Öğrenci bilgilerini güncelle
async function updateStudent(event, studentId) {
  event.preventDefault();
  
  const formData = {
    student_number: document.getElementById('studentNumber').value,
    department: document.getElementById('department').value
  };
  
  try {
    const response = await fetch(`http://localhost:5000/api/students/${studentId}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Öğrenci güncellenirken bir hata oluştu');
    }
    
    showSuccess('Öğrenci bilgileri başarıyla güncellendi!');
    
  } catch (error) {
    console.error('Hata:', error);
    showError(error.message);
  }
}

// Yüz fotoğrafı yükle
async function uploadFacePhoto(event, studentId) {
  event.preventDefault();
  
  const fileInput = document.getElementById('facePhoto');
  if (!fileInput.files || fileInput.files.length === 0) {
    showError('Lütfen bir fotoğraf seçin.');
    return;
  }
  
  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  
  try {
    const response = await fetch(`http://localhost:5000/api/students/${studentId}/face`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
      body: formData
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Fotoğraf yüklenirken bir hata oluştu');
    }
    
    const result = await response.json();
    showSuccess('Yüz fotoğrafı başarıyla yüklendi!');
    
    // Yeni fotoğrafı göster
    document.getElementById('studentPhoto').src = result.face_photo_url;
    document.getElementById('photoContainer').style.display = 'block';
    
  } catch (error) {
    console.error('Hata:', error);
    showError(error.message);
  }
}
```
