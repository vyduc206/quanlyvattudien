from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import SanPham, DanhMuc, NhaCungCap
from utils import process_base64_image, scan_barcode_from_base64
import logging
from datetime import datetime

bp = Blueprint('san_pham', __name__, url_prefix='/san-pham')

@bp.route('/')
@login_required
def index():
    # Lấy thông tin tìm kiếm từ query params
    search = request.args.get('search', '')
    danh_muc_id = request.args.get('danh_muc_id', type=int)
    nha_cung_cap_id = request.args.get('nha_cung_cap_id', type=int)
    trang_thai = request.args.get('trang_thai')
    
    # Lấy thông tin sắp xếp
    sort_by = request.args.get('sort_by', 'id')
    sort_dir = request.args.get('sort_dir', 'desc')
    
    # Lấy thông tin phân trang
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Khởi tạo query
    query = SanPham.query
    
    # Áp dụng bộ lọc tìm kiếm
    if search:
        query = query.filter(
            (SanPham.ten.ilike(f'%{search}%')) | 
            (SanPham.ma_vach.ilike(f'%{search}%'))
        )
    
    if danh_muc_id:
        query = query.filter(SanPham.danh_muc_id == danh_muc_id)
    
    if nha_cung_cap_id:
        query = query.filter(SanPham.nha_cung_cap_id == nha_cung_cap_id)
    
    if trang_thai is not None:
        query = query.filter(SanPham.trang_thai == (trang_thai == 'true'))
    
    # Áp dụng sắp xếp
    if sort_by == 'ten':
        query = query.order_by(SanPham.ten.asc() if sort_dir == 'asc' else SanPham.ten.desc())
    elif sort_by == 'gia':
        query = query.order_by(SanPham.gia_ban.asc() if sort_dir == 'asc' else SanPham.gia_ban.desc())
    elif sort_by == 'so_luong':
        query = query.order_by(SanPham.so_luong_ton.asc() if sort_dir == 'asc' else SanPham.so_luong_ton.desc())
    else:
        query = query.order_by(SanPham.id.asc() if sort_dir == 'asc' else SanPham.id.desc())
    
    # Lấy danh sách sản phẩm phân trang
    san_pham_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Lấy danh sách danh mục và nhà cung cấp để hiển thị trong bộ lọc
    danh_muc_list = DanhMuc.query.all()
    nha_cung_cap_list = NhaCungCap.query.all()
    
    return render_template(
        'san_pham/index.html',
        san_pham_list=san_pham_pagination.items,
        pagination=san_pham_pagination,
        danh_muc_list=danh_muc_list,
        nha_cung_cap_list=nha_cung_cap_list,
        search=search,
        danh_muc_id=danh_muc_id,
        nha_cung_cap_id=nha_cung_cap_id,
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
        ma_vach = request.form.get('ma_vach')
        mo_ta = request.form.get('mo_ta')
        thong_so_ky_thuat = request.form.get('thong_so_ky_thuat')
        don_vi_tinh = request.form.get('don_vi_tinh')
        gia_nhap = request.form.get('gia_nhap', type=float)
        gia_ban = request.form.get('gia_ban', type=float)
        so_luong_toi_thieu = request.form.get('so_luong_toi_thieu', type=int)
        danh_muc_id = request.form.get('danh_muc_id', type=int)
        nha_cung_cap_id = request.form.get('nha_cung_cap_id', type=int)
        hinh_anh = request.form.get('hinh_anh')
        
        # Kiểm tra dữ liệu đầu vào
        if not ten:
            flash('Vui lòng nhập tên sản phẩm!', 'danger')
            danh_muc_list = DanhMuc.query.all()
            nha_cung_cap_list = NhaCungCap.query.all()
            return render_template('san_pham/them.html', danh_muc_list=danh_muc_list, nha_cung_cap_list=nha_cung_cap_list)
        
        # Kiểm tra mã vạch đã tồn tại chưa (nếu có)
        if ma_vach:
            existing_product = SanPham.query.filter_by(ma_vach=ma_vach).first()
            if existing_product:
                flash('Mã vạch đã tồn tại trong hệ thống!', 'danger')
                danh_muc_list = DanhMuc.query.all()
                nha_cung_cap_list = NhaCungCap.query.all()
                return render_template('san_pham/them.html', danh_muc_list=danh_muc_list, nha_cung_cap_list=nha_cung_cap_list)
        
        # Xử lý hình ảnh nếu có
        processed_image = None
        if hinh_anh:
            processed_image = process_base64_image(hinh_anh)
        
        # Tạo sản phẩm mới
        new_product = SanPham(
            ten=ten,
            ma_vach=ma_vach,
            mo_ta=mo_ta,
            thong_so_ky_thuat=thong_so_ky_thuat,
            don_vi_tinh=don_vi_tinh,
            gia_nhap=gia_nhap or 0,
            gia_ban=gia_ban or 0,
            so_luong_toi_thieu=so_luong_toi_thieu or 10,
            danh_muc_id=danh_muc_id,
            nha_cung_cap_id=nha_cung_cap_id,
            hinh_anh=processed_image,
            trang_thai=True,
            ngay_tao=datetime.now()
        )
        
        # Lưu vào cơ sở dữ liệu
        try:
            db.session.add(new_product)
            db.session.commit()
            flash('Thêm sản phẩm thành công!', 'success')
            return redirect(url_for('san_pham.index'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Lỗi khi thêm sản phẩm: {str(e)}")
            flash('Đã xảy ra lỗi, vui lòng thử lại sau!', 'danger')
    
    # Lấy danh sách danh mục và nhà cung cấp để hiển thị trong form
    danh_muc_list = DanhMuc.query.all()
    nha_cung_cap_list = NhaCungCap.query.all()
    
    return render_template('san_pham/them.html', danh_muc_list=danh_muc_list, nha_cung_cap_list=nha_cung_cap_list)

@bp.route('/sua/<int:id>', methods=['GET', 'POST'])
@login_required
def sua(id):
    # Lấy thông tin sản phẩm
    san_pham = SanPham.query.get_or_404(id)
    
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        ten = request.form.get('ten')
        ma_vach = request.form.get('ma_vach')
        mo_ta = request.form.get('mo_ta')
        thong_so_ky_thuat = request.form.get('thong_so_ky_thuat')
        don_vi_tinh = request.form.get('don_vi_tinh')
        gia_nhap = request.form.get('gia_nhap', type=float)
        gia_ban = request.form.get('gia_ban', type=float)
        so_luong_toi_thieu = request.form.get('so_luong_toi_thieu', type=int)
        danh_muc_id = request.form.get('danh_muc_id', type=int)
        nha_cung_cap_id = request.form.get('nha_cung_cap_id', type=int)
        hinh_anh = request.form.get('hinh_anh')
        trang_thai = request.form.get('trang_thai') == 'on'
        
        # Kiểm tra dữ liệu đầu vào
        if not ten:
            flash('Vui lòng nhập tên sản phẩm!', 'danger')
            danh_muc_list = DanhMuc.query.all()
            nha_cung_cap_list = NhaCungCap.query.all()
            return render_template('san_pham/sua.html', 
                                 san_pham=san_pham, 
                                 danh_muc_list=danh_muc_list, 
                                 nha_cung_cap_list=nha_cung_cap_list)
        
        # Kiểm tra mã vạch đã tồn tại chưa (nếu có và khác mã vạch hiện tại)
        if ma_vach and ma_vach != san_pham.ma_vach:
            existing_product = SanPham.query.filter_by(ma_vach=ma_vach).first()
            if existing_product:
                flash('Mã vạch đã tồn tại trong hệ thống!', 'danger')
                danh_muc_list = DanhMuc.query.all()
                nha_cung_cap_list = NhaCungCap.query.all()
                return render_template('san_pham/sua.html', 
                                     san_pham=san_pham, 
                                     danh_muc_list=danh_muc_list, 
                                     nha_cung_cap_list=nha_cung_cap_list)
        
        # Xử lý hình ảnh nếu có
        if hinh_anh and hinh_anh != san_pham.hinh_anh:
            processed_image = process_base64_image(hinh_anh)
            san_pham.hinh_anh = processed_image
        
        # Cập nhật thông tin sản phẩm
        san_pham.ten = ten
        san_pham.ma_vach = ma_vach
        san_pham.mo_ta = mo_ta
        san_pham.thong_so_ky_thuat = thong_so_ky_thuat
        san_pham.don_vi_tinh = don_vi_tinh
        san_pham.gia_nhap = gia_nhap or 0
        san_pham.gia_ban = gia_ban or 0
        san_pham.so_luong_toi_thieu = so_luong_toi_thieu or 10
        san_pham.danh_muc_id = danh_muc_id
        san_pham.nha_cung_cap_id = nha_cung_cap_id
        san_pham.trang_thai = trang_thai
        
        # Lưu vào cơ sở dữ liệu
        try:
            db.session.commit()
            flash('Cập nhật sản phẩm thành công!', 'success')
            return redirect(url_for('san_pham.index'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Lỗi khi cập nhật sản phẩm: {str(e)}")
            flash('Đã xảy ra lỗi, vui lòng thử lại sau!', 'danger')
    
    # Lấy danh sách danh mục và nhà cung cấp để hiển thị trong form
    danh_muc_list = DanhMuc.query.all()
    nha_cung_cap_list = NhaCungCap.query.all()
    
    return render_template('san_pham/sua.html', 
                         san_pham=san_pham, 
                         danh_muc_list=danh_muc_list, 
                         nha_cung_cap_list=nha_cung_cap_list)

@bp.route('/chi-tiet/<int:id>')
@login_required
def chi_tiet(id):
    # Lấy thông tin sản phẩm
    san_pham = SanPham.query.get_or_404(id)
    return render_template('san_pham/chi_tiet.html', san_pham=san_pham)

@bp.route('/xoa/<int:id>', methods=['POST'])
@login_required
def xoa(id):
    # Lấy thông tin sản phẩm
    san_pham = SanPham.query.get_or_404(id)
    
    try:
        # Thay vì xóa, chỉ thay đổi trạng thái
        san_pham.trang_thai = False
        db.session.commit()
        flash('Đã vô hiệu hóa sản phẩm thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Lỗi khi vô hiệu hóa sản phẩm: {str(e)}")
        flash('Đã xảy ra lỗi, vui lòng thử lại sau!', 'danger')
    
    return redirect(url_for('san_pham.index'))

@bp.route('/scan-barcode', methods=['POST'])
@login_required
def scan_barcode():
    # Lấy dữ liệu hình ảnh từ request
    image_data = request.form.get('image')
    
    if not image_data:
        return jsonify({'success': False, 'message': 'Không có dữ liệu hình ảnh!'})
    
    # Quét mã vạch từ hình ảnh
    try:
        barcode_results = scan_barcode_from_base64(image_data)
        
        if not barcode_results:
            return jsonify({'success': False, 'message': 'Không tìm thấy mã vạch trong hình ảnh!'})
        
        return jsonify({
            'success': True, 
            'data': barcode_results[0]['data'],
            'type': barcode_results[0]['type']
        })
    except Exception as e:
        logging.error(f"Lỗi khi quét mã vạch: {str(e)}")
        return jsonify({'success': False, 'message': 'Lỗi khi xử lý mã vạch!'})

@bp.route('/kiem-tra-ton-kho')
@login_required
def kiem_tra_ton_kho():
    # Lấy danh sách sản phẩm có số lượng tồn dưới mức tối thiểu
    san_pham_can_nhap = SanPham.query.filter(
        SanPham.so_luong_ton < SanPham.so_luong_toi_thieu,
        SanPham.trang_thai == True
    ).all()
    
    return render_template('san_pham/kiem_tra_ton_kho.html', san_pham_list=san_pham_can_nhap)
