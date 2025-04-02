# API Test Log

## ✅ POST /auth/register

**Timestamp:** 2025-04-01 21:21:54.032792
**Status Code:** `201`

**Request Payload:**
```json
{
  "email": "admin_20250401212153@test.com",
  "password": "adminpass",
  "first_name": "Admin",
  "last_name": "User",
  "role": "ADMIN"
}
```

**Response Body:**
```json
{
  "created_at": "Tue, 01 Apr 2025 18:21:54 GMT",
  "email": "admin_20250401212153@test.com",
  "first_name": "Admin",
  "id": 22,
  "is_active": true,
  "last_name": "User",
  "role": "ADMIN",
  "updated_at": "Tue, 01 Apr 2025 18:21:54 GMT"
}
```

---

## ✅ POST /auth/register

**Timestamp:** 2025-04-01 21:21:54.260374
**Status Code:** `201`

**Request Payload:**
```json
{
  "email": "teacher_20250401212153@test.com",
  "password": "teacherpass",
  "first_name": "Test",
  "last_name": "Teacher",
  "role": "TEACHER",
  "department": "CompSci",
  "title": "Professor"
}
```

**Response Body:**
```json
{
  "created_at": "Tue, 01 Apr 2025 18:21:54 GMT",
  "email": "teacher_20250401212153@test.com",
  "first_name": "Test",
  "id": 23,
  "is_active": true,
  "last_name": "Teacher",
  "role": "TEACHER",
  "updated_at": "Tue, 01 Apr 2025 18:21:54 GMT"
}
```

---

## ✅ POST /auth/register

**Timestamp:** 2025-04-01 21:21:54.484301
**Status Code:** `201`

**Request Payload:**
```json
{
  "email": "student_20250401212153@test.com",
  "password": "studentpass",
  "first_name": "Test",
  "last_name": "Student",
  "role": "STUDENT",
  "department": "CompEng",
  "student_number": "S20250401212153"
}
```

**Response Body:**
```json
{
  "created_at": "Tue, 01 Apr 2025 18:21:54 GMT",
  "email": "student_20250401212153@test.com",
  "first_name": "Test",
  "id": 24,
  "is_active": true,
  "last_name": "Student",
  "role": "STUDENT",
  "updated_at": "Tue, 01 Apr 2025 18:21:54 GMT"
}
```

---

## ✅ POST /auth/login

**Timestamp:** 2025-04-01 21:21:54.700527
**Status Code:** `200`

**Request Payload:**
```json
{
  "email": "admin_20250401212153@test.com",
  "password": "adminpass"
}
```

**Response Body:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0MzUzMTcxNCwianRpIjoiM2Y0MzdiMmItODMxZC00ZmUxLTkzMzgtNzI5N2MxNzk0MTRhIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjIyIiwibmJmIjoxNzQzNTMxNzE0fQ.vPmEMm-9tKH2HyfJZM9y4SyzmRTaykav_IISQImD9wg",
  "token_type": "bearer",
  "user": {
    "created_at": "Tue, 01 Apr 2025 18:21:54 GMT",
    "email": "admin_20250401212153@test.com",
    "first_name": "Admin",
    "id": 22,
    "is_active": true,
    "last_name": "User",
    "role": "ADMIN",
    "updated_at": "Tue, 01 Apr 2025 18:21:54 GMT"
  }
}
```

---

## ✅ POST /auth/login

**Timestamp:** 2025-04-01 21:21:54.908779
**Status Code:** `200`

**Request Payload:**
```json
{
  "email": "teacher_20250401212153@test.com",
  "password": "teacherpass"
}
```

**Response Body:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0MzUzMTcxNCwianRpIjoiZTUzNjkyM2UtMDM0My00ZTI3LWE1MGUtMmVlZTA4MmI3MDU0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjIzIiwibmJmIjoxNzQzNTMxNzE0fQ.0aJ5XTF7j-D7R9fidsLfTQVXnfiEXDVNYevLcJyAo6o",
  "token_type": "bearer",
  "user": {
    "created_at": "Tue, 01 Apr 2025 18:21:54 GMT",
    "email": "teacher_20250401212153@test.com",
    "first_name": "Test",
    "id": 23,
    "is_active": true,
    "last_name": "Teacher",
    "role": "TEACHER",
    "updated_at": "Tue, 01 Apr 2025 18:21:54 GMT"
  }
}
```

---

## ✅ POST /auth/login

**Timestamp:** 2025-04-01 21:21:55.112176
**Status Code:** `200`

**Request Payload:**
```json
{
  "email": "student_20250401212153@test.com",
  "password": "studentpass"
}
```

**Response Body:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0MzUzMTcxNSwianRpIjoiYjFiMmRlOWEtMDZjMy00ODYyLWI2OWUtYTNlYWNkYWYyNmU4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjI0IiwibmJmIjoxNzQzNTMxNzE1fQ.TtEqlRs0YxEsTfOUoL2zUjmFEGtRPDLpivu2oxg-uIk",
  "token_type": "bearer",
  "user": {
    "created_at": "Tue, 01 Apr 2025 18:21:54 GMT",
    "email": "student_20250401212153@test.com",
    "first_name": "Test",
    "id": 24,
    "is_active": true,
    "last_name": "Student",
    "role": "STUDENT",
    "updated_at": "Tue, 01 Apr 2025 18:21:54 GMT"
  }
}
```

---

## ✅ GET /auth/me

**Timestamp:** 2025-04-01 21:21:55.116177
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
{
  "created_at": "Tue, 01 Apr 2025 18:21:54 GMT",
  "email": "admin_20250401212153@test.com",
  "first_name": "Admin",
  "id": 22,
  "is_active": true,
  "last_name": "User",
  "role": "ADMIN",
  "updated_at": "Tue, 01 Apr 2025 18:21:54 GMT"
}
```

---

## ✅ PUT /auth/me

**Timestamp:** 2025-04-01 21:21:55.122183
**Status Code:** `200`

**Request Payload:**
```json
{
  "last_name": "StudentUpdated"
}
```

