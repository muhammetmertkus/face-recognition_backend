import os
import secrets
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.models.user import default_datetime
from app.services import data_service
from app.utils.auth import admin_required

password_reset_bp = Blueprint('password_reset_bp', __name__)

USERS_FILE = 'users.json'

def generate_secure_password(length=10):
    """Güvenli rastgele şifre oluştur"""
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*()_+=-'
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def send_password_reset_email(email, new_password):
    """Yeni şifreyi email olarak gönder"""
    sender_email = "bykusbilet@gmail.com"
    app_password = "htln pcbf bfli bqgr"  # Gmail uygulama şifresi
    
    # Email mesajı oluştur
    message = MIMEMultipart("alternative")
    message["Subject"] = "Şifre Sıfırlama - Yüz Tanıma Sistemi"
    message["From"] = sender_email
    message["To"] = email
    
    # HTML içeriği oluştur
    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }}
            .header {{
                background-color: #4a86e8;
                color: white;
                padding: 10px 20px;
                border-radius: 5px 5px 0 0;
                text-align: center;
            }}
            .content {{
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .password-box {{
                background-color: #fff;
                border: 1px solid #ddd;
                padding: 10px;
                margin: 15px 0;
                text-align: center;
                font-size: 20px;
                font-weight: bold;
                letter-spacing: 1px;
                border-radius: 3px;
            }}
            .footer {{
                text-align: center;
                font-size: 12px;
                color: #777;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Şifre Sıfırlama</h2>
            </div>
            <div class="content">
                <p>Merhaba,</p>
                <p>Yüz Tanıma Sistemine erişim için şifreniz sıfırlanmıştır. Yeni şifreniz aşağıda verilmiştir:</p>
                
                <div class="password-box">
                    {new_password}
                </div>
                
                <p>Sisteme giriş yaptıktan sonra güvenlik için şifrenizi değiştirmenizi öneriyoruz.</p>
                <p>Bu şifre sıfırlama talebinde bulunmadıysanız, lütfen sistem yöneticisiyle iletişime geçin.</p>
                <p>Saygılarımızla,<br>Yüz Tanıma Sistemi Ekibi</p>
            </div>
            <div class="footer">
                <p>Bu mail otomatik olarak gönderilmiştir, lütfen yanıtlamayınız.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # HTML içeriğini MIMEText nesnesine ekle
    part = MIMEText(html, "html")
    message.attach(part)
    
    try:
        # SMTP sunucuya bağlan
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, app_password)
        
        # Email'i gönder
        server.sendmail(sender_email, email, message.as_string())
        server.quit()
        
        current_app.logger.info(f"Şifre sıfırlama email'i {email} adresine gönderildi.")
        return True
    except Exception as e:
        current_app.logger.error(f"Email gönderimi sırasında hata: {e}")
        return False

@password_reset_bp.route('/reset', methods=['POST'])
@admin_required  # Sadece adminler başkalarının şifresini sıfırlayabilir
def reset_password():
    """
    Kullanıcının şifresini sıfırlar ve yeni şifreyi email ile gönderir.
    ---
    tags:
      - Şifre Yönetimi
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
          properties:
            email:
              type: string
              description: Şifresi sıfırlanacak kullanıcının email adresi
              example: "kullanici@ornek.com"
    responses:
      200:
        description: Şifre başarıyla sıfırlandı ve email gönderildi
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Şifre başarıyla sıfırlandı ve email gönderildi"
      400:
        description: Geçersiz istek (email verilmemiş)
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Email adresi gereklidir"
      404:
        description: Belirtilen email adresiyle kullanıcı bulunamadı
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Bu email adresine sahip kullanıcı bulunamadı"
      500:
        description: Email gönderimi sırasında hata oluştu
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Şifre sıfırlandı ancak email gönderiminde hata oluştu"
    """
    data = request.get_json()
    
    if not data or 'email' not in data:
        return jsonify({"message": "Email adresi gereklidir"}), 400
    
    email = data['email']
    
    # Kullanıcıyı email ile bul
    user = data_service.find_one(USERS_FILE, email=email)
    if not user:
        return jsonify({"message": "Bu email adresine sahip kullanıcı bulunamadı"}), 404
    
    # Yeni şifre oluştur
    new_password = generate_secure_password(12)  # 12 karakterli güvenli şifre
    
    # Şifreyi hashle ve kullanıcıyı güncelle
    import bcrypt
    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    updates = {
        "password_hash": password_hash,
        "updated_at": default_datetime()
    }
    
    updated_user = data_service.update_item(USERS_FILE, user['id'], updates)
    
    if not updated_user:
        return jsonify({"message": "Şifre güncellenirken bir hata oluştu"}), 500
    
    # Email gönder
    email_sent = send_password_reset_email(email, new_password)
    
    if email_sent:
        return jsonify({"message": "Şifre başarıyla sıfırlandı ve email gönderildi"}), 200
    else:
        return jsonify({
            "message": "Şifre sıfırlandı ancak email gönderiminde hata oluştu",
            "password": new_password  # Hata durumunda şifreyi yanıtta görüntüle (Sadece geliştirme ortamında kullanılmalı)
        }), 500

@password_reset_bp.route('/reset/self', methods=['POST'])
@jwt_required()  # Kullanıcının kendi şifresini sıfırlaması için JWT token gerekli
def reset_own_password():
    """
    Giriş yapmış kullanıcının kendi şifresini sıfırlar ve yeni şifreyi email ile gönderir.
    ---
    tags:
      - Şifre Yönetimi
    security:
      - Bearer: []
    responses:
      200:
        description: Şifre başarıyla sıfırlandı ve email gönderildi
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Şifreniz başarıyla sıfırlandı ve email adresinize gönderildi"
      404:
        description: Kullanıcı bulunamadı veya email adresi eksik
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Kullanıcı bulunamadı veya email adresi eksik"
      500:
        description: Email gönderimi sırasında hata oluştu
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Şifre sıfırlandı ancak email gönderiminde hata oluştu"
    """
    from flask_jwt_extended import get_jwt_identity
    
    # JWT token'dan kullanıcı ID'sini al
    user_id = get_jwt_identity()
    
    # Kullanıcıyı ID ile bul
    user = data_service.find_one(USERS_FILE, id=user_id)
    if not user or not user.get('email'):
        return jsonify({"message": "Kullanıcı bulunamadı veya email adresi eksik"}), 404
    
    # Yeni şifre oluştur
    new_password = generate_secure_password(12)  # 12 karakterli güvenli şifre
    
    # Şifreyi hashle ve kullanıcıyı güncelle
    import bcrypt
    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    updates = {
        "password_hash": password_hash,
        "updated_at": default_datetime()
    }
    
    updated_user = data_service.update_item(USERS_FILE, user_id, updates)
    
    if not updated_user:
        return jsonify({"message": "Şifre güncellenirken bir hata oluştu"}), 500
    
    # Email gönder
    email_sent = send_password_reset_email(user['email'], new_password)
    
    if email_sent:
        return jsonify({"message": "Şifreniz başarıyla sıfırlandı ve email adresinize gönderildi"}), 200
    else:
        return jsonify({
            "message": "Şifre sıfırlandı ancak email gönderiminde hata oluştu",
            "password": new_password  # Hata durumunda şifreyi yanıtta görüntüle (Sadece geliştirme ortamında kullanılmalı)
        }), 500 