from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import DanhMuc
import logging
from datetime import datetime
from sqlalchemy import or_

bp = Blueprint('danh_muc', __name__, url_prefix='/danh-muc')

@bp.route('/')
@login_required
def index():
    # Lấy thông tin tìm kiếm từ query params
    search = request.args.get('search', '')
    
    # Lấy thông tin sắp xếp
    sort_by = request.args.get('sort_by', 'ten')
    sort_dir = request.args.get('sort_dir', 'asc')
    
    # Lấy thông tin phân trang
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Khởi tạo query
    query = DanhMuc.query
    
    # Áp dụng bộ lọc tìm kiếm
    if search:
        query = query.filter(
            or_(
                DanhMuc.ten.ilike(f'%{search}%'),
                DanhMuc.mo_ta.ilike(f'%{search}%')
            )
        )
    
    # Áp dụng sắp xếp
    if sort_by == 'ten':
        query = query.order_by(DanhMuc.ten.asc() if sort_dir == 'asc' else DanhMuc.ten.desc())
    elif sort_by == 'ngay_tao':
        query = query.order_by(DanhMuc.ngay_tao.asc() if sort_dir == 'asc' else DanhMuc.ngay_tao.desc())
    else:
        query = query.order_by(DanhMuc.id.asc() if sort_dir == 'asc' else DanhMuc.id.desc())
    
    # Lấy danh sách danh mục phân trang
    danh_muc_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template(
        'danh_muc/index.html',
        danh_muc_list=danh_muc_pagination.items,
        pagination=danh_muc_pagination,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir
    )

@bp.route('/them', methods=['GET', 'POST'])
@login_required
def them():
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        ten = request.form.get('ten')
        mo_ta = request.form.get('mo_ta')
        
        # Kiểm tra dữ liệu đầu vào
        if not ten:
            flash('Vui lòng nhập tên danh mục!', 'danger')
            return render_template('danh_muc/them.html')
        
        # Kiểm tra danh mục đã tồn tại chưa
        existing_category = DanhMuc.query.filter_by(ten=ten).first()
        if existing_category:
            flash('Danh mục này đã tồn tại!', 'danger')
            return render_template('danh_muc/them.html')
        
        # Tạo danh mục mới
        new_category = DanhMuc(
            ten=ten,
            mo_ta=mo_ta,
            ngay_tao=datetime.now()
        )
        
        # Lưu vào cơ sở dữ liệu
        try:
            db.session.add(new_category)
            db.session.commit()
            flash('Thêm danh mục thành công!', 'success')
            return redirect(url_for('danh_muc.index'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Lỗi khi thêm danh mục: {str(e)}")
            flash('Đã xảy ra lỗi, vui lòng thử lại sau!', 'danger')
    
    return render_template('danh_muc/them.html')

@bp.route('/sua/<int:id>', methods=['GET', 'POST'])
@login_required
def sua(id):
    # Lấy thông tin danh mục
    danh_muc = DanhMuc.query.get_or_404(id)
    
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        ten = request.form.get('ten')
        mo_ta = request.form.get('mo_ta')
        
        # Kiểm tra dữ liệu đầu vào
        if not ten:
            flash('Vui lòng nhập tên danh mục!', 'danger')
            return render_template('danh_muc/sua.html', danh_muc=danh_muc)
        
        # Kiểm tra danh mục đã tồn tại chưa (nếu tên thay đổi)
        if ten != danh_muc.ten:
            existing_category = DanhMuc.query.filter_by(ten=ten).first()
            if existing_category:
                flash('Danh mục này đã tồn tại!', 'danger')
                return render_template('danh_muc/sua.html', danh_muc=danh_muc)
        
        # Cập nhật thông tin danh mục
        danh_muc.ten = ten
        danh_muc.mo_ta = mo_ta
        
        # Lưu vào cơ sở dữ liệu
        try:
            db.session.commit()
            flash('Cập nhật danh mục thành công!', 'success')
            return redirect(url_for('danh_muc.index'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Lỗi khi cập nhật danh mục: {str(e)}")
            flash('Đã xảy ra lỗi, vui lòng thử lại sau!', 'danger')
    
    return render_template('danh_muc/sua.html', danh_muc=danh_muc)

@bp.route('/xoa/<int:id>', methods=['POST'])
@login_required
def xoa(id):
    # Lấy thông tin danh mục
    danh_muc = DanhMuc.query.get_or_404(id)
    
    # Kiểm tra danh mục có sản phẩm không
    if danh_muc.san_pham and len(danh_muc.san_pham) > 0:
        flash('Không thể xóa danh mục này vì có sản phẩm thuộc danh mục!', 'danger')
        return redirect(url_for('danh_muc.index'))
    
    try:
        # Xóa danh mục
        db.session.delete(danh_muc)
        db.session.commit()
        flash('Xóa danh mục thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Lỗi khi xóa danh mục: {str(e)}")
        flash('Đã xảy ra lỗi, vui lòng thử lại sau!', 'danger')
    
    return redirect(url_for('danh_muc.index'))
