from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from models import NguoiDung
import logging

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        ten_dang_nhap = request.form.get('ten_dang_nhap')
        mat_khau = request.form.get('mat_khau')
        
        # Thông báo lỗi nếu thiếu thông tin
        if not ten_dang_nhap or not mat_khau:
            flash('Vui lòng nhập đầy đủ thông tin đăng nhập!', 'danger')
            return render_template('login.html')
        
        # Tìm người dùng trong cơ sở dữ liệu
        user = NguoiDung.query.filter_by(ten_dang_nhap=ten_dang_nhap).first()
        
        # Kiểm tra người dùng và mật khẩu
        if not user or not user.check_password(mat_khau):
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'danger')
            return render_template('login.html')
            
        # Kiểm tra trạng thái tài khoản
        if not user.trang_thai:
            flash('Tài khoản của bạn đã bị vô hiệu hóa!', 'danger')
            return render_template('login.html')
        
        # Đăng nhập người dùng
        login_user(user)
        flash(f'Xin chào, {user.ho_ten}!', 'success')
        
        # Chuyển hướng đến trang được yêu cầu trước đó (nếu có)
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('index'))
    
    return render_template('login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        ho_ten = request.form.get('ho_ten')
        email = request.form.get('email')
        ten_dang_nhap = request.form.get('ten_dang_nhap')
        mat_khau = request.form.get('mat_khau')
        xac_nhan_mat_khau = request.form.get('xac_nhan_mat_khau')
        
        # Kiểm tra xem đã điền đầy đủ thông tin chưa
        if not ho_ten or not email or not ten_dang_nhap or not mat_khau or not xac_nhan_mat_khau:
            flash('Vui lòng điền đầy đủ thông tin!', 'danger')
            return render_template('register.html')
        
        # Kiểm tra mật khẩu xác nhận
        if mat_khau != xac_nhan_mat_khau:
            flash('Mật khẩu xác nhận không khớp!', 'danger')
            return render_template('register.html')
        
        # Kiểm tra email đã tồn tại chưa
        user_email = NguoiDung.query.filter_by(email=email).first()
        if user_email:
            flash('Email đã được sử dụng!', 'danger')
            return render_template('register.html')
        
        # Kiểm tra tên đăng nhập đã tồn tại chưa
        user_username = NguoiDung.query.filter_by(ten_dang_nhap=ten_dang_nhap).first()
        if user_username:
            flash('Tên đăng nhập đã tồn tại!', 'danger')
            return render_template('register.html')
        
        # Tạo người dùng mới
        new_user = NguoiDung(
            ho_ten=ho_ten,
            email=email,
            ten_dang_nhap=ten_dang_nhap,
            vai_tro='nhan_vien'  # Mặc định là nhân viên
        )
        new_user.set_password(mat_khau)
        
        # Kiểm tra xem có phải là người dùng đầu tiên không
        user_count = NguoiDung.query.count()
        if user_count == 0:
            new_user.vai_tro = 'admin'  # Người dùng đầu tiên là admin
        
        # Lưu vào cơ sở dữ liệu
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Lỗi khi đăng ký: {str(e)}")
            flash('Đã xảy ra lỗi, vui lòng thử lại sau!', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất thành công!', 'success')
    return redirect(url_for('auth.login'))

@bp.route('/doi-mat-khau', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        mat_khau_cu = request.form.get('mat_khau_cu')
        mat_khau_moi = request.form.get('mat_khau_moi')
        xac_nhan_mat_khau = request.form.get('xac_nhan_mat_khau')
        
        # Kiểm tra mật khẩu cũ
        if not current_user.check_password(mat_khau_cu):
            flash('Mật khẩu hiện tại không đúng!', 'danger')
            return render_template('doi_mat_khau.html')
        
        # Kiểm tra mật khẩu mới và xác nhận
        if mat_khau_moi != xac_nhan_mat_khau:
            flash('Mật khẩu xác nhận không khớp!', 'danger')
            return render_template('doi_mat_khau.html')
        
        # Cập nhật mật khẩu
        current_user.set_password(mat_khau_moi)
        db.session.commit()
        
        flash('Đổi mật khẩu thành công!', 'success')
        return redirect(url_for('index'))
    
    return render_template('doi_mat_khau.html')