**Response Body:**
```json
{
  "created_at": "Tue, 01 Apr 2025 18:21:54 GMT",
  "email": "student_20250401212153@test.com",
  "first_name": "Test",
  "id": 24,
  "is_active": true,
  "last_name": "StudentUpdated",
  "role": "STUDENT",
  "updated_at": "Tue, 01 Apr 2025 18:21:55 GMT"
}
```

---

## ✅ GET /teachers/

**Timestamp:** 2025-04-01 21:21:55.137414
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
[
  {
    "created_at": "2025-04-01T17:52:11.230576+00:00",
    "department": "string",
    "id": 1,
    "title": "string",
    "updated_at": "2025-04-01T17:52:11.230576+00:00",
    "user": {
      "created_at": "2025-04-01T17:52:11.230576+00:00",
      "email": "mert@example.com",
      "first_name": "string",
      "id": 2,
      "is_active": true,
      "last_name": "string",
      "role": "TEACHER",
      "updated_at": "2025-04-01T17:52:11.230576+00:00"
    },
    "user_id": 2
  },
  {
    "created_at": "2025-04-01T18:09:06.729911+00:00",
    "department": "CompSci",
    "id": 2,
    "title": "Associate Professor",
    "updated_at": "2025-04-01T18:09:07.763306+00:00",
    "user": {
      "created_at": "2025-04-01T18:09:06.729911+00:00",
      "email": "teacher_20250401210906@test.com",
      "first_name": "Test",
      "id": 4,
      "is_active": true,
      "last_name": "Teacher",
      "role": "TEACHER",
      "updated_at": "2025-04-01T18:09:06.729911+00:00"
    },
    "user_id": 4
  },
  {
    "created_at": "2025-04-01T18:11:57.338308+00:00",
    "department": "CompSci",
    "id": 3,
    "title": "Associate Professor",
    "updated_at": "2025-04-01T18:11:58.240046+00:00",
    "user": {
      "created_at": "2025-04-01T18:11:57.338308+00:00",
      "email": "teacher_20250401211156@test.com",
      "first_name": "Test",
      "id": 7,
      "is_active": true,
      "last_name": "Teacher",
      "role": "TEACHER",
      "updated_at": "2025-04-01T18:11:57.338308+00:00"
    },
    "user_id": 7
  },
  {
    "created_at": "2025-04-01T18:13:31.512946+00:00",
    "department": "CompSci",
    "id": 4,
    "title": "Associate Professor",
    "updated_at": "2025-04-01T18:13:32.394090+00:00",
    "user": {
      "created_at": "2025-04-01T18:13:31.512946+00:00",
      "email": "teacher_20250401211331@test.com",
      "first_name": "Test",
      "id": 10,
      "is_active": true,
      "last_name": "Teacher",
      "role": "TEACHER",
      "updated_at": "2025-04-01T18:13:31.512946+00:00"
    },
    "user_id": 10
  },
  {
    "created_at": "2025-04-01T18:15:12.810803+00:00",
    "department": "CompSci",
    "id": 5,
    "title": "Associate Professor",
    "updated_at": "2025-04-01T18:15:13.717863+00:00",
    "user": {
      "created_at": "2025-04-01T18:15:12.810803+00:00",
      "email": "teacher_20250401211512@test.com",
      "first_name": "Test",
      "id": 13,
      "is_active": true,
      "last_name": "Teacher",
      "role": "TEACHER",
      "updated_at": "2025-04-01T18:15:12.810803+00:00"
    },
    "user_id": 13
  },
  {
    "created_at": "2025-04-01T18:15:54.803119+00:00",
    "department": "CompSci",
    "id": 6,
    "title": "Associate Professor",
    "updated_at": "2025-04-01T18:15:55.707592+00:00",
    "user": {
      "created_at": "2025-04-01T18:15:54.803119+00:00",
      "email": "teacher_20250401211554@test.com",
      "first_name": "Test",
      "id": 16,
      "is_active": true,
      "last_name": "Teacher",
      "role": "TEACHER",
      "updated_at": "2025-04-01T18:15:54.803119+00:00"
    },
    "user_id": 16
  },
  {
    "created_at": "2025-04-01T18:18:10.496046+00:00",
    "department": "CompSci",
    "id": 7,
    "title": "Associate Professor",
    "updated_at": "2025-04-01T18:18:11.404252+00:00",
    "user": {
      "created_at": "2025-04-01T18:18:10.496046+00:00",
      "email": "teacher_20250401211810@test.com",
      "first_name": "Test",
      "id": 19,
      "is_active": true,
      "last_name": "Teacher",
      "role": "TEACHER",
      "updated_at": "2025-04-01T18:18:10.496046+00:00"
    },
    "user_id": 19
  },
  {
    "created_at": "2025-04-01T18:21:54.254707+00:00",
    "department": "CompSci",
    "id": 8,
    "title": "Professor",
    "updated_at": "2025-04-01T18:21:54.254707+00:00",
    "user": {
      "created_at": "2025-04-01T18:21:54.254707+00:00",
      "email": "teacher_20250401212153@test.com",
      "first_name": "Test",
      "id": 23,
      "is_active": true,
      "last_name": "Teacher",
      "role": "TEACHER",
      "updated_at": "2025-04-01T18:21:54.254707+00:00"
    },
    "user_id": 23
  }
]
```

---

## ✅ GET /teachers/8

**Timestamp:** 2025-04-01 21:21:55.142525
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
{
  "created_at": "2025-04-01T18:21:54.254707+00:00",
  "department": "CompSci",
  "id": 8,
  "title": "Professor",
  "updated_at": "2025-04-01T18:21:54.254707+00:00",
  "user": {
    "created_at": "2025-04-01T18:21:54.254707+00:00",
    "email": "teacher_20250401212153@test.com",
    "first_name": "Test",
    "id": 23,
    "is_active": true,
    "last_name": "Teacher",
    "role": "TEACHER",
    "updated_at": "2025-04-01T18:21:54.254707+00:00"
  },
  "user_id": 23
}
```

---

## ✅ PUT /teachers/8

**Timestamp:** 2025-04-01 21:21:55.149531
**Status Code:** `200`

