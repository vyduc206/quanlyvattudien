import os
import logging
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager, current_user

# Cấu hình logging
logging.basicConfig(level=logging.DEBUG)

# Tạo class Base cho SQLAlchemy
Base = declarative_base()

# Khởi tạo SQLAlchemy
db = SQLAlchemy()

# Tạo ứng dụng Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "mat-khau-bi-mat-tam-thoi")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # Cần thiết cho url_for để tạo với https

# Cấu hình cơ sở dữ liệu
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith('postgres://'):
    # Heroku và một số nền tảng khác sử dụng postgres://, nhưng SQLAlchemy cần postgresql://
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    # Fallback to SQLite
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(BASE_DIR, 'quan_ly_vat_tu.db')
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Cấu hình thời gian tải lên tối đa (10MB)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

# Khởi tạo SQLAlchemy với ứng dụng
db.init_app(app)

# Cấu hình Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = "Vui lòng đăng nhập để tiếp tục!"

# Khởi tạo cơ sở dữ liệu và import models
with app.app_context():
    import models
    db.create_all()

# Import các routes
from routes import auth, san_pham, nhap_kho, xuat_kho, nha_cung_cap, danh_muc, bao_cao

# Đăng ký các blueprint
app.register_blueprint(auth.bp)
app.register_blueprint(san_pham.bp)
app.register_blueprint(nhap_kho.bp)
app.register_blueprint(xuat_kho.bp)
app.register_blueprint(nha_cung_cap.bp)
app.register_blueprint(danh_muc.bp)
app.register_blueprint(bao_cao.bp)

@login_manager.user_loader
def load_user(user_id):
    from models import NguoiDung
    return NguoiDung.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    else:
        return redirect(url_for('auth.login'))

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
