# Quản lý Vật Tư Điện

Ứng dụng quản lý vật tư điện bằng tiếng Việt xây dựng trên nền tảng Flask với khả năng quét mã vạch, quản lý hình ảnh và xuất báo cáo.

## Tính năng chính

- Quản lý sản phẩm, danh mục, nhà cung cấp
- Quản lý nhập/xuất kho
- Quét mã vạch
- Báo cáo tồn kho, nhập xuất
- Xuất báo cáo ra Excel, PDF

## Hướng dẫn triển khai lên PythonAnywhere

Để triển khai ứng dụng lên PythonAnywhere và truy cập từ bất kỳ thiết bị nào:

### 1. Đăng ký và đăng nhập vào PythonAnywhere

- Truy cập: https://www.pythonanywhere.com
- Đăng ký tài khoản miễn phí và đăng nhập

### 2. Tải dự án lên PythonAnywhere

- Tải file ZIP từ Replit về máy tính
- Trong PythonAnywhere, nhấp vào tab "Files"
- Nhấp vào nút "Upload a file" và chọn file ZIP vừa tải
- Mở tab "Consoles" > "Bash" và chạy lệnh:
  ```bash
  cd ~
  unzip QuanLyVatTuDien.zip -d quanlyvattudien
  cd quanlyvattudien
  ```

### 3. Cài đặt các gói phụ thuộc

Trong console Bash, chạy các lệnh:

```bash
# Tạo môi trường ảo
python -m venv venv
source venv/bin/activate

# Cài đặt các gói cơ bản
pip install flask==2.3.3 flask-login==0.6.2 flask-sqlalchemy==3.1.1 gunicorn==23.0.0 email-validator==2.1.0 openpyxl==3.1.2 pandas==2.1.2 psycopg2-binary==2.9.9 reportlab==4.0.7 werkzeug==2.3.7 sqlalchemy==2.0.22

# Cài đặt NumPy phiên bản ổn định
pip install numpy==1.21.6

# Cài đặt OpenCV phiên bản không cần GUI
pip install opencv-python-headless==4.5.5.64

# Cài đặt pyzbar (có thể gặp lỗi nếu thiếu thư viện hệ thống)
pip install pyzbar
```

### 4. Thiết lập ứng dụng web

1. Nhấp vào tab "Web" của PythonAnywhere
2. Nhấp vào nút "Add a new web app"
3. Chọn domain mặc định (username.pythonanywhere.com)
4. Chọn "Manual configuration"
5. Chọn phiên bản Python phù hợp (ví dụ: 3.9)
6. Điền các thông tin:
   - Source code: `/home/yourusername/quanlyvattudien`
   - Working directory: `/home/yourusername/quanlyvattudien`

### 5. Cấu hình WSGI

1. Nhấp vào đường dẫn file cấu hình WSGI
2. Xóa nội dung hiện tại và thay thế bằng:
   ```python
   import sys
   import os
   
   path = '/home/yourusername/quanlyvattudien'
   if path not in sys.path:
       sys.path.append(path)
   
   os.environ['SECRET_KEY'] = 'your-secret-key'
   
   from wsgi import application
   ```
3. Lưu file

### 6. Cấu hình Static Files

1. Trong tab "Web", cuộn xuống phần "Static files"
2. Thêm ánh xạ:
   - URL: `/static/`
   - Directory: `/home/yourusername/quanlyvattudien/static`

### 7. Cấu hình môi trường ảo

1. Trong phần "Virtualenv", nhập đường dẫn: `/home/yourusername/quanlyvattudien/venv`

### 8. Khởi tạo cơ sở dữ liệu

```bash
cd ~/quanlyvattudien
source venv/bin/activate
python -c "from app import db; db.create_all()"
```

### 9. Tải lại ứng dụng

Nhấp vào nút "Reload" trong tab "Web" và đợi ứng dụng khởi động.

### 10. Truy cập ứng dụng

Ứng dụng của bạn sẽ khả dụng tại địa chỉ:
`https://yourusername.pythonanywhere.com`

## Ghi chú bổ sung

- Nếu gặp lỗi với thư viện pyzbar, có thể cần cài đặt phiên bản thấp hơn hoặc sử dụng phương pháp cài đặt khác.
- Nếu thấy thông báo lỗi liên quan đến NumPy hoặc OpenCV, kiểm tra log trong tab "Web" và tab "Logs".
- Tài khoản miễn phí của PythonAnywhere có giới hạn CPU và bộ nhớ, nên hãy chú ý khi xử lý nhiều hình ảnh cùng lúc.

## Người phát triển

Phát triển bởi [Tên của bạn] sử dụng Flask và SQLAlchemy.