**Request Payload:**
```json
{
  "title": "Associate Professor"
}
```

**Response Body:**
```json
{
  "created_at": "2025-04-01T18:21:54.254707+00:00",
  "department": "CompSci",
  "id": 8,
  "title": "Associate Professor",
  "updated_at": "2025-04-01T18:21:55.146523+00:00",
  "user": {
    "created_at": "2025-04-01T18:21:54.254707+00:00",
    "email": "teacher_20250401212153@test.com",
    "first_name": "Test",
    "id": 23,
    "is_active": true,
    "last_name": "Teacher",
    "role": "TEACHER",
    "updated_at": "2025-04-01T18:21:54.254707+00:00"
  },
  "user_id": 23
}
```

---

## ✅ GET /teachers/8/courses

**Timestamp:** 2025-04-01 21:21:55.163147
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
[]
```

---

## ✅ GET /students/

**Timestamp:** 2025-04-01 21:21:55.170765
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
[
  {
    "created_at": "2025-04-01T17:27:08.383390+00:00",
    "department": "string",
    "face_photo_url": null,
    "id": 1,
    "student_number": "string",
    "updated_at": "2025-04-01T17:27:08.383390+00:00",
    "user": {
      "created_at": "2025-04-01T17:31:56.545806+00:00",
      "email": "user@example.com",
      "first_name": "string",
      "id": 1,
      "is_active": true,
      "last_name": "string",
      "role": "STUDENT",
      "updated_at": "2025-04-01T17:31:56.545806+00:00"
    },
    "user_id": 1
  },
  {
    "created_at": "2025-04-01T17:31:56.545806+00:00",
    "department": "string",
    "face_photo_url": null,
    "id": 2,
    "student_number": "1234",
    "updated_at": "2025-04-01T17:31:56.545806+00:00",
    "user": {
      "created_at": "2025-04-01T17:31:56.545806+00:00",
      "email": "user@example.com",
      "first_name": "string",
      "id": 1,
      "is_active": true,
      "last_name": "string",
      "role": "STUDENT",
      "updated_at": "2025-04-01T17:31:56.545806+00:00"
    },
    "user_id": 1
  },
  {
    "created_at": "2025-04-01T18:09:06.962266+00:00",
    "department": "CompEng",
    "face_photo_url": "/C:\\Users\\mert1\\OneDrive\\Masa\u00fcst\u00fc\\yuztanima_backend\\app\\uploads\\faces/student_3_20250401210908.jpg",
    "id": 3,
    "student_number": "S20250401210906",
    "updated_at": "2025-04-01T18:09:08.682163+00:00",
    "user": {
      "created_at": "2025-04-01T18:09:06.962266+00:00",
      "email": "student_20250401210906@test.com",
      "first_name": "Test",
      "id": 5,
      "is_active": true,
      "last_name": "StudentUpdated",
      "role": "STUDENT",
      "updated_at": "2025-04-01T18:09:07.734520+00:00"
    },
    "user_id": 5
  },
  {
    "created_at": "2025-04-01T18:11:57.567840+00:00",
    "department": "CompEng",
    "face_photo_url": "/C:\\Users\\mert1\\OneDrive\\Masa\u00fcst\u00fc\\yuztanima_backend\\app\\uploads\\faces/student_4_20250401211159.jpg",
    "id": 4,
    "student_number": "S20250401211156",
    "updated_at": "2025-04-01T18:11:59.049556+00:00",
    "user": {
      "created_at": "2025-04-01T18:11:57.567840+00:00",
      "email": "student_20250401211156@test.com",
      "first_name": "Test",
      "id": 8,
      "is_active": true,
      "last_name": "StudentUpdated",
      "role": "STUDENT",
      "updated_at": "2025-04-01T18:11:58.209788+00:00"
    },
    "user_id": 8
  },
  {
    "created_at": "2025-04-01T18:13:31.738644+00:00",
    "department": "CompEng",
    "face_photo_url": "/C:\\Users\\mert1\\OneDrive\\Masa\u00fcst\u00fc\\yuztanima_backend\\app\\uploads\\faces/student_5_20250401211333.jpg",
    "id": 5,
    "student_number": "S20250401211331",
    "updated_at": "2025-04-01T18:13:33.239927+00:00",
    "user": {
      "created_at": "2025-04-01T18:13:31.738644+00:00",
      "email": "student_20250401211331@test.com",
      "first_name": "Test",
      "id": 11,
      "is_active": true,
      "last_name": "StudentUpdated",
      "role": "STUDENT",
      "updated_at": "2025-04-01T18:13:32.367299+00:00"
    },
    "user_id": 11
  },
  {
    "created_at": "2025-04-01T18:15:13.052505+00:00",
    "department": "CompEng",
    "face_photo_url": "/C:\\Users\\mert1\\OneDrive\\Masa\u00fcst\u00fc\\yuztanima_backend\\app\\uploads\\faces/student_6_20250401211514.jpg",
    "id": 6,
    "student_number": "S20250401211512",
    "updated_at": "2025-04-01T18:15:14.541063+00:00",
    "user": {
      "created_at": "2025-04-01T18:15:13.052505+00:00",
      "email": "student_20250401211512@test.com",
      "first_name": "Test",
      "id": 14,
      "is_active": true,
      "last_name": "StudentUpdated",
      "role": "STUDENT",
      "updated_at": "2025-04-01T18:15:13.690947+00:00"
    },
    "user_id": 14
  },
  {
    "created_at": "2025-04-01T18:15:55.035385+00:00",
    "department": "CompEng",
    "face_photo_url": "/C:\\Users\\mert1\\OneDrive\\Masa\u00fcst\u00fc\\yuztanima_backend\\app\\uploads\\faces/student_7_20250401211556.jpg",
    "id": 7,
    "student_number": "S20250401211554",
    "updated_at": "2025-04-01T18:15:56.556412+00:00",
    "user": {
      "created_at": "2025-04-01T18:15:55.035385+00:00",
      "email": "student_20250401211554@test.com",
      "first_name": "Test",
      "id": 17,
      "is_active": true,
      "last_name": "StudentUpdated",
      "role": "STUDENT",
      "updated_at": "2025-04-01T18:15:55.677720+00:00"
    },
    "user_id": 17
  },
  {
    "created_at": "2025-04-01T18:18:10.725621+00:00",
    "department": "CompEng",
    "face_photo_url": "/C:\\Users\\mert1\\OneDrive\\Masa\u00fcst\u00fc\\yuztanima_backend\\app\\uploads\\faces/student_8_20250401211812.jpg",
    "id": 8,
    "student_number": "S20250401211810",
    "updated_at": "2025-04-01T18:18:12.241325+00:00",
    "user": {
      "created_at": "2025-04-01T18:18:10.725621+00:00",
      "email": "student_20250401211810@test.com",
      "first_name": "Test",
      "id": 20,
      "is_active": true,
      "last_name": "StudentUpdated",
      "role": "STUDENT",
      "updated_at": "2025-04-01T18:18:11.375750+00:00"
    },
    "user_id": 20
  },
  {
    "created_at": "2025-04-01T18:21:54.477471+00:00",
    "department": "CompEng",
    "face_photo_url": null,
    "id": 9,
    "student_number": "S20250401212153",
    "updated_at": "2025-04-01T18:21:54.477471+00:00",
    "user": {
      "created_at": "2025-04-01T18:21:54.477471+00:00",
      "email": "student_20250401212153@test.com",
      "first_name": "Test",
      "id": 24,
      "is_active": true,
      "last_name": "StudentUpdated",
      "role": "STUDENT",
      "updated_at": "2025-04-01T18:21:55.119223+00:00"
    },
    "user_id": 24
  }
]
```

