/**
 * Xử lý quét mã vạch bằng camera
 */

// Khai báo biến toàn cục
let videoElement;
let canvasElement;
let canvasContext;
let streaming = false;
let timerId = null;

// Khởi tạo quét mã vạch
function initBarcodeScanner(videoId, canvasId, resultInputId, scanStartBtnId, scanStopBtnId) {
    videoElement = document.getElementById(videoId);
    canvasElement = document.getElementById(canvasId);
    canvasContext = canvasElement.getContext('2d');
    
    let resultInput = document.getElementById(resultInputId);
    const startScanBtn = document.getElementById(scanStartBtnId);
    const stopScanBtn = document.getElementById(scanStopBtnId);
    
    // Xử lý nút bắt đầu quét
    startScanBtn.addEventListener('click', function() {
        startCamera();
        startScanBtn.style.display = 'none';
        stopScanBtn.style.display = 'inline-block';
    });
    
    // Xử lý nút dừng quét
    stopScanBtn.addEventListener('click', function() {
        stopCamera();
        startScanBtn.style.display = 'inline-block';
        stopScanBtn.style.display = 'none';
    });
    
    // Ẩn nút dừng ban đầu
    stopScanBtn.style.display = 'none';
}

// Hàm bắt đầu camera
function startCamera() {
    if (streaming) return;
    
    navigator.mediaDevices.getUserMedia({ 
        video: { 
            facingMode: "environment",
            width: { ideal: 1280 },
            height: { ideal: 720 }
        },
        audio: false 
    })
    .then(function(stream) {
        videoElement.srcObject = stream;
        videoElement.play();
        streaming = true;
        
        // Thiết lập kích thước canvas
        videoElement.addEventListener('canplay', function() {
            canvasElement.width = videoElement.videoWidth;
            canvasElement.height = videoElement.videoHeight;
        });
        
        // Bắt đầu quét
        startScanning();
    })
    .catch(function(err) {
        console.error("Lỗi truy cập camera:", err);
        alert("Không thể truy cập camera! Vui lòng kiểm tra quyền truy cập camera và thử lại.");
    });
}

// Hàm dừng camera
function stopCamera() {
    if (!streaming) return;
    
    const stream = videoElement.srcObject;
    const tracks = stream.getTracks();
    
    tracks.forEach(function(track) {
        track.stop();
    });
    
    videoElement.srcObject = null;
    streaming = false;
    
    // Dừng quét
    stopScanning();
}

// Bắt đầu quét mã vạch
function startScanning() {
    if (timerId) return;
    
    timerId = setInterval(function() {
        if (streaming) {
            captureAndScanImage();
        }
    }, 500);
}

// Dừng quét mã vạch
function stopScanning() {
    if (timerId) {
        clearInterval(timerId);
        timerId = null;
    }
}

// Chụp và quét hình ảnh
function captureAndScanImage() {
    if (!streaming) return;
    
    canvasContext.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
    let imageData = canvasElement.toDataURL('image/jpeg');
    
    // Gửi hình ảnh lên server để quét mã vạch
    scanBarcodeOnServer(imageData);
}

// Gửi ảnh lên server để quét mã vạch
function scanBarcodeOnServer(imageData) {
    fetch('/san-pham/scan-barcode', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'image=' + encodeURIComponent(imageData),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Tìm thấy mã vạch
            let barcodeValue = data.data;
            let barcodeResultInput = document.getElementById('ma_vach');
            if (barcodeResultInput) {
                barcodeResultInput.value = barcodeValue;
                
                // Dừng quét khi đã tìm thấy
                stopCamera();
                
                // Kích hoạt nút bắt đầu
                document.getElementById('start-scan-btn').style.display = 'inline-block';
                document.getElementById('stop-scan-btn').style.display = 'none';
                
                // Hiển thị thông báo
                showAlert('Đã quét được mã vạch: ' + barcodeValue, 'success');
                
                // Hiển thị ảnh đã quét
                if (document.getElementById('barcode-preview')) {
                    document.getElementById('barcode-preview').src = imageData;
                    document.getElementById('barcode-preview-container').style.display = 'block';
                }
                
                // Nếu đang ở trang nhập/xuất kho, tìm sản phẩm theo mã vạch
                if (window.location.pathname.includes('/nhap-kho/them') || 
                    window.location.pathname.includes('/xuat-kho/them')) {
                    findProductByBarcode(barcodeValue);
                }
            }
        }
    })
    .catch(error => {
        console.error('Lỗi khi quét mã vạch:', error);
    });
}

