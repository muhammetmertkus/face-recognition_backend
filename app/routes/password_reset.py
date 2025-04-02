import os
import secrets
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import default_datetime
from app.services import data_service
from app.utils.auth import admin_required
import html
import bcrypt
from ..models.user import User, db

password_reset = Blueprint('password_reset', __name__)

USERS_FILE = 'users.json'

def generate_password(length=12):
    """Güvenli bir şifre oluşturur."""
    alphabet = string.ascii_letters + string.digits + '!@#$%&*'
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    # Şifrenin en az bir büyük harf, bir küçük harf, bir rakam ve bir özel karakter içerdiğinden emin olun
    while (not any(c.isupper() for c in password)
           or not any(c.islower() for c in password)
           or not any(c.isdigit() for c in password)
           or not any(c in '!@#$%&*' for c in password)):
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    return password

def send_password_reset_email(email, new_password):
    """Şifre sıfırlama e-postasını gönderir."""
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "bykusbilet@gmail.com"  # Gönderen e-posta
    app_password = "oqbw kgrc ptlt iotl"  # Uygulama şifresi
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Şifre Sıfırlama - Yüz Tanıma Sistemi"
    msg["From"] = sender_email
    msg["To"] = email
    
    # HTML içeriği oluştur
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
            }}
            .container {{
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 20px;
                margin-top: 20px;
            }}
            .header {{
                background-color: #4285f4;
                color: white;
                padding: 10px;
                text-align: center;
                border-radius: 5px 5px 0 0;
                margin-bottom: 20px;
            }}
            .password-box {{
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                padding: 15px;
                text-align: center;
                font-size: 18px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .footer {{
                font-size: 12px;
                color: #777;
                margin-top: 20px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Yüz Tanıma Sistemi</h2>
            </div>
            <p>Sayın Kullanıcı,</p>
            <p>Şifreniz başarıyla sıfırlanmıştır. Yeni şifreniz aşağıda belirtilmiştir:</p>
            
            <div class="password-box">
                <strong>{html.escape(new_password)}</strong>
            </div>
            
            <p>Güvenlik nedeniyle, sisteme giriş yaptıktan sonra bu şifreyi değiştirmenizi önemle tavsiye ederiz.</p>
            <p>Eğer bu şifre sıfırlama talebini siz yapmadıysanız, lütfen derhal sistem yöneticisiyle iletişime geçiniz.</p>
            
            <p>Saygılarımızla,<br>Yüz Tanıma Sistemi Ekibi</p>
            
            <div class="footer">
                <p>Bu e-posta otomatik olarak gönderilmiştir, lütfen yanıtlamayınız.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # HTML içeriğini email mesajına ekle
    html_part = MIMEText(html_content, "html")
    msg.attach(html_part)
    
    try:
        # Email gönderme
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
        return True, None
    except Exception as e:
        return False, str(e)

@password_reset.route('/reset', methods=['POST'])
def reset_password():
    """
    Kullanıcı şifresini sıfırlar ve yeni şifreyi email ile gönderir.
    Bu endpoint kimlik doğrulama gerektirmez, şifresini unutan kullanıcılar için.
    """
    data = request.get_json()
    
    if not data or 'email' not in data:
        return jsonify({"message": "Email adresi gereklidir"}), 400
    
    email = data['email']
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "Bu email adresine sahip kullanıcı bulunamadı"}), 404
    
    # Yeni şifre oluştur
    new_password = generate_password()
    
    # Şifreyi hashle
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    
    # Kullanıcının şifresini güncelle
    user.password = hashed_password
    db.session.commit()
    
    # Email gönder
    email_sent, error = send_password_reset_email(email, new_password)
    
    if email_sent:
        return jsonify({"message": "Şifre başarıyla sıfırlandı ve email gönderildi"}), 200
    else:
        # Geliştirme ortamında şifreyi döndür
        if current_app.config.get('DEBUG', False):
            return jsonify({
                "message": "Şifre sıfırlandı ancak email gönderiminde hata oluştu",
                "error": error,
                "password": new_password
            }), 500
        else:
            return jsonify({
                "message": "Şifre sıfırlandı ancak email gönderiminde hata oluştu"
            }), 500

@password_reset.route('/admin/reset', methods=['POST'])
@jwt_required()
@admin_required
def admin_reset_password():
    """
    Admin tarafından kullanıcı şifresini sıfırlar ve yeni şifreyi email ile gönderir.
    Bu endpoint admin yetkisi gerektirir.
    """
    data = request.get_json()
    
    if not data or 'email' not in data:
        return jsonify({"message": "Email adresi gereklidir"}), 400
    
    email = data['email']
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "Bu email adresine sahip kullanıcı bulunamadı"}), 404
    
    # Yeni şifre oluştur
    new_password = generate_password()
    
    # Şifreyi hashle
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    
    # Kullanıcının şifresini güncelle
    user.password = hashed_password
    db.session.commit()
    
    # Email gönder
    email_sent, error = send_password_reset_email(email, new_password)
    
    if email_sent:
        return jsonify({"message": "Şifre başarıyla sıfırlandı ve email gönderildi"}), 200
    else:
        # Geliştirme ortamında şifreyi döndür
        if current_app.config.get('DEBUG', False):
            return jsonify({
                "message": "Şifre sıfırlandı ancak email gönderiminde hata oluştu",
                "error": error,
                "password": new_password
            }), 500
        else:
            return jsonify({
                "message": "Şifre sıfırlandı ancak email gönderiminde hata oluştu"
            }), 500

@password_reset.route('/reset/self', methods=['POST'])
@jwt_required()
def reset_own_password():
    """
    Kullanıcı kendi şifresini sıfırlar ve yeni şifreyi kendi email adresine gönderir.
    Kullanıcı kimliği JWT tokendan alınır.
    """
    user_id = get_jwt_identity()
    
    user = User.query.get(user_id)
    if not user or not user.email:
        return jsonify({"message": "Kullanıcı bulunamadı veya email adresi eksik"}), 404
    
    # Yeni şifre oluştur
    new_password = generate_password()
    
    # Şifreyi hashle
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    
    # Kullanıcının şifresini güncelle
    user.password = hashed_password
    db.session.commit()
    
    # Email gönder
    email_sent, error = send_password_reset_email(user.email, new_password)
    
    if email_sent:
        return jsonify({"message": "Şifreniz başarıyla sıfırlandı ve email adresinize gönderildi"}), 200
    else:
        # Geliştirme ortamında şifreyi döndür
        if current_app.config.get('DEBUG', False):
            return jsonify({
                "message": "Şifre sıfırlandı ancak email gönderiminde hata oluştu",
                "error": error,
                "password": new_password
            }), 500
        else:
            return jsonify({
                "message": "Şifre sıfırlandı ancak email gönderiminde hata oluştu"
            }), 500 