---

## ✅ GET /students/9

**Timestamp:** 2025-04-01 21:21:55.175826
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
{
  "created_at": "2025-04-01T18:21:54.477471+00:00",
  "department": "CompEng",
  "face_photo_url": null,
  "id": 9,
  "student_number": "S20250401212153",
  "updated_at": "2025-04-01T18:21:54.477471+00:00",
  "user": {
    "created_at": "2025-04-01T18:21:54.477471+00:00",
    "email": "student_20250401212153@test.com",
    "first_name": "Test",
    "id": 24,
    "is_active": true,
    "last_name": "StudentUpdated",
    "role": "STUDENT",
    "updated_at": "2025-04-01T18:21:55.119223+00:00"
  },
  "user_id": 24
}
```

---

## ✅ PUT /students/9

**Timestamp:** 2025-04-01 21:21:55.182822
**Status Code:** `200`

**Request Payload:**
```json
{
  "department": "Computer Science & Eng."
}
```

**Response Body:**
```json
{
  "created_at": "2025-04-01T18:21:54.477471+00:00",
  "department": "Computer Science & Eng.",
  "face_photo_url": null,
  "id": 9,
  "student_number": "S20250401212153",
  "updated_at": "2025-04-01T18:21:55.178826+00:00",
  "user": {
    "created_at": "2025-04-01T18:21:54.477471+00:00",
    "email": "student_20250401212153@test.com",
    "first_name": "Test",
    "id": 24,
    "is_active": true,
    "last_name": "StudentUpdated",
    "role": "STUDENT",
    "updated_at": "2025-04-01T18:21:55.119223+00:00"
  },
  "user_id": 24
}
```

---

## ✅ POST /students/9/face

**Timestamp:** 2025-04-01 21:21:56.008365
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
{
  "face_photo_url": "/C:\\Users\\mert1\\OneDrive\\Masa\u00fcst\u00fc\\yuztanima_backend\\app\\uploads\\faces/student_9_20250401212155.jpg",
  "message": "Face photo processed and encoding saved successfully.",
  "student_id": 9
}
```

---

## ✅ GET /students/9/courses