// Tìm sản phẩm theo mã vạch
function findProductByBarcode(barcode) {
    let url = window.location.pathname.includes('/nhap-kho/') 
        ? '/nhap-kho/get-san-pham-by-barcode'
        : '/xuat-kho/get-san-pham-by-barcode';
    
    fetch(`${url}?ma_vach=${encodeURIComponent(barcode)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Tìm thấy sản phẩm, thêm vào phiếu
                let sanPham = data.san_pham;
                
                if (window.location.pathname.includes('/nhap-kho/')) {
                    addProductToPhieuNhap(sanPham);
                } else {
                    addProductToPhieuXuat(sanPham);
                }
                
                showAlert('Đã tìm thấy sản phẩm: ' + sanPham.ten, 'success');
            } else {
                showAlert(data.message, 'warning');
            }
        })
        .catch(error => {
            console.error('Lỗi khi tìm sản phẩm:', error);
            showAlert('Đã xảy ra lỗi khi tìm sản phẩm', 'danger');
        });
}

// Chụp ảnh từ camera
function captureImage(videoId, canvasId, previewId, hiddenInputId) {
    const video = document.getElementById(videoId);
    const canvas = document.getElementById(canvasId);
    const preview = document.getElementById(previewId);
    const hiddenInput = document.getElementById(hiddenInputId);
    
    // Đảm bảo video đang chạy
    if (video.paused || video.ended) {
        alert('Vui lòng bật camera trước khi chụp ảnh!');
        return;
    }
    
    // Thiết lập kích thước canvas
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Vẽ hình ảnh từ video lên canvas
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Lấy dữ liệu hình ảnh dưới dạng base64
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    
    // Hiển thị hình ảnh đã chụp
    preview.src = imageData;
    preview.style.display = 'block';
    
    // Lưu dữ liệu vào input ẩn
    hiddenInput.value = imageData;
    
    // Hiển thị thông báo
    showAlert('Đã chụp ảnh thành công!', 'success');
}

// Khởi động camera để chụp ảnh sản phẩm
function startCameraForPhoto(videoId, startBtnId, captureBtnId, stopBtnId) {
    const video = document.getElementById(videoId);
    const startBtn = document.getElementById(startBtnId);
    const captureBtn = document.getElementById(captureBtnId);
    const stopBtn = document.getElementById(stopBtnId);
    
    // Bật camera
    navigator.mediaDevices.getUserMedia({
        video: {
            facingMode: "environment",
            width: { ideal: 1280 },
            height: { ideal: 720 }
        },
        audio: false
    })
    .then(function(stream) {
        video.srcObject = stream;
        video.play();
        
        // Hiển thị các nút liên quan
        startBtn.style.display = 'none';
        captureBtn.style.display = 'inline-block';
        stopBtn.style.display = 'inline-block';
        video.style.display = 'block';
    })
    .catch(function(err) {
        console.error("Lỗi truy cập camera:", err);
        alert("Không thể truy cập camera! Vui lòng kiểm tra quyền truy cập camera và thử lại.");
    });
}

// Dừng camera chụp ảnh
function stopCameraForPhoto(videoId, startBtnId, captureBtnId, stopBtnId) {
    const video = document.getElementById(videoId);
    const startBtn = document.getElementById(startBtnId);
    const captureBtn = document.getElementById(captureBtnId);
    const stopBtn = document.getElementById(stopBtnId);
    
    // Dừng video stream
    if (video.srcObject) {
        const stream = video.srcObject;
        const tracks = stream.getTracks();
        
        tracks.forEach(function(track) {
            track.stop();
        });
        
        video.srcObject = null;
    }
    
    // Cập nhật giao diện
    video.style.display = 'none';
    startBtn.style.display = 'inline-block';
    captureBtn.style.display = 'none';
    stopBtn.style.display = 'none';
}
