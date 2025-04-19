from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import PhieuNhap, ChiTietNhap, SanPham, NhaCungCap
from utils import generate_reference_number, export_to_excel, export_to_pdf, format_currency
import json
import logging
from datetime import datetime
from io import BytesIO

bp = Blueprint('nhap_kho', __name__, url_prefix='/nhap-kho')

@bp.route('/')
@login_required
def index():
    # Lấy thông tin tìm kiếm từ query params
    search = request.args.get('search', '')
    nha_cung_cap_id = request.args.get('nha_cung_cap_id', type=int)
    trang_thai = request.args.get('trang_thai')
    tu_ngay = request.args.get('tu_ngay')
    den_ngay = request.args.get('den_ngay')
    
    # Lấy thông tin sắp xếp
    sort_by = request.args.get('sort_by', 'ngay_nhap')
    sort_dir = request.args.get('sort_dir', 'desc')
    
    # Lấy thông tin phân trang
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Khởi tạo query
    query = PhieuNhap.query
    
    # Áp dụng bộ lọc tìm kiếm
    if search:
        query = query.filter(PhieuNhap.ma_phieu.ilike(f'%{search}%'))
    
    if nha_cung_cap_id:
        query = query.filter(PhieuNhap.nha_cung_cap_id == nha_cung_cap_id)
    
    if trang_thai:
        query = query.filter(PhieuNhap.trang_thai == trang_thai)
    
    if tu_ngay:
        try:
            tu_ngay_dt = datetime.strptime(tu_ngay, '%Y-%m-%d')
            query = query.filter(PhieuNhap.ngay_nhap >= tu_ngay_dt)
        except:
            pass
    
    if den_ngay:
        try:
            den_ngay_dt = datetime.strptime(den_ngay, '%Y-%m-%d')
            den_ngay_dt = datetime.combine(den_ngay_dt.date(), datetime.max.time())
            query = query.filter(PhieuNhap.ngay_nhap <= den_ngay_dt)
        except:
            pass
    
    # Áp dụng sắp xếp
    if sort_by == 'ma_phieu':
        query = query.order_by(PhieuNhap.ma_phieu.asc() if sort_dir == 'asc' else PhieuNhap.ma_phieu.desc())
    elif sort_by == 'tong_tien':
        query = query.order_by(PhieuNhap.tong_tien.asc() if sort_dir == 'asc' else PhieuNhap.tong_tien.desc())
    else:  # ngay_nhap
        query = query.order_by(PhieuNhap.ngay_nhap.asc() if sort_dir == 'asc' else PhieuNhap.ngay_nhap.desc())
    
    # Lấy danh sách phiếu nhập phân trang
    phieu_nhap_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Lấy danh sách nhà cung cấp để hiển thị trong bộ lọc
    nha_cung_cap_list = NhaCungCap.query.all()
    
    return render_template(
        'nhap_kho/index.html',
        phieu_nhap_list=phieu_nhap_pagination.items,
        pagination=phieu_nhap_pagination,
        nha_cung_cap_list=nha_cung_cap_list,
        search=search,
        nha_cung_cap_id=nha_cung_cap_id,
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
        nha_cung_cap_id = request.form.get('nha_cung_cap_id', type=int)
        ngay_nhap = request.form.get('ngay_nhap')
        ghi_chu = request.form.get('ghi_chu')
        chi_tiet_json = request.form.get('chi_tiet')
        
        # Kiểm tra dữ liệu nhập
        if not chi_tiet_json:
            flash('Vui lòng thêm ít nhất một sản phẩm vào phiếu nhập!', 'danger')
            nha_cung_cap_list = NhaCungCap.query.all()
            return render_template('nhap_kho/them.html', nha_cung_cap_list=nha_cung_cap_list)
        
        # Chuyển đổi chuỗi JSON thành đối tượng Python
        try:
            chi_tiet_list = json.loads(chi_tiet_json)
        except:
            flash('Dữ liệu chi tiết phiếu nhập không hợp lệ!', 'danger')
            nha_cung_cap_list = NhaCungCap.query.all()
            return render_template('nhap_kho/them.html', nha_cung_cap_list=nha_cung_cap_list)
        
        # Kiểm tra ngày nhập
        try:
            if ngay_nhap:
                ngay_nhap_dt = datetime.strptime(ngay_nhap, '%Y-%m-%d')
            else:
                ngay_nhap_dt = datetime.now()
        except:
            ngay_nhap_dt = datetime.now()
        
        # Tạo mã phiếu nhập tự động
        ma_phieu = generate_reference_number('NK', PhieuNhap)
        
        # Tính tổng tiền
        tong_tien = sum(item.get('thanh_tien', 0) for item in chi_tiet_list)
        
        # Tạo phiếu nhập mới
        phieu_nhap = PhieuNhap(
            ma_phieu=ma_phieu,
            ngay_nhap=ngay_nhap_dt,
            nha_cung_cap_id=nha_cung_cap_id,
            nguoi_dung_id=current_user.id,
            tong_tien=tong_tien,
            ghi_chu=ghi_chu,
            trang_thai='da_nhap',
            ngay_tao=datetime.now()
        )
        
        try:
            # Thêm phiếu nhập vào cơ sở dữ liệu
            db.session.add(phieu_nhap)
            db.session.flush()  # Lấy ID của phiếu nhập mới
            
            # Thêm chi tiết phiếu nhập
            for item in chi_tiet_list:
                san_pham_id = item.get('san_pham_id')
                so_luong = item.get('so_luong', 0)
                don_gia = item.get('don_gia', 0)
                thanh_tien = item.get('thanh_tien', 0)
                
                # Kiểm tra sản phẩm tồn tại
                san_pham = SanPham.query.get(san_pham_id)
                if not san_pham:
                    continue
                
                # Tạo chi tiết phiếu nhập
                chi_tiet = ChiTietNhap(
                    phieu_nhap_id=phieu_nhap.id,
                    san_pham_id=san_pham_id,
                    so_luong=so_luong,
                    don_gia=don_gia,
                    thanh_tien=thanh_tien
                )
                db.session.add(chi_tiet)
                
                # Cập nhật số lượng tồn của sản phẩm
                san_pham.so_luong_ton += so_luong
                
                # Cập nhật giá nhập nếu có thay đổi
                if don_gia > 0:
                    san_pham.gia_nhap = don_gia
            
            # Lưu tất cả thay đổi vào cơ sở dữ liệu
            db.session.commit()
            flash('Tạo phiếu nhập kho thành công!', 'success')
            return redirect(url_for('nhap_kho.chi_tiet', id=phieu_nhap.id))
        
        except Exception as e:
            db.session.rollback()
            logging.error(f"Lỗi khi tạo phiếu nhập: {str(e)}")
            flash('Đã xảy ra lỗi, vui lòng thử lại sau!', 'danger')
    
    # Lấy danh sách nhà cung cấp
    nha_cung_cap_list = NhaCungCap.query.all()
    
    return render_template('nhap_kho/them.html', nha_cung_cap_list=nha_cung_cap_list)

@bp.route('/chi-tiet/<int:id>')
@login_required
def chi_tiet(id):
    # Lấy thông tin phiếu nhập
    phieu_nhap = PhieuNhap.query.get_or_404(id)
    
    # Lấy chi tiết phiếu nhập
    chi_tiet_list = ChiTietNhap.query.filter_by(phieu_nhap_id=id).all()
    
    return render_template('nhap_kho/chi_tiet.html', phieu_nhap=phieu_nhap, chi_tiet_list=chi_tiet_list)

@bp.route('/huy/<int:id>', methods=['POST'])
@login_required
def huy(id):
    # Lấy thông tin phiếu nhập
    phieu_nhap = PhieuNhap.query.get_or_404(id)
    
    # Kiểm tra trạng thái phiếu
    if phieu_nhap.trang_thai == 'da_nhap':
        # Lấy chi tiết phiếu nhập
        chi_tiet_list = ChiTietNhap.query.filter_by(phieu_nhap_id=id).all()
        
        try:
            # Cập nhật số lượng tồn kho
            for chi_tiet in chi_tiet_list:
                san_pham = SanPham.query.get(chi_tiet.san_pham_id)
                if san_pham:
                    san_pham.so_luong_ton -= chi_tiet.so_luong
                    if san_pham.so_luong_ton < 0:
                        san_pham.so_luong_ton = 0
            
            # Cập nhật trạng thái phiếu
            phieu_nhap.trang_thai = 'huy_bo'
            
            # Lưu thay đổi
            db.session.commit()
            flash('Đã hủy phiếu nhập kho thành công!', 'success')
        except Exception as e:
            db.session.rollback()
            logging.error(f"Lỗi khi hủy phiếu nhập: {str(e)}")
            flash('Đã xảy ra lỗi, vui lòng thử lại sau!', 'danger')
    else:
        flash('Không thể hủy phiếu nhập này!', 'warning')
    
    return redirect(url_for('nhap_kho.chi_tiet', id=id))

@bp.route('/get-san-pham')
@login_required
def get_san_pham():
    # Lấy tất cả sản phẩm đang hoạt động
    san_pham_list = SanPham.query.filter_by(trang_thai=True).all()
    
    result = []
    for sp in san_pham_list:
        result.append({
            'id': sp.id,
            'ten': sp.ten,
            'ma_vach': sp.ma_vach or '',
            'don_vi_tinh': sp.don_vi_tinh or '',
            'gia_nhap': sp.gia_nhap,
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
    
    return jsonify({
        'success': True,
        'san_pham': {
            'id': san_pham.id,
            'ten': san_pham.ten,
            'ma_vach': san_pham.ma_vach or '',
            'don_vi_tinh': san_pham.don_vi_tinh or '',
            'gia_nhap': san_pham.gia_nhap,
            'so_luong_ton': san_pham.so_luong_ton
        }
    })

@bp.route('/xuat-excel/<int:id>')
@login_required
def xuat_excel(id):
    # Lấy thông tin phiếu nhập
    phieu_nhap = PhieuNhap.query.get_or_404(id)
    
    # Lấy chi tiết phiếu nhập
    chi_tiet_list = ChiTietNhap.query.filter_by(phieu_nhap_id=id).all()
    
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
        f'phieu_nhap_{phieu_nhap.ma_phieu}.xlsx', 
        f'Phiếu nhập {phieu_nhap.ma_phieu}'
    )
    
    # Trả về file Excel
    from flask import send_file
    return send_file(
        output,
        as_attachment=True,
        download_name=f'phieu_nhap_{phieu_nhap.ma_phieu}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@bp.route('/xuat-pdf/<int:id>')
@login_required
def xuat_pdf(id):
    # Lấy thông tin phiếu nhập
    phieu_nhap = PhieuNhap.query.get_or_404(id)
    
    # Lấy chi tiết phiếu nhập
    chi_tiet_list = ChiTietNhap.query.filter_by(phieu_nhap_id=id).all()
    
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
    title = f"PHIẾU NHẬP KHO\nSố: {phieu_nhap.ma_phieu}"
    
    # Xuất file PDF
    output = export_to_pdf(
        data, 
        headers, 
        title, 
        f'phieu_nhap_{phieu_nhap.ma_phieu}.pdf'
    )
    
    # Trả về file PDF
    from flask import send_file
    return send_file(
        output,
        as_attachment=True,
        download_name=f'phieu_nhap_{phieu_nhap.ma_phieu}.pdf',
        mimetype='application/pdf'
    )