**Timestamp:** 2025-04-01 21:21:56.023981
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
[]
```

---

## ✅ POST /courses/

**Timestamp:** 2025-04-01 21:21:56.047387
**Status Code:** `201`

**Request Payload:**
```json
{
  "code": "TEST20250401212153",
  "name": "API Test Course",
  "semester": "2025-Test",
  "lesson_times": [
    {
      "day": "TUESDAY",
      "start_time": "10:00",
      "end_time": "11:50",
      "lesson_number": 1
    },
    {
      "day": "THURSDAY",
      "start_time": "14:00",
      "end_time": "15:50",
      "lesson_number": 2
    }
  ]
}
```

**Response Body:**
```json
{
  "code": "TEST20250401212153",
  "created_at": "2025-04-01T18:21:56.028990+00:00",
  "id": 7,
  "lesson_times": [
    {
      "course_id": 7,
      "created_at": "2025-04-01T18:21:56.028990+00:00",
      "day": "TUESDAY",
      "end_time": "11:50",
      "id": 13,
      "lesson_number": 1,
      "start_time": "10:00",
      "updated_at": "2025-04-01T18:21:56.028990+00:00"
    },
    {
      "course_id": 7,
      "created_at": "2025-04-01T18:21:56.028990+00:00",
      "day": "THURSDAY",
      "end_time": "15:50",
      "id": 14,
      "lesson_number": 2,
      "start_time": "14:00",
      "updated_at": "2025-04-01T18:21:56.028990+00:00"
    }
  ],
  "name": "API Test Course",
  "semester": "2025-Test",
  "teacher": {
    "created_at": "2025-04-01T18:21:54.254707+00:00",
    "department": "CompSci",
    "id": 8,
    "title": "Associate Professor",
    "updated_at": "2025-04-01T18:21:55.146523+00:00",
    "user": {
      "created_at": "2025-04-01T18:21:54.254707+00:00",
      "email": "teacher_20250401212153@test.com",
      "first_name": "Test",
      "id": 23,
      "is_active": true,
      "last_name": "Teacher",
      "role": "TEACHER",
      "updated_at": "2025-04-01T18:21:54.254707+00:00"
    },
    "user_id": 23
  },
  "teacher_id": 8,
  "updated_at": "2025-04-01T18:21:56.028990+00:00"
}
```

---

## ✅ GET /courses/

**Timestamp:** 2025-04-01 21:21:56.066938
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
[
  {
    "code": "CS101",
    "created_at": "2025-04-01T18:04:44.328748+00:00",
    "id": 1,
    "lesson_times": [],
    "name": "Bilgisayar Bilimlerine Giri\u015f",
    "semester": "2024-Bahar",
    "teacher": {
      "created_at": "2025-04-01T17:52:11.230576+00:00",
      "department": "string",
      "id": 1,
      "title": "string",
      "updated_at": "2025-04-01T17:52:11.230576+00:00",
      "user": {
        "created_at": "2025-04-01T17:52:11.230576+00:00",
        "email": "mert@example.com",
        "first_name": "string",
        "id": 2,
        "is_active": true,
        "last_name": "string",
        "role": "TEACHER",
        "updated_at": "2025-04-01T17:52:11.230576+00:00"
      },
      "user_id": 2
    },
    "teacher_id": 1,
    "updated_at": "2025-04-01T18:04:44.328748+00:00"
  },
  {
    "code": "TEST20250401211156",
    "created_at": "2025-04-01T18:11:59.081865+00:00",
    "id": 2,
    "lesson_times": [],
    "name": "API Test Course",
    "semester": "2025-Test-Updated",
    "teacher": {
      "created_at": "2025-04-01T18:11:57.338308+00:00",
      "department": "CompSci",
      "id": 3,
      "title": "Associate Professor",
      "updated_at": "2025-04-01T18:11:58.240046+00:00",
      "user": {
        "created_at": "2025-04-01T18:11:57.338308+00:00",
        "email": "teacher_20250401211156@test.com",
        "first_name": "Test",
        "id": 7,
        "is_active": true,
        "last_name": "Teacher",
        "role": "TEACHER",
        "updated_at": "2025-04-01T18:11:57.338308+00:00"
      },
      "user_id": 7
    },
    "teacher_id": 3,
    "updated_at": "2025-04-01T18:11:59.130655+00:00"
  },
  {
    "code": "TEST20250401211331",
    "created_at": "2025-04-01T18:13:33.262057+00:00",
    "id": 3,
    "lesson_times": [],
    "name": "API Test Course",
    "semester": "2025-Test-Updated",
    "teacher": {
      "created_at": "2025-04-01T18:13:31.512946+00:00",
      "department": "CompSci",
      "id": 4,
      "title": "Associate Professor",
      "updated_at": "2025-04-01T18:13:32.394090+00:00",
      "user": {
        "created_at": "2025-04-01T18:13:31.512946+00:00",
        "email": "teacher_20250401211331@test.com",
        "first_name": "Test",
        "id": 10,
        "is_active": true,
        "last_name": "Teacher",
        "role": "TEACHER",
        "updated_at": "2025-04-01T18:13:31.512946+00:00"
      },
      "user_id": 10
    },
    "teacher_id": 4,
    "updated_at": "2025-04-01T18:13:33.309813+00:00"
  },
  {
    "code": "TEST20250401211512",
    "created_at": "2025-04-01T18:15:14.571119+00:00",
    "id": 4,
    "lesson_times": [],
    "name": "API Test Course",
    "semester": "2025-Test-Updated",
    "teacher": {
      "created_at": "2025-04-01T18:15:12.810803+00:00",
      "department": "CompSci",
      "id": 5,
      "title": "Associate Professor",
      "updated_at": "2025-04-01T18:15:13.717863+00:00",
      "user": {
        "created_at": "2025-04-01T18:15:12.810803+00:00",
        "email": "teacher_20250401211512@test.com",
        "first_name": "Test",
        "id": 13,
        "is_active": true,
        "last_name": "Teacher",
        "role": "TEACHER",
        "updated_at": "2025-04-01T18:15:12.810803+00:00"
      },
      "user_id": 13
    },
    "teacher_id": 5,
    "updated_at": "2025-04-01T18:15:14.622003+00:00"
  },
  {
    "code": "TEST20250401211554",
    "created_at": "2025-04-01T18:15:56.581744+00:00",
    "id": 5,
    "lesson_times": [],
    "name": "API Test Course",
    "semester": "2025-Test-Updated",
    "teacher": {
      "created_at": "2025-04-01T18:15:54.803119+00:00",
      "department": "CompSci",
      "id": 6,
      "title": "Associate Professor",
      "updated_at": "2025-04-01T18:15:55.707592+00:00",
      "user": {
        "created_at": "2025-04-01T18:15:54.803119+00:00",
        "email": "teacher_20250401211554@test.com",
        "first_name": "Test",
        "id": 16,
        "is_active": true,
        "last_name": "Teacher",
        "role": "TEACHER",
        "updated_at": "2025-04-01T18:15:54.803119+00:00"
      },
      "user_id": 16
    },
    "teacher_id": 6,
    "updated_at": "2025-04-01T18:15:56.641506+00:00"
  },
  {
    "code": "TEST20250401211810",
    "created_at": "2025-04-01T18:18:12.272257+00:00",
    "id": 6,
    "lesson_times": [],
    "name": "API Test Course",
    "semester": "2025-Test-Updated",
    "teacher": {
      "created_at": "2025-04-01T18:18:10.496046+00:00",
      "department": "CompSci",
      "id": 7,
      "title": "Associate Professor",
      "updated_at": "2025-04-01T18:18:11.404252+00:00",
      "user": {
        "created_at": "2025-04-01T18:18:10.496046+00:00",
        "email": "teacher_20250401211810@test.com",
        "first_name": "Test",
        "id": 19,
        "is_active": true,
        "last_name": "Teacher",
        "role": "TEACHER",
        "updated_at": "2025-04-01T18:18:10.496046+00:00"
      },
      "user_id": 19
    },
    "teacher_id": 7,
    "updated_at": "2025-04-01T18:18:12.324079+00:00"
  },
  {
    "code": "TEST20250401212153",
    "created_at": "2025-04-01T18:21:56.028990+00:00",
    "id": 7,
    "lesson_times": [],
    "name": "API Test Course",
    "semester": "2025-Test",
    "teacher": {
      "created_at": "2025-04-01T18:21:54.254707+00:00",
      "department": "CompSci",
      "id": 8,
      "title": "Associate Professor",
      "updated_at": "2025-04-01T18:21:55.146523+00:00",
      "user": {
        "created_at": "2025-04-01T18:21:54.254707+00:00",
        "email": "teacher_20250401212153@test.com",
        "first_name": "Test",
        "id": 23,
        "is_active": true,
        "last_name": "Teacher",
        "role": "TEACHER",
        "updated_at": "2025-04-01T18:21:54.254707+00:00"
      },
      "user_id": 23
    },
    "teacher_id": 8,
    "updated_at": "2025-04-01T18:21:56.028990+00:00"
  }
]
```

