from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import PhieuXuat, ChiTietXuat, SanPham
from utils import generate_reference_number, export_to_excel, export_to_pdf, format_currency
import json
import logging
from datetime import datetime
from io import BytesIO

bp = Blueprint('xuat_kho', __name__, url_prefix='/xuat-kho')

@bp.route('/')
@login_required
def index():
    # Lấy thông tin tìm kiếm từ query params
    search = request.args.get('search', '')
    nguoi_nhan = request.args.get('nguoi_nhan', '')
    bo_phan = request.args.get('bo_phan', '')
    trang_thai = request.args.get('trang_thai')
    tu_ngay = request.args.get('tu_ngay')
    den_ngay = request.args.get('den_ngay')
    
    # Lấy thông tin sắp xếp
    sort_by = request.args.get('sort_by', 'ngay_xuat')
    sort_dir = request.args.get('sort_dir', 'desc')
    
    # Lấy thông tin phân trang
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Khởi tạo query
    query = PhieuXuat.query
    
    # Áp dụng bộ lọc tìm kiếm
    if search:
        query = query.filter(PhieuXuat.ma_phieu.ilike(f'%{search}%'))
    
    if nguoi_nhan:
        query = query.filter(PhieuXuat.nguoi_nhan.ilike(f'%{nguoi_nhan}%'))
    
    if bo_phan:
        query = query.filter(PhieuXuat.bo_phan.ilike(f'%{bo_phan}%'))
    
    if trang_thai:
        query = query.filter(PhieuXuat.trang_thai == trang_thai)
    
    if tu_ngay:
        try:
            tu_ngay_dt = datetime.strptime(tu_ngay, '%Y-%m-%d')
            query = query.filter(PhieuXuat.ngay_xuat >= tu_ngay_dt)
        except:
            pass
    
    if den_ngay:
        try:
            den_ngay_dt = datetime.strptime(den_ngay, '%Y-%m-%d')
            den_ngay_dt = datetime.combine(den_ngay_dt.date(), datetime.max.time())
            query = query.filter(PhieuXuat.ngay_xuat <= den_ngay_dt)
        except:
            pass
    
    # Áp dụng sắp xếp
    if sort_by == 'ma_phieu':
        query = query.order_by(PhieuXuat.ma_phieu.asc() if sort_dir == 'asc' else PhieuXuat.ma_phieu.desc())
    elif sort_by == 'tong_tien':
        query = query.order_by(PhieuXuat.tong_tien.asc() if sort_dir == 'asc' else PhieuXuat.tong_tien.desc())
    else:  # ngay_xuat
        query = query.order_by(PhieuXuat.ngay_xuat.asc() if sort_dir == 'asc' else PhieuXuat.ngay_xuat.desc())
    
    # Lấy danh sách phiếu xuất phân trang
    phieu_xuat_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template(
        'xuat_kho/index.html',
        phieu_xuat_list=phieu_xuat_pagination.items,
        pagination=phieu_xuat_pagination,
        search=search,
        nguoi_nhan=nguoi_nhan,
        bo_phan=bo_phan,
        trang_thai=trang_thai,
        tu_ngay=tu_ngay,
        den_ngay=den_ngay,
        sort_by=sort_by,
        sort_dir=sort_dir
    )

