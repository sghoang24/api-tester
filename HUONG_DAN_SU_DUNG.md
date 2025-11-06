# Hướng Dẫn Sử Dụng API Tester

## Giới Thiệu

Ứng dụng HTTP API Tester giúp bạn kiểm tra và gọi các API một cách dễ dàng với giao diện web đơn giản.

## Cách Sử Dụng

### 1. Đăng Nhập

- **Người dùng thường**: Nhập tên đăng nhập để sử dụng
- **Quản trị viên**: Sử dụng tài khoản `admin` để quản lý cấu hình toàn cục

### 2. Chọn Môi Trường

Chọn một trong ba môi trường:

- **DAI**: Môi trường phát triển
- **SIT**: Môi trường kiểm thử
- **UAT**: Môi trường thử nghiệm người dùng

### 3. Gọi API

#### Cách 1: Sử dụng API Đã Lưu

- Chọn API từ danh sách "Predefined API Tests" hoặc "Saved APIs"
- Nhấn "Test API" để thực thi

#### Cách 2: Tạo API Mới

1. Chọn **HTTP Method** (GET, POST, PUT, DELETE)
2. Nhập **Endpoint** (đường dẫn API)
3. Thêm **Headers** nếu cần (JSON format)
4. Thêm **Body** cho POST/PUT request (JSON format)
5. Nhấn **Send Request**

### 4. Xem Kết Quả

- Xem mã trạng thái (Status Code)
- Xem nội dung phản hồi (Response)
- Kiểm tra thời gian phản hồi

### 5. Lưu API

- Sau khi test thành công, có thể lưu cấu hình API
- Nhập tên để lưu vào danh sách cá nhân hoặc toàn cục

## Tính Năng Chính

✅ **Đa môi trường**: DAI, SIT, UAT  
✅ **Quản lý Cookie**: Tự động xử lý authentication  
✅ **Lưu API**: Lưu các cấu hình API để sử dụng lại  
✅ **Lịch sử**: Theo dõi các request đã thực hiện  
✅ **Giao diện đơn giản**: Dễ sử dụng với Streamlit

## Lưu Ý

- Đảm bảo có kết nối internet để gọi API
- Cookies được quản lý tự động cho từng môi trường
- Dữ liệu được lưu riêng biệt cho từng người dùng
