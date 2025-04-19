from flask import Blueprint
from app import app
from routes.auth import auth_bp
from routes.san_pham import san_pham_bp
from routes.danh_muc import danh_muc_bp
from routes.nha_cung_cap import nha_cung_cap_bp
from routes.nhap_kho import nhap_kho_bp
from routes.xuat_kho import xuat_kho_bp
from routes.bao_cao import bao_cao_bp
from routes.hang_san_xuat import hang_san_xuat_bp

# Đăng ký các blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(san_pham_bp)
app.register_blueprint(danh_muc_bp)
app.register_blueprint(nha_cung_cap_bp)
app.register_blueprint(nhap_kho_bp)
app.register_blueprint(xuat_kho_bp)
app.register_blueprint(bao_cao_bp)
app.register_blueprint(hang_san_xuat_bp)