@bp.route('/them', methods=['GET', 'POST'])
@login_required
def them():
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        nguoi_nhan = request.form.get('nguoi_nhan')
        bo_phan = request.form.get('bo_phan')
        ngay_xuat = request.form.get('ngay_xuat')
        ghi_chu = request.form.get('ghi_chu')
        chi_tiet_json = request.form.get('chi_tiet')
        
        # Kiểm tra dữ liệu nhập
        if not chi_tiet_json:
            flash('Vui lòng thêm ít nhất một sản phẩm vào phiếu xuất!', 'danger')
            return render_template('xuat_kho/them.html')
        
        # Chuyển đổi chuỗi JSON thành đối tượng Python
        try:
            chi_tiet_list = json.loads(chi_tiet_json)
        except:
            flash('Dữ liệu chi tiết phiếu xuất không hợp lệ!', 'danger')
            return render_template('xuat_kho/them.html')
        
        # Kiểm tra thông tin người nhận
        if not nguoi_nhan:
            flash('Vui lòng nhập thông tin người nhận!', 'danger')
            return render_template('xuat_kho/them.html')
        
        # Kiểm tra ngày xuất
        try:
            if ngay_xuat:
                ngay_xuat_dt = datetime.strptime(ngay_xuat, '%Y-%m-%d')
            else:
                ngay_xuat_dt = datetime.now()
        except:
            ngay_xuat_dt = datetime.now()
        
        # Tạo mã phiếu xuất tự động
        ma_phieu = generate_reference_number('XK', PhieuXuat)
        
        # Tính tổng tiền
        tong_tien = sum(item.get('thanh_tien', 0) for item in chi_tiet_list)
        
        # Tạo phiếu xuất mới
        phieu_xuat = PhieuXuat(
            ma_phieu=ma_phieu,
            ngay_xuat=ngay_xuat_dt,
            nguoi_dung_id=current_user.id,
            nguoi_nhan=nguoi_nhan,
            bo_phan=bo_phan,
            tong_tien=tong_tien,
            ghi_chu=ghi_chu,
            trang_thai='da_xuat',
            ngay_tao=datetime.now()
        )
        
        try:
            # Kiểm tra số lượng tồn trước khi xuất
            du_so_luong = True
            thieu_san_pham = []
            
            for item in chi_tiet_list:
                san_pham_id = item.get('san_pham_id')
                so_luong = item.get('so_luong', 0)
                
                # Kiểm tra sản phẩm tồn tại
                san_pham = SanPham.query.get(san_pham_id)
                if not san_pham:
                    continue
                
                # Kiểm tra số lượng tồn
                if san_pham.so_luong_ton < so_luong:
                    du_so_luong = False
                    thieu_san_pham.append(f"{san_pham.ten} (hiện có {san_pham.so_luong_ton}, cần {so_luong})")
            
            if not du_so_luong:
                flash(f'Không đủ số lượng tồn kho: {", ".join(thieu_san_pham)}', 'danger')
                return render_template('xuat_kho/them.html')
            
            # Thêm phiếu xuất vào cơ sở dữ liệu
            db.session.add(phieu_xuat)
            db.session.flush()  # Lấy ID của phiếu xuất mới
            
            # Thêm chi tiết phiếu xuất
            for item in chi_tiet_list:
                san_pham_id = item.get('san_pham_id')
                so_luong = item.get('so_luong', 0)
                don_gia = item.get('don_gia', 0)
                thanh_tien = item.get('thanh_tien', 0)
                
                # Kiểm tra sản phẩm tồn tại
                san_pham = SanPham.query.get(san_pham_id)
                if not san_pham:
                    continue
                
                # Tạo chi tiết phiếu xuất
                chi_tiet = ChiTietXuat(
                    phieu_xuat_id=phieu_xuat.id,
                    san_pham_id=san_pham_id,
                    so_luong=so_luong,
                    don_gia=don_gia,
                    thanh_tien=thanh_tien
                )
                db.session.add(chi_tiet)
                
                # Cập nhật số lượng tồn của sản phẩm
                san_pham.so_luong_ton -= so_luong
            
            # Lưu tất cả thay đổi vào cơ sở dữ liệu
            db.session.commit()
            flash('Tạo phiếu xuất kho thành công!', 'success')
            return redirect(url_for('xuat_kho.chi_tiet', id=phieu_xuat.id))
        
        except Exception as e:
            db.session.rollback()
            logging.error(f"Lỗi khi tạo phiếu xuất: {str(e)}")
            flash('Đã xảy ra lỗi, vui lòng thử lại sau!', 'danger')
    
    return render_template('xuat_kho/them.html')

@bp.route('/chi-tiet/<int:id>')
@login_required
def chi_tiet(id):
    # Lấy thông tin phiếu xuất
    phieu_xuat = PhieuXuat.query.get_or_404(id)
    
    # Lấy chi tiết phiếu xuất
    chi_tiet_list = ChiTietXuat.query.filter_by(phieu_xuat_id=id).all()
    
    return render_template('xuat_kho/chi_tiet.html', phieu_xuat=phieu_xuat, chi_tiet_list=chi_tiet_list)

@bp.route('/huy/<int:id>', methods=['POST'])
@login_required
def huy(id):
    # Lấy thông tin phiếu xuất
    phieu_xuat = PhieuXuat.query.get_or_404(id)
    
    # Kiểm tra trạng thái phiếu
    if phieu_xuat.trang_thai == 'da_xuat':
        # Lấy chi tiết phiếu xuất
        chi_tiet_list = ChiTietXuat.query.filter_by(phieu_xuat_id=id).all()
        
        try:
            # Cập nhật số lượng tồn kho
            for chi_tiet in chi_tiet_list:
                san_pham = SanPham.query.get(chi_tiet.san_pham_id)
                if san_pham:
                    san_pham.so_luong_ton += chi_tiet.so_luong
            
            # Cập nhật trạng thái phiếu
            phieu_xuat.trang_thai = 'huy_bo'
            
            # Lưu thay đổi
            db.session.commit()
            flash('Đã hủy phiếu xuất kho thành công!', 'success')
        except Exception as e:
            db.session.rollback()
            logging.error(f"Lỗi khi hủy phiếu xuất: {str(e)}")
            flash('Đã xảy ra lỗi, vui lòng thử lại sau!', 'danger')
    else:
        flash('Không thể hủy phiếu xuất này!', 'warning')
    
    return redirect(url_for('xuat_kho.chi_tiet', id=id))

