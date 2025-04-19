from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class NguoiDung(UserMixin, db.Model):
    __tablename__ = 'nguoi_dung'
    
    id = db.Column(db.Integer, primary_key=True)
    ho_ten = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    ten_dang_nhap = db.Column(db.String(50), unique=True, nullable=False)
    mat_khau_hash = db.Column(db.String(256), nullable=False)
    vai_tro = db.Column(db.String(20), default='nhan_vien')  # admin, nhan_vien
    trang_thai = db.Column(db.Boolean, default=True)
    ngay_tao = db.Column(db.DateTime, default=datetime.now)
    
    def set_password(self, password):
        self.mat_khau_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.mat_khau_hash, password)
    
    def __repr__(self):
        return f'<NguoiDung {self.ten_dang_nhap}>'

class DanhMuc(db.Model):
    __tablename__ = 'danh_muc'
    
    id = db.Column(db.Integer, primary_key=True)
    ten = db.Column(db.String(100), nullable=False)
    mo_ta = db.Column(db.Text, nullable=True)
    ngay_tao = db.Column(db.DateTime, default=datetime.now)
    
    san_pham = db.relationship('SanPham', backref='danh_muc', lazy=True)
    
    def __repr__(self):
        return f'<DanhMuc {self.ten}>'

class NhaCungCap(db.Model):
    __tablename__ = 'nha_cung_cap'
    
    id = db.Column(db.Integer, primary_key=True)
    ten = db.Column(db.String(100), nullable=False)
    dia_chi = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    so_dien_thoai = db.Column(db.String(20), nullable=True)
    nguoi_lien_he = db.Column(db.String(100), nullable=True)
    ghi_chu = db.Column(db.Text, nullable=True)
    trang_thai = db.Column(db.Boolean, default=True)
    ngay_tao = db.Column(db.DateTime, default=datetime.now)
    
    san_pham = db.relationship('SanPham', backref='nha_cung_cap', lazy=True)
    phieu_nhap = db.relationship('PhieuNhap', backref='nha_cung_cap', lazy=True)
    
    def __repr__(self):
        return f'<NhaCungCap {self.ten}>'

class SanPham(db.Model):
    __tablename__ = 'san_pham'
    
    id = db.Column(db.Integer, primary_key=True)
    ma_vach = db.Column(db.String(50), unique=True, nullable=True)
    ten = db.Column(db.String(200), nullable=False)
    mo_ta = db.Column(db.Text, nullable=True)
    thong_so_ky_thuat = db.Column(db.Text, nullable=True)
    don_vi_tinh = db.Column(db.String(50), nullable=True)
    gia_nhap = db.Column(db.Float, default=0)
    gia_ban = db.Column(db.Float, default=0)
    so_luong_toi_thieu = db.Column(db.Integer, default=10)
    so_luong_ton = db.Column(db.Integer, default=0)
    hinh_anh = db.Column(db.Text, nullable=True)  # Lưu dưới dạng base64 hoặc URL
    danh_muc_id = db.Column(db.Integer, db.ForeignKey('danh_muc.id'), nullable=True)
    nha_cung_cap_id = db.Column(db.Integer, db.ForeignKey('nha_cung_cap.id'), nullable=True)
    trang_thai = db.Column(db.Boolean, default=True)
    ngay_tao = db.Column(db.DateTime, default=datetime.now)
    
    chi_tiet_nhap = db.relationship('ChiTietNhap', backref='san_pham', lazy=True)
    chi_tiet_xuat = db.relationship('ChiTietXuat', backref='san_pham', lazy=True)
    
    def __repr__(self):
        return f'<SanPham {self.ten}>'

class PhieuNhap(db.Model):
    __tablename__ = 'phieu_nhap'
    
    id = db.Column(db.Integer, primary_key=True)
    ma_phieu = db.Column(db.String(50), unique=True, nullable=False)
    ngay_nhap = db.Column(db.DateTime, default=datetime.now)
    nha_cung_cap_id = db.Column(db.Integer, db.ForeignKey('nha_cung_cap.id'), nullable=True)
    nguoi_dung_id = db.Column(db.Integer, db.ForeignKey('nguoi_dung.id'), nullable=False)
    tong_tien = db.Column(db.Float, default=0)
    ghi_chu = db.Column(db.Text, nullable=True)
    trang_thai = db.Column(db.String(20), default='da_nhap')  # cho_duyet, da_nhap, huy_bo
    ngay_tao = db.Column(db.DateTime, default=datetime.now)
    
    nguoi_dung = db.relationship('NguoiDung', backref='phieu_nhap')
    chi_tiet = db.relationship('ChiTietNhap', backref='phieu_nhap', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<PhieuNhap {self.ma_phieu}>'

class ChiTietNhap(db.Model):
    __tablename__ = 'chi_tiet_nhap'
    
    id = db.Column(db.Integer, primary_key=True)
    phieu_nhap_id = db.Column(db.Integer, db.ForeignKey('phieu_nhap.id'), nullable=False)
    san_pham_id = db.Column(db.Integer, db.ForeignKey('san_pham.id'), nullable=False)
    so_luong = db.Column(db.Integer, default=1)
    don_gia = db.Column(db.Float, default=0)
    thanh_tien = db.Column(db.Float, default=0)
    
    def __repr__(self):
        return f'<ChiTietNhap {self.id}>'

class PhieuXuat(db.Model):
    __tablename__ = 'phieu_xuat'
    
    id = db.Column(db.Integer, primary_key=True)
    ma_phieu = db.Column(db.String(50), unique=True, nullable=False)
    ngay_xuat = db.Column(db.DateTime, default=datetime.now)
    nguoi_dung_id = db.Column(db.Integer, db.ForeignKey('nguoi_dung.id'), nullable=False)
    nguoi_nhan = db.Column(db.String(100), nullable=True)
    bo_phan = db.Column(db.String(100), nullable=True)
    tong_tien = db.Column(db.Float, default=0)
    ghi_chu = db.Column(db.Text, nullable=True)
    trang_thai = db.Column(db.String(20), default='da_xuat')  # cho_duyet, da_xuat, huy_bo
    ngay_tao = db.Column(db.DateTime, default=datetime.now)
    
    nguoi_dung = db.relationship('NguoiDung', backref='phieu_xuat')
    chi_tiet = db.relationship('ChiTietXuat', backref='phieu_xuat', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<PhieuXuat {self.ma_phieu}>'

class ChiTietXuat(db.Model):
    __tablename__ = 'chi_tiet_xuat'
    
    id = db.Column(db.Integer, primary_key=True)
    phieu_xuat_id = db.Column(db.Integer, db.ForeignKey('phieu_xuat.id'), nullable=False)
    san_pham_id = db.Column(db.Integer, db.ForeignKey('san_pham.id'), nullable=False)
    so_luong = db.Column(db.Integer, default=1)
    don_gia = db.Column(db.Float, default=0)
    thanh_tien = db.Column(db.Float, default=0)
    
    def __repr__(self):
        return f'<ChiTietXuat {self.id}>'
