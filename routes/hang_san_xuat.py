from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from models import HangSanXuat
from datetime import datetime

hang_san_xuat_bp = Blueprint('hang_san_xuat', __name__)

@hang_san_xuat_bp.route('/hang-san-xuat')
@login_required
def index():
    hangs = HangSanXuat.query.all()
    return render_template('hang_san_xuat/index.html', hangs=hangs)

@hang_san_xuat_bp.route('/hang-san-xuat/them', methods=['GET', 'POST'])
@login_required
def them():
    if request.method == 'POST':
        ten = request.form.get('ten')
        quoc_gia = request.form.get('quoc_gia')
        website = request.form.get('website')
        mo_ta = request.form.get('mo_ta')
        
        if not ten:
            flash('Tên hãng sản xuất không được để trống', 'danger')
            return redirect(url_for('hang_san_xuat.them'))
        
        hang = HangSanXuat(
            ten=ten,
            quoc_gia=quoc_gia,
            website=website,
            mo_ta=mo_ta
        )
        
        db.session.add(hang)
        db.session.commit()
        flash('Thêm hãng sản xuất thành công', 'success')
        return redirect(url_for('hang_san_xuat.index'))
    
    return render_template('hang_san_xuat/them.html')

@hang_san_xuat_bp.route('/hang-san-xuat/sua/<int:id>', methods=['GET', 'POST'])
@login_required
def sua(id):
    hang = HangSanXuat.query.get_or_404(id)
    
    if request.method == 'POST':
        ten = request.form.get('ten')
        quoc_gia = request.form.get('quoc_gia')
        website = request.form.get('website')
        mo_ta = request.form.get('mo_ta')
        
        if not ten:
            flash('Tên hãng sản xuất không được để trống', 'danger')
            return redirect(url_for('hang_san_xuat.sua', id=id))
        
        hang.ten = ten
        hang.quoc_gia = quoc_gia
        hang.website = website
        hang.mo_ta = mo_ta
        
        db.session.commit()
        flash('Cập nhật hãng sản xuất thành công', 'success')
        return redirect(url_for('hang_san_xuat.index'))
    
    return render_template('hang_san_xuat/sua.html', hang=hang)

@hang_san_xuat_bp.route('/hang-san-xuat/xoa/<int:id>')
@login_required
def xoa(id):
    hang = HangSanXuat.query.get_or_404(id)
    
    try:
        db.session.delete(hang)
        db.session.commit()
        flash('Xóa hãng sản xuất thành công', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Không thể xóa hãng sản xuất này vì đã có sản phẩm liên kết', 'danger')
    
    return redirect(url_for('hang_san_xuat.index'))