@bp.route('/get-san-pham')
@login_required
def get_san_pham():
    # Lấy tất cả sản phẩm đang hoạt động và có số lượng tồn > 0
    san_pham_list = SanPham.query.filter(SanPham.trang_thai==True, SanPham.so_luong_ton>0).all()
    
    result = []
    for sp in san_pham_list:
        result.append({
            'id': sp.id,
            'ten': sp.ten,
            'ma_vach': sp.ma_vach or '',
            'don_vi_tinh': sp.don_vi_tinh or '',
            'gia_ban': sp.gia_ban,
            'so_luong_ton': sp.so_luong_ton
        })
    
    return jsonify(result)

@bp.route('/get-san-pham-by-barcode')
@login_required
def get_san_pham_by_barcode():
    # Lấy mã vạch từ query params
    ma_vach = request.args.get('ma_vach', '')
    
    if not ma_vach:
        return jsonify({'success': False, 'message': 'Không có mã vạch!'})
    
    # Tìm sản phẩm theo mã vạch
    san_pham = SanPham.query.filter_by(ma_vach=ma_vach, trang_thai=True).first()
    
    if not san_pham:
        return jsonify({'success': False, 'message': 'Không tìm thấy sản phẩm với mã vạch này!'})
    
    if san_pham.so_luong_ton <= 0:
        return jsonify({'success': False, 'message': 'Sản phẩm này đã hết hàng!'})
    
    return jsonify({
        'success': True,
        'san_pham': {
            'id': san_pham.id,
            'ten': san_pham.ten,
            'ma_vach': san_pham.ma_vach or '',
            'don_vi_tinh': san_pham.don_vi_tinh or '',
            'gia_ban': san_pham.gia_ban,
            'so_luong_ton': san_pham.so_luong_ton
        }
    })

@bp.route('/xuat-excel/<int:id>')
@login_required
def xuat_excel(id):
    # Lấy thông tin phiếu xuất
    phieu_xuat = PhieuXuat.query.get_or_404(id)
    
    # Lấy chi tiết phiếu xuất
    chi_tiet_list = ChiTietXuat.query.filter_by(phieu_xuat_id=id).all()
    
    # Chuẩn bị dữ liệu
    headers = ['STT', 'Mã SP', 'Tên sản phẩm', 'Đơn vị tính', 'Số lượng', 'Đơn giá', 'Thành tiền']
    data = []
    
    for i, chi_tiet in enumerate(chi_tiet_list):
        san_pham = SanPham.query.get(chi_tiet.san_pham_id)
        if san_pham:
            data.append([
                i + 1,
                san_pham.ma_vach or '',
                san_pham.ten,
                san_pham.don_vi_tinh or '',
                chi_tiet.so_luong,
                format_currency(chi_tiet.don_gia),
                format_currency(chi_tiet.thanh_tien)
            ])
    
    # Xuất file Excel
    output = export_to_excel(
        data, 
        headers, 
        f'phieu_xuat_{phieu_xuat.ma_phieu}.xlsx', 
        f'Phiếu xuất {phieu_xuat.ma_phieu}'
    )
    
    # Trả về file Excel
    from flask import send_file
    return send_file(
        output,
        as_attachment=True,
        download_name=f'phieu_xuat_{phieu_xuat.ma_phieu}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@bp.route('/xuat-pdf/<int:id>')
@login_required
def xuat_pdf(id):
    # Lấy thông tin phiếu xuất
    phieu_xuat = PhieuXuat.query.get_or_404(id)
    
    # Lấy chi tiết phiếu xuất
    chi_tiet_list = ChiTietXuat.query.filter_by(phieu_xuat_id=id).all()
    
    # Chuẩn bị dữ liệu
    headers = ['STT', 'Mã SP', 'Tên sản phẩm', 'ĐVT', 'SL', 'Đơn giá', 'Thành tiền']
    data = []
    
    for i, chi_tiet in enumerate(chi_tiet_list):
        san_pham = SanPham.query.get(chi_tiet.san_pham_id)
        if san_pham:
            data.append([
                i + 1,
                san_pham.ma_vach or '',
                san_pham.ten,
                san_pham.don_vi_tinh or '',
                chi_tiet.so_luong,
                format_currency(chi_tiet.don_gia),
                format_currency(chi_tiet.thanh_tien)
            ])
    
    # Tiêu đề phiếu
    title = f"PHIẾU XUẤT KHO\nSố: {phieu_xuat.ma_phieu}"
    
    # Xuất file PDF
    output = export_to_pdf(
        data, 
        headers, 
        title, 
        f'phieu_xuat_{phieu_xuat.ma_phieu}.pdf'
    )
    
    # Trả về file PDF
    from flask import send_file
    return send_file(
        output,
        as_attachment=True,
        download_name=f'phieu_xuat_{phieu_xuat.ma_phieu}.pdf',
        mimetype='application/pdf'
    )
