/**
 * Main JavaScript file cho ứng dụng quản lý vật tư điện
 */

// Thiết lập sẵn sàng khi DOM đã được tải
document.addEventListener('DOMContentLoaded', function() {
    // Bật tooltip Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Xử lý flash messages tự động biến mất sau 5 giây
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert-auto-dismiss');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Xử lý xác nhận xóa
    var deleteButtons = document.querySelectorAll('.btn-delete-confirm');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Bạn có chắc chắn muốn thực hiện hành động này không?')) {
                e.preventDefault();
            }
        });
    });

    // Xử lý định dạng tiền tệ
    var currencyInputs = document.querySelectorAll('.currency-input');
    currencyInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            var value = this.value.replace(/\D/g, '');
            this.value = formatCurrency(value);
        });
        
        // Format giá trị ban đầu
        var initialValue = input.value.replace(/\D/g, '');
        input.value = formatCurrency(initialValue);
    });

    // Xử lý input chỉ nhận số
    var numberInputs = document.querySelectorAll('.number-only');
    numberInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            this.value = this.value.replace(/[^\d]/g, '');
        });
    });

    // Bắt sự kiện tìm kiếm
    var searchForms = document.querySelectorAll('.search-form');
    searchForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            // Loại bỏ các tham số trống
            var inputs = form.querySelectorAll('input, select');
            inputs.forEach(function(input) {
                if (input.value === '' || input.value === null) {
                    input.disabled = true;
                }
            });
        });
    });

    // Xử lý toggle sidebar trên mobile
    var sidebarToggleBtn = document.getElementById('sidebar-toggle');
    if (sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener('click', function() {
            document.getElementById('sidebar').classList.toggle('show');
        });
    }
});

// Hàm định dạng số tiền
function formatCurrency(value) {
    if (!value) return '';
    return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

// Hàm chuyển định dạng tiền tệ về số
function parseCurrency(value) {
    if (!value) return 0;
    return parseInt(value.replace(/\./g, ''));
}

// Hàm hiển thị thông báo
function showAlert(message, type = 'info') {
    var alertContainer = document.getElementById('alert-container');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.id = 'alert-container';
        alertContainer.style.position = 'fixed';
        alertContainer.style.top = '10px';
        alertContainer.style.right = '10px';
        alertContainer.style.zIndex = '9999';
        document.body.appendChild(alertContainer);
    }

    var alert = document.createElement('div');
    alert.className = 'alert alert-' + type + ' alert-dismissible fade show';
    alert.innerHTML = message + 
                      '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';
    
    alertContainer.appendChild(alert);
    
    // Tự động đóng sau 5 giây
    setTimeout(function() {
        var bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
}

// Hàm tạo ID duy nhất
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Hàm tính tổng mảng số
function sumArray(arr) {
    return arr.reduce(function(a, b) {
        return a + b;
    }, 0);
}

// Hàm format ngày giờ
function formatDateTime(dateTimeStr) {
    if (!dateTimeStr) return '';
    
    var date = new Date(dateTimeStr);
    
    var day = date.getDate().toString().padStart(2, '0');
    var month = (date.getMonth() + 1).toString().padStart(2, '0');
    var year = date.getFullYear();
    
    var hours = date.getHours().toString().padStart(2, '0');
    var minutes = date.getMinutes().toString().padStart(2, '0');
    
    return `${day}/${month}/${year} ${hours}:${minutes}`;
}

// Hàm format ngày
function formatDate(dateStr) {
    if (!dateStr) return '';
    
    var date = new Date(dateStr);
    
    var day = date.getDate().toString().padStart(2, '0');
    var month = (date.getMonth() + 1).toString().padStart(2, '0');
    var year = date.getFullYear();
    
    return `${day}/${month}/${year}`;
}