---

## ✅ GET /courses/7

**Timestamp:** 2025-04-01 21:21:56.082827
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
{
  "code": "TEST20250401212153",
  "created_at": "2025-04-01T18:21:56.028990+00:00",
  "id": 7,
  "lesson_times": [
    {
      "course_id": 7,
      "created_at": "2025-04-01T18:21:56.028990+00:00",
      "day": "TUESDAY",
      "end_time": "11:50",
      "id": 13,
      "lesson_number": 1,
      "start_time": "10:00",
      "updated_at": "2025-04-01T18:21:56.028990+00:00"
    },
    {
      "course_id": 7,
      "created_at": "2025-04-01T18:21:56.028990+00:00",
      "day": "THURSDAY",
      "end_time": "15:50",
      "id": 14,
      "lesson_number": 2,
      "start_time": "14:00",
      "updated_at": "2025-04-01T18:21:56.028990+00:00"
    }
  ],
  "name": "API Test Course",
  "semester": "2025-Test",
  "teacher": {
    "created_at": "2025-04-01T18:21:54.254707+00:00",
    "department": "CompSci",
    "id": 8,
    "title": "Associate Professor",
    "updated_at": "2025-04-01T18:21:55.146523+00:00",
    "user": {
      "created_at": "2025-04-01T18:21:54.254707+00:00",
      "email": "teacher_20250401212153@test.com",
      "first_name": "Test",
      "id": 23,
      "is_active": true,
      "last_name": "Teacher",
      "role": "TEACHER",
      "updated_at": "2025-04-01T18:21:54.254707+00:00"
    },
    "user_id": 23
  },
  "teacher_id": 8,
  "updated_at": "2025-04-01T18:21:56.028990+00:00"
}
```

---

## ✅ PUT /courses/7

**Timestamp:** 2025-04-01 21:21:56.094335
**Status Code:** `200`

**Request Payload:**
```json
{
  "semester": "2025-Test-Updated"
}
```

**Response Body:**
```json
{
  "code": "TEST20250401212153",
  "created_at": "2025-04-01T18:21:56.028990+00:00",
  "id": 7,
  "lesson_times": [
    {
      "course_id": 7,
      "created_at": "2025-04-01T18:21:56.028990+00:00",
      "day": "TUESDAY",
      "end_time": "11:50",
      "id": 13,
      "lesson_number": 1,
      "start_time": "10:00",
      "updated_at": "2025-04-01T18:21:56.028990+00:00"
    },
    {
      "course_id": 7,
      "created_at": "2025-04-01T18:21:56.028990+00:00",
      "day": "THURSDAY",
      "end_time": "15:50",
      "id": 14,
      "lesson_number": 2,
      "start_time": "14:00",
      "updated_at": "2025-04-01T18:21:56.028990+00:00"
    }
  ],
  "name": "API Test Course",
  "semester": "2025-Test-Updated",
  "teacher": {
    "created_at": "2025-04-01T18:21:54.254707+00:00",
    "department": "CompSci",
    "id": 8,
    "title": "Associate Professor",
    "updated_at": "2025-04-01T18:21:55.146523+00:00",
    "user": {
      "created_at": "2025-04-01T18:21:54.254707+00:00",
      "email": "teacher_20250401212153@test.com",
      "first_name": "Test",
      "id": 23,
      "is_active": true,
      "last_name": "Teacher",
      "role": "TEACHER",
      "updated_at": "2025-04-01T18:21:54.254707+00:00"
    },
    "user_id": 23
  },
  "teacher_id": 8,
  "updated_at": "2025-04-01T18:21:56.088374+00:00"
}
```

---

## ✅ POST /courses/7/students

**Timestamp:** 2025-04-01 21:21:56.110264
**Status Code:** `201`

**Request Payload:**
```json
{
  "student_id": 9
}
```

**Response Body:**
```json
{
  "course_id": 7,
  "id": 4,
  "student_id": 9
}
```

---

## ✅ GET /courses/7/students

**Timestamp:** 2025-04-01 21:21:56.117262
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
[
  {
    "created_at": "2025-04-01T18:21:54.477471+00:00",
    "department": "Computer Science & Eng.",
    "face_photo_url": "/C:\\Users\\mert1\\OneDrive\\Masa\u00fcst\u00fc\\yuztanima_backend\\app\\uploads\\faces/student_9_20250401212155.jpg",
    "id": 9,
    "student_number": "S20250401212153",
    "updated_at": "2025-04-01T18:21:55.998403+00:00",
    "user": {
      "created_at": "2025-04-01T18:21:54.477471+00:00",
      "email": "student_20250401212153@test.com",
      "first_name": "Test",
      "id": 24,
      "is_active": true,
      "last_name": "StudentUpdated",
      "role": "STUDENT",
      "updated_at": "2025-04-01T18:21:55.119223+00:00"
    },
    "user_id": 24
  }
]
```

---

## ✅ GET /students/9/courses

**Timestamp:** 2025-04-01 21:21:56.123895
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
[
  {
    "code": "TEST20250401212153",
    "created_at": "2025-04-01T18:21:56.028990+00:00",
    "id": 7,
    "name": "API Test Course",
    "semester": "2025-Test-Updated",
    "teacher_id": 8,
    "updated_at": "2025-04-01T18:21:56.088374+00:00"
  }
]
```

---

## ✅ GET /courses/7/attendance

**Timestamp:** 2025-04-01 21:21:56.129903
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
[]
```

---

## ✅ DELETE /courses/7/students/9

