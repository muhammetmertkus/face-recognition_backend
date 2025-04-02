# Şifre Sıfırlama API Dokümantasyonu

Bu dokümantasyon, şifre sıfırlama ile ilgili API endpoint'lerini detaylı olarak açıklar.

## 1. Şifre Sıfırlama (Kimlik Doğrulama Gerektirmez)

Kullanıcının şifresini sıfırlar ve yeni şifreyi kullanıcının email adresine gönderir. Bu endpoint kimlik doğrulama gerektirmez, şifresini unutan kullanıcılar için uygundur.

### İstek

```
POST /api/password/reset
```

**İçerik Tipi**: application/json

**Body Parametreleri**:

```json
{
  "email": "kullanici@ornek.com"
}
```

**Örnek İstek (curl)**:

```bash
curl -X POST "http://localhost:5000/api/password/reset" \
  -H "Content-Type: application/json" \
  -d '{"email": "kullanici@ornek.com"}'
```

**Örnek İstek (JavaScript)**:

```javascript
const response = await fetch('http://localhost:5000/api/password/reset', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'kullanici@ornek.com'
  })
});

const result = await response.json();
```

### Yanıt

**Başarılı Yanıt (200 OK)**:

```json
{
  "message": "Şifre başarıyla sıfırlandı ve email gönderildi"
}
```

**Olası Hata Yanıtları**:

- `400 Bad Request`: Email adresi verilmemiş
  ```json
  {
    "message": "Email adresi gereklidir"
  }
  ```

- `404 Not Found`: Belirtilen email adresine sahip kullanıcı bulunamadı
  ```json
  {
    "message": "Bu email adresine sahip kullanıcı bulunamadı"
  }
  ```

- `500 Internal Server Error`: Email gönderimi sırasında hata oluştu
  ```json
  {
    "message": "Şifre sıfırlandı ancak email gönderiminde hata oluştu",
    "password": "yeniSifre123!"  // Sadece geliştirme ortamında görünür
  }
  ```

## 2. Admin Tarafından Şifre Sıfırlama

Bir kullanıcının şifresini sıfırlar ve yeni şifreyi email ile gönderir. Sadece admin yetkisiyle kullanılabilir.

### İstek

```
POST /api/password/admin/reset
```

**Yetki**: Sadece admin kullanabilir.

**İçerik Tipi**: application/json

**Body Parametreleri**:

```json
{
  "email": "kullanici@ornek.com"
}
```

**Örnek İstek (curl)**:

```bash
curl -X POST "http://localhost:5000/api/password/admin/reset" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"email": "kullanici@ornek.com"}'
```

**Örnek İstek (JavaScript)**:

```javascript
const response = await fetch('http://localhost:5000/api/password/admin/reset', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'kullanici@ornek.com'
  })
});

const result = await response.json();
```

### Yanıt

**Başarılı Yanıt (200 OK)**:

```json
{
  "message": "Şifre başarıyla sıfırlandı ve email gönderildi"
}
```

**Olası Hata Yanıtları**:

- `400 Bad Request`: Email adresi verilmemiş
- `401 Unauthorized`: Geçerli token sağlanmadı
- `403 Forbidden`: Kullanıcı Admin değil
- `404 Not Found`: Belirtilen email adresine sahip kullanıcı bulunamadı
- `500 Internal Server Error`: Email gönderimi sırasında hata oluştu

## 3. Kullanıcının Kendi Şifresini Sıfırlama

Giriş yapmış olan kullanıcının kendi şifresini sıfırlar ve yeni şifreyi email adresine gönderir.

### İstek

```
POST /api/password/reset/self
```

**Yetki**: Giriş yapmış herhangi bir kullanıcı kullanabilir (JWT token gerekli).

**Örnek İstek (curl)**:

```bash
curl -X POST "http://localhost:5000/api/password/reset/self" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Örnek İstek (JavaScript)**:

```javascript
const response = await fetch('http://localhost:5000/api/password/reset/self', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
  }
});

const result = await response.json();
```

### Yanıt

**Başarılı Yanıt (200 OK)**:

```json
{
  "message": "Şifreniz başarıyla sıfırlandı ve email adresinize gönderildi"
}
```

**Olası Hata Yanıtları**:

- `401 Unauthorized`: Geçerli token sağlanmadı
- `404 Not Found`: Kullanıcı bulunamadı veya email adresi eksik
- `500 Internal Server Error`: Email gönderimi sırasında hata oluştu

## Email Formatı

Şifre sıfırlama emaili profesyonel bir HTML formatında gönderilir. Email içeriği:

1. Şirket logosu ve başlık
2. Kullanıcıya hoş geldin mesajı
3. Yeni şifre (vurgulanmış ve belirgin bir kutu içinde)
4. Şifre güvenliği ve değiştirme tavsiyesi
5. İletişim bilgileri

## Güvenlik Notları

- Şifreler bcrypt ile güvenli bir şekilde hashlenip saklanır
- Yeni şifreler, sayılar, harfler ve özel karakterler içeren 12 karakter uzunluğunda rastgele oluşturulur
- Email gönderimi SSL şifrelemesi ile yapılır
- Mail gönderimi sırasında hata oluşması durumunda, sadece geliştirme ortamında şifre yanıtta görünür. Production ortamında bu özellik kapatılmalıdır 