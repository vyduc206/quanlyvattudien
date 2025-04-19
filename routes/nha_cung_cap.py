from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import NhaCungCap
import logging
from datetime import datetime
from sqlalchemy import or_

bp = Blueprint('nha_cung_cap', __name__, url_prefix='/nha-cung-cap')

@bp.route('/')
@login_required
def index():
    # Lấy thông tin tìm kiếm từ query params
    search = request.args.get('search', '')
    trang_thai = request.args.get('trang_thai')
    
    # Lấy thông tin sắp xếp
    sort_by = request.args.get('sort_by', 'ten')
    sort_dir = request.args.get('sort_dir', 'asc')
    
    # Lấy thông tin phân trang
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Khởi tạo query
    query = NhaCungCap.query
    
    # Áp dụng bộ lọc tìm kiếm
    if search:
        query = query.filter(
            or_(
                NhaCungCap.ten.ilike(f'%{search}%'),
                NhaCungCap.email.ilike(f'%{search}%'),
                NhaCungCap.so_dien_thoai.ilike(f'%{search}%'),
                NhaCungCap.nguoi_lien_he.ilike(f'%{search}%')
            )
        )
    
    if trang_thai is not None:
        query = query.filter(NhaCungCap.trang_thai == (trang_thai == 'true'))
    
    # Áp dụng sắp xếp
    if sort_by == 'ten':
        query = query.order_by(NhaCungCap.ten.asc() if sort_dir == 'asc' else NhaCungCap.ten.desc())
    elif sort_by == 'email':
        query = query.order_by(NhaCungCap.email.asc() if sort_dir == 'asc' else NhaCungCap.email.desc())
    elif sort_by == 'ngay_tao':
        query = query.order_by(NhaCungCap.ngay_tao.asc() if sort_dir == 'asc' else NhaCungCap.ngay_tao.desc())
    else:
        query = query.order_by(NhaCungCap.id.asc() if sort_dir == 'asc' else NhaCungCap.id.desc())
    
    # Lấy danh sách nhà cung cấp phân trang
    nha_cung_cap_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template(
        'nha_cung_cap/index.html',
        nha_cung_cap_list=nha_cung_cap_pagination.items,
        pagination=nha_cung_cap_pagination,
        search=search,
        trang_thai=trang_thai,
        sort_by=sort_by,
        sort_dir=sort_dir
    )

@bp.route('/them', methods=['GET', 'POST'])
@login_required
def them():
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        ten = request.form.get('ten')
        dia_chi = request.form.get('dia_chi')
        email = request.form.get('email')
        so_dien_thoai = request.form.get('so_dien_thoai')
        nguoi_lien_he = request.form.get('nguoi_lien_he')
        ghi_chu = request.form.get('ghi_chu')
        
        # Kiểm tra dữ liệu đầu vào
        if not ten:
            flash('Vui lòng nhập tên nhà cung cấp!', 'danger')
            return render_template('nha_cung_cap/them.html')
        
        # Tạo nhà cung cấp mới
        new_supplier = NhaCungCap(
            ten=ten,
            dia_chi=dia_chi,
            email=email,
            so_dien_thoai=so_dien_thoai,
            nguoi_lien_he=nguoi_lien_he,
            ghi_chu=ghi_chu,
            trang_thai=True,
            ngay_tao=datetime.now()
        )
        
        # Lưu vào cơ sở dữ liệu
        try:
            db.session.add(new_supplier)
            db.session.commit()
            flash('Thêm nhà cung cấp thành công!', 'success')
            return redirect(url_for('nha_cung_cap.index'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Lỗi khi thêm nhà cung cấp: {str(e)}")
            flash('Đã xảy ra lỗi, vui lòng thử lại sau!', 'danger')
    
    return render_template('nha_cung_cap/them.html')

@bp.route('/sua/<int:id>', methods=['GET', 'POST'])
@login_required
def sua(id):
    # Lấy thông tin nhà cung cấp
    nha_cung_cap = NhaCungCap.query.get_or_404(id)
    
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        ten = request.form.get('ten')
        dia_chi = request.form.get('dia_chi')
        email = request.form.get('email')
        so_dien_thoai = request.form.get('so_dien_thoai')
        nguoi_lien_he = request.form.get('nguoi_lien_he')
        ghi_chu = request.form.get('ghi_chu')
        trang_thai = request.form.get('trang_thai') == 'on'
        
        # Kiểm tra dữ liệu đầu vào
        if not ten:
            flash('Vui lòng nhập tên nhà cung cấp!', 'danger')
            return render_template('nha_cung_cap/sua.html', nha_cung_cap=nha_cung_cap)
        
        # Cập nhật thông tin nhà cung cấp
        nha_cung_cap.ten = ten
        nha_cung_cap.dia_chi = dia_chi
        nha_cung_cap.email = email
        nha_cung_cap.so_dien_thoai = so_dien_thoai
        nha_cung_cap.nguoi_lien_he = nguoi_lien_he
        nha_cung_cap.ghi_chu = ghi_chu
        nha_cung_cap.trang_thai = trang_thai
        
        # Lưu vào cơ sở dữ liệu
        try:
            db.session.commit()
            flash('Cập nhật nhà cung cấp thành công!', 'success')
            return redirect(url_for('nha_cung_cap.index'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Lỗi khi cập nhật nhà cung cấp: {str(e)}")
            flash('Đã xảy ra lỗi, vui lòng thử lại sau!', 'danger')
    
    return render_template('nha_cung_cap/sua.html', nha_cung_cap=nha_cung_cap)

@bp.route('/xoa/<int:id>', methods=['POST'])
@login_required
def xoa(id):
    # Lấy thông tin nhà cung cấp
    nha_cung_cap = NhaCungCap.query.get_or_404(id)
    
    try:
        # Thay vì xóa, chỉ thay đổi trạng thái
        nha_cung_cap.trang_thai = False
        db.session.commit()
        flash('Đã vô hiệu hóa nhà cung cấp thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Lỗi khi vô hiệu hóa nhà cung cấp: {str(e)}")
        flash('Đã xảy ra lỗi, vui lòng thử lại sau!', 'danger')
    
    return redirect(url_for('nha_cung_cap.index'))