**Timestamp:** 2025-04-01 21:21:56.135621
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
{
  "message": "Student 9 removed from course 7 successfully."
}
```

---

## ✅ POST /courses/7/students

**Timestamp:** 2025-04-01 21:21:56.146255
**Status Code:** `201`

**Request Payload:**
```json
{
  "student_id": 9
}
```

**Response Body:**
```json
{
  "course_id": 7,
  "id": 4,
  "student_id": 9
}
```

---

## ✅ POST /attendance/

**Timestamp:** 2025-04-01 21:21:57.056377
**Status Code:** `201`

**Request Payload:**
```json
{
  "course_id": 7,
  "lesson_number": 1,
  "date": "2025-04-01",
  "type": "FACE"
}
```

**Response Body:**
```json
{
  "attendance_id": 4,
  "recognized_count": 1,
  "results": [
    {
      "confidence": 1.0,
      "emotion": null,
      "emotion_confidence": null,
      "status": "PRESENT",
      "student_id": 9
    }
  ],
  "unrecognized_count": 0
}
```

---

## ✅ GET /attendance/4

**Timestamp:** 2025-04-01 21:21:57.077075
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
{
  "course_id": 7,
  "created_at": "2025-04-01T18:21:57.040518+00:00",
  "created_by": 23,
  "date": "2025-04-01",
  "details": [
    {
      "attendance_id": 4,
      "confidence": 1.0,
      "created_at": "2025-04-01T18:21:57.040518+00:00",
      "emotion": null,
      "emotion_confidence": null,
      "emotion_statistics": null,
      "id": 4,
      "status": "PRESENT",
      "student": {
        "id": 9,
        "student_number": "S20250401212153",
        "user_id": 24
      },
      "student_id": 9
    }
  ],
  "emotion_statistics": null,
  "id": 4,
  "lesson_number": 1,
  "photo_path": "/uploads/attendance/attendance_7_2025-04-01_1_212157.jpg",
  "recognized_students": 1,
  "total_students": 1,
  "type": "FACE",
  "unrecognized_students": 0
}
```

---

## ✅ GET /attendance/course/7

**Timestamp:** 2025-04-01 21:21:57.083547
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
[
  {
    "course_id": 7,
    "created_at": "2025-04-01T18:21:57.040518+00:00",
    "created_by": 23,
    "date": "2025-04-01",
    "emotion_statistics": null,
    "id": 4,
    "lesson_number": 1,
    "photo_path": "/uploads/attendance/attendance_7_2025-04-01_1_212157.jpg",
    "recognized_students": 1,
    "total_students": 1,
    "type": "FACE",
    "unrecognized_students": 0
  }
]
```

---

## ✅ GET /attendance/course/7/student/9

**Timestamp:** 2025-04-01 21:21:57.088724
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
{
  "attendance_details": [
    {
      "attendance_id": 4,
      "confidence": 1.0,
      "created_at": "2025-04-01T18:21:57.040518+00:00",
      "date": "2025-04-01",
      "emotion": null,
      "emotion_confidence": null,
      "emotion_statistics": null,
      "id": 4,
      "status": "PRESENT",
      "student_id": 9
    }
  ],
  "course_info": {
    "code": "TEST20250401212153",
    "created_at": "2025-04-01T18:21:56.028990+00:00",
    "id": 7,
    "name": "API Test Course",
    "semester": "2025-Test-Updated",
    "teacher_id": 8,
    "updated_at": "2025-04-01T18:21:56.088374+00:00"
  },
  "student_info": {
    "created_at": "2025-04-01T18:21:54.477471+00:00",
    "department": "Computer Science & Eng.",
    "face_photo_url": "/C:\\Users\\mert1\\OneDrive\\Masa\u00fcst\u00fc\\yuztanima_backend\\app\\uploads\\faces/student_9_20250401212155.jpg",
    "id": 9,
    "student_number": "S20250401212153",
    "updated_at": "2025-04-01T18:21:55.998403+00:00",
    "user": {
      "created_at": "2025-04-01T18:21:54.477471+00:00",
      "email": "student_20250401212153@test.com",
      "first_name": "Test",
      "id": 24,
      "is_active": true,
      "last_name": "StudentUpdated",
      "role": "STUDENT",
      "updated_at": "2025-04-01T18:21:55.119223+00:00"
    },
    "user_id": 24
  }
}
```

---

## ✅ GET /courses/7/students

**Timestamp:** 2025-04-01 21:21:57.096179
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
[
  {
    "created_at": "2025-04-01T18:21:54.477471+00:00",
    "department": "Computer Science & Eng.",
    "face_photo_url": "/C:\\Users\\mert1\\OneDrive\\Masa\u00fcst\u00fc\\yuztanima_backend\\app\\uploads\\faces/student_9_20250401212155.jpg",
    "id": 9,
    "student_number": "S20250401212153",
    "updated_at": "2025-04-01T18:21:55.998403+00:00",
    "user": {
      "created_at": "2025-04-01T18:21:54.477471+00:00",
      "email": "student_20250401212153@test.com",
      "first_name": "Test",
      "id": 24,
      "is_active": true,
      "last_name": "StudentUpdated",
      "role": "STUDENT",
      "updated_at": "2025-04-01T18:21:55.119223+00:00"
    },
    "user_id": 24
  }
]
```

---

## ✅ POST /attendance/4/students/9

**Timestamp:** 2025-04-01 21:21:57.115204
**Status Code:** `200`

**Request Payload:**
```json
{
  "status": "EXCUSED"
}
```

**Response Body:**
```json
{
  "attendance_id": 4,
  "confidence": 1.0,
  "created_at": "2025-04-01T18:21:57.040518+00:00",
  "emotion": null,
  "emotion_confidence": null,
  "emotion_statistics": null,
  "id": 4,
  "status": "EXCUSED",
  "student": {
    "created_at": "2025-04-01T18:21:54.477471+00:00",
    "email": "student_20250401212153@test.com",
    "first_name": "Test",
    "id": 24,
    "is_active": true,
    "last_name": "StudentUpdated",
    "role": "STUDENT",
    "updated_at": "2025-04-01T18:21:55.119223+00:00"
  },
  "student_id": 9,
  "updated_at": "2025-04-01T18:21:57.101100+00:00"
}
```

---

## ✅ GET /reports/attendance/daily

**Timestamp:** 2025-04-01 21:21:57.130019
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
{
  "date": "Tue, 01 Apr 2025 00:00:00 GMT",
  "reports": [
    {
      "absent_count": 1,
      "course_code": "TEST20250401211512",
      "course_id": 4,
      "course_name": "API Test Course",
      "present_count": 0
    },
    {
      "absent_count": 1,
      "course_code": "TEST20250401211554",
      "course_id": 5,
      "course_name": "API Test Course",
      "present_count": 0
    },
    {
      "absent_count": 1,
      "course_code": "TEST20250401211810",
      "course_id": 6,
      "course_name": "API Test Course",
      "present_count": 0
    },
    {
      "absent_count": 1,
      "course_code": "TEST20250401212153",
      "course_id": 7,
      "course_name": "API Test Course",
      "present_count": 0
    },
    {
      "absent_count": 0,
      "course_code": "CS101",
      "course_id": 1,
      "course_name": "Bilgisayar Bilimlerine Giri\u015f",
      "present_count": 0
    },
    {
      "absent_count": 0,
      "course_code": "TEST20250401211156",
      "course_id": 2,
      "course_name": "API Test Course",
      "present_count": 0
    },
    {
      "absent_count": 0,
      "course_code": "TEST20250401211331",
      "course_id": 3,
      "course_name": "API Test Course",
      "present_count": 0
    }
  ]
}
```

