from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from models import db, SanPham, DanhMuc, PhieuNhap, PhieuXuat, ChiTietNhap, ChiTietXuat

bp = Blueprint('bao_cao', __name__, url_prefix='/bao-cao')

@bp.route('/')
@login_required
def index():
    """Trang báo cáo tổng quan"""
    return render_template('bao_cao/index.html')

@bp.route('/ton-kho')
@login_required
def ton_kho():
    """Báo cáo tồn kho"""
    danh_muc_list = DanhMuc.query.all()
    
    # Lấy sản phẩm có số lượng dưới mức tối thiểu
    san_pham_canh_bao = SanPham.query.filter(SanPham.so_luong_ton < SanPham.so_luong_toi_thieu).all()
    
    return render_template('bao_cao/ton_kho.html', 
                          danh_muc_list=danh_muc_list,
                          san_pham_canh_bao=san_pham_canh_bao)

@bp.route('/nhap-xuat')
@login_required
def nhap_xuat():
    """Báo cáo nhập xuất kho"""
    # Lấy ngày bắt đầu và kết thúc từ tham số truy vấn
    ngay_bat_dau = request.args.get('ngay_bat_dau', 
                                   (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    ngay_ket_thuc = request.args.get('ngay_ket_thuc', 
                                    datetime.now().strftime('%Y-%m-%d'))
    
    # Chuyển đổi chuỗi sang datetime
    date_format = '%Y-%m-%d'
    ngay_bat_dau = datetime.strptime(ngay_bat_dau, date_format)
    ngay_ket_thuc = datetime.strptime(ngay_ket_thuc, date_format)
    ngay_ket_thuc = ngay_ket_thuc.replace(hour=23, minute=59, second=59)
    
    # Lấy tổng số phiếu nhập và giá trị
    tong_nhap = db.session.query(
        func.count(PhieuNhap.id).label('so_phieu'),
        func.sum(PhieuNhap.tong_tien).label('tong_tien')
    ).filter(
        PhieuNhap.ngay_nhap.between(ngay_bat_dau, ngay_ket_thuc),
        PhieuNhap.trang_thai == 'da_nhap'
    ).first()
    
    # Lấy tổng số phiếu xuất và giá trị
    tong_xuat = db.session.query(
        func.count(PhieuXuat.id).label('so_phieu'),
        func.sum(PhieuXuat.tong_tien).label('tong_tien')
    ).filter(
        PhieuXuat.ngay_xuat.between(ngay_bat_dau, ngay_ket_thuc),
        PhieuXuat.trang_thai == 'da_xuat'
    ).first()
    
    # Các sản phẩm nhập nhiều nhất
    san_pham_nhap_nhieu = db.session.query(
        SanPham.id,
        SanPham.ma_vach,
        SanPham.ten,
        func.sum(ChiTietNhap.so_luong).label('tong_so_luong'),
        func.sum(ChiTietNhap.thanh_tien).label('tong_tien')
    ).join(
        ChiTietNhap, SanPham.id == ChiTietNhap.san_pham_id
    ).join(
        PhieuNhap, ChiTietNhap.phieu_nhap_id == PhieuNhap.id
    ).filter(
        PhieuNhap.ngay_nhap.between(ngay_bat_dau, ngay_ket_thuc),
        PhieuNhap.trang_thai == 'da_nhap'
    ).group_by(
        SanPham.id, SanPham.ma_vach, SanPham.ten
    ).order_by(
        desc('tong_so_luong')
    ).limit(10).all()
    
    # Các sản phẩm xuất nhiều nhất
    san_pham_xuat_nhieu = db.session.query(
        SanPham.id,
        SanPham.ma_vach,
        SanPham.ten,
        func.sum(ChiTietXuat.so_luong).label('tong_so_luong'),
        func.sum(ChiTietXuat.thanh_tien).label('tong_tien')
    ).join(
        ChiTietXuat, SanPham.id == ChiTietXuat.san_pham_id
    ).join(
        PhieuXuat, ChiTietXuat.phieu_xuat_id == PhieuXuat.id
    ).filter(
        PhieuXuat.ngay_xuat.between(ngay_bat_dau, ngay_ket_thuc),
        PhieuXuat.trang_thai == 'da_xuat'
    ).group_by(
        SanPham.id, SanPham.ma_vach, SanPham.ten
    ).order_by(
        desc('tong_so_luong')
    ).limit(10).all()
    
    return render_template('bao_cao/nhap_xuat.html',
                          ngay_bat_dau=ngay_bat_dau.strftime(date_format),
                          ngay_ket_thuc=ngay_ket_thuc.strftime(date_format),
                          tong_nhap=tong_nhap,
                          tong_xuat=tong_xuat,
                          san_pham_nhap_nhieu=san_pham_nhap_nhieu,
                          san_pham_xuat_nhieu=san_pham_xuat_nhieu)

@bp.route('/api/du-lieu-bieu-do')
@login_required
def du_lieu_bieu_do():
    """API trả về dữ liệu cho biểu đồ"""
    loai_bieu_do = request.args.get('loai', 'nhap-xuat')
    
    if loai_bieu_do == 'nhap-xuat':
        # Dữ liệu nhập xuất 30 ngày gần nhất
        ngay_bat_dau = datetime.now() - timedelta(days=30)
        
        # Dữ liệu nhập kho theo ngày
        du_lieu_nhap = db.session.query(
            func.date(PhieuNhap.ngay_nhap).label('ngay'),
            func.sum(PhieuNhap.tong_tien).label('tong_tien')
        ).filter(
            PhieuNhap.ngay_nhap >= ngay_bat_dau,
            PhieuNhap.trang_thai == 'da_nhap'
        ).group_by(
            func.date(PhieuNhap.ngay_nhap)
        ).all()
        
        # Dữ liệu xuất kho theo ngày
        du_lieu_xuat = db.session.query(
            func.date(PhieuXuat.ngay_xuat).label('ngay'),
            func.sum(PhieuXuat.tong_tien).label('tong_tien')
        ).filter(
            PhieuXuat.ngay_xuat >= ngay_bat_dau,
            PhieuXuat.trang_thai == 'da_xuat'
        ).group_by(
            func.date(PhieuXuat.ngay_xuat)
        ).all()
        
        # Chuyển đổi dữ liệu sang định dạng phù hợp cho biểu đồ
        ngay_list = []
        nhap_list = []
        xuat_list = []
        
        # Tạo danh sách ngày trong 30 ngày gần nhất
        for i in range(30, -1, -1):
            ngay = datetime.now() - timedelta(days=i)
            ngay_str = ngay.strftime('%d/%m')
            ngay_list.append(ngay_str)
            
            # Tìm dữ liệu nhập cho ngày này
            nhap_value = 0
            for item in du_lieu_nhap:
                if item.ngay.strftime('%Y-%m-%d') == ngay.strftime('%Y-%m-%d'):
                    nhap_value = float(item.tong_tien or 0)
                    break
            nhap_list.append(nhap_value)
            
            # Tìm dữ liệu xuất cho ngày này
            xuat_value = 0
            for item in du_lieu_xuat:
                if item.ngay.strftime('%Y-%m-%d') == ngay.strftime('%Y-%m-%d'):
                    xuat_value = float(item.tong_tien or 0)
                    break
            xuat_list.append(xuat_value)
        
        return jsonify({
            'labels': ngay_list,
            'datasets': [
                {
                    'label': 'Nhập kho',
                    'data': nhap_list,
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Xuất kho',
                    'data': xuat_list,
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 1
                }
            ]
        })
    
    elif loai_bieu_do == 'ton-kho':
        # Dữ liệu tồn kho theo danh mục
        du_lieu_danh_muc = db.session.query(
            DanhMuc.ten.label('ten_danh_muc'),
            func.sum(SanPham.so_luong_ton).label('tong_so_luong'),
            func.sum(SanPham.so_luong_ton * SanPham.gia_nhap).label('tong_gia_tri')
        ).join(
            SanPham, DanhMuc.id == SanPham.danh_muc_id
        ).group_by(
            DanhMuc.ten
        ).all()
        
        ten_danh_muc = [item.ten_danh_muc for item in du_lieu_danh_muc]
        so_luong = [int(item.tong_so_luong or 0) for item in du_lieu_danh_muc]
        gia_tri = [float(item.tong_gia_tri or 0) for item in du_lieu_danh_muc]
        
        return jsonify({
            'labels': ten_danh_muc,
            'datasets': [
                {
                    'type': 'bar',
                    'label': 'Số lượng',
                    'data': so_luong,
                    'backgroundColor': 'rgba(54, 162, 235, 0.5)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'borderWidth': 1,
                    'yAxisID': 'y'
                },
                {
                    'type': 'line',
                    'label': 'Giá trị',
                    'data': gia_tri,
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 2,
                    'yAxisID': 'y1'
                }
            ]
        })
    
    return jsonify({'error': 'Loại biểu đồ không hợp lệ'})