---

## ✅ GET /reports/attendance/daily?course_id=7

**Timestamp:** 2025-04-01 21:21:57.135902
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
{
  "date": "Tue, 01 Apr 2025 00:00:00 GMT",
  "reports": [
    {
      "absent_count": 1,
      "course_code": "TEST20250401212153",
      "course_id": 7,
      "course_name": "API Test Course",
      "present_count": 0
    }
  ]
}
```

---

## ✅ GET /reports/attendance/student/9

**Timestamp:** 2025-04-01 21:21:57.142388
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
{
  "course_reports": [
    {
      "course_code": "TEST20250401212153",
      "course_id": 7,
      "details": [
        {
          "attendance_id": 4,
          "confidence": null,
          "created_at": "Tue, 01 Apr 2025 18:21:57 GMT",
          "emotion": null,
          "emotion_confidence": null,
          "emotion_statistics": null,
          "id": 4,
          "status": "EXCUSED",
          "student": null,
          "student_id": 9
        }
      ],
      "rate": 0.0
    }
  ],
  "overall_attendance_rate": 0.0,
  "student_info": {
    "created_at": "Tue, 01 Apr 2025 18:21:54 GMT",
    "department": "Computer Science & Eng.",
    "face_photo_url": "/C:\\Users\\mert1\\OneDrive\\Masa\u00fcst\u00fc\\yuztanima_backend\\app\\uploads\\faces/student_9_20250401212155.jpg",
    "id": 9,
    "student_number": "S20250401212153",
    "updated_at": "Tue, 01 Apr 2025 18:21:55 GMT",
    "user": {
      "created_at": "Tue, 01 Apr 2025 18:21:54 GMT",
      "email": "student_20250401212153@test.com",
      "first_name": "Test",
      "id": 24,
      "is_active": true,
      "last_name": "StudentUpdated",
      "role": "STUDENT",
      "updated_at": "Tue, 01 Apr 2025 18:21:55 GMT"
    },
    "user_id": 24
  }
}
```

---

## ✅ GET /reports/attendance/student/9?course_id=7

**Timestamp:** 2025-04-01 21:21:57.148384
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
{
  "course_reports": [
    {
      "course_code": "TEST20250401212153",
      "course_id": 7,
      "details": [
        {
          "attendance_id": 4,
          "confidence": null,
          "created_at": "Tue, 01 Apr 2025 18:21:57 GMT",
          "emotion": null,
          "emotion_confidence": null,
          "emotion_statistics": null,
          "id": 4,
          "status": "EXCUSED",
          "student": null,
          "student_id": 9
        }
      ],
      "rate": 0.0
    }
  ],
  "overall_attendance_rate": 0.0,
  "student_info": {
    "created_at": "Tue, 01 Apr 2025 18:21:54 GMT",
    "department": "Computer Science & Eng.",
    "face_photo_url": "/C:\\Users\\mert1\\OneDrive\\Masa\u00fcst\u00fc\\yuztanima_backend\\app\\uploads\\faces/student_9_20250401212155.jpg",
    "id": 9,
    "student_number": "S20250401212153",
    "updated_at": "Tue, 01 Apr 2025 18:21:55 GMT",
    "user": {
      "created_at": "Tue, 01 Apr 2025 18:21:54 GMT",
      "email": "student_20250401212153@test.com",
      "first_name": "Test",
      "id": 24,
      "is_active": true,
      "last_name": "StudentUpdated",
      "role": "STUDENT",
      "updated_at": "Tue, 01 Apr 2025 18:21:55 GMT"
    },
    "user_id": 24
  }
}
```

---

## ✅ GET /reports/emotions/course/7

**Timestamp:** 2025-04-01 21:21:57.155085
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
{
  "course_code": "TEST20250401212153",
  "course_id": 7,
  "course_name": "API Test Course",
  "overall_emotion_stats": {},
  "timeline": []
}
```

---

## ✅ DELETE /courses/7

**Timestamp:** 2025-04-01 21:21:57.170720
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
{
  "message": "Course 7 and all associated data deleted successfully."
}
```

---

## ✅ DELETE /teachers/8

**Timestamp:** 2025-04-01 21:21:57.179383
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
{
  "message": "Teacher 8 and associated user 23 deleted successfully"
}
```

---

## ✅ DELETE /students/9

**Timestamp:** 2025-04-01 21:21:57.200798
**Status Code:** `200`

**Request Payload:** None

**Response Body:**
```json
{
  "message": "Student 9 and associated data deleted successfully"
}
```

---

