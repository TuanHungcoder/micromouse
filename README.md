# 🐭 Dự án Micromouse ESP32 - MicroPython

Dự án phát triển robot giải mê cung sử dụng vi điều khiển ESP32, lập trình bằng ngôn ngữ MicroPython.

## 🛠 Cấu trúc dự án
*   **`config.py`**: Cấu hình chân (Pinout), thông số PID và các hằng số hệ thống.
*   **`sensors.py`**: Xử lý 4 cảm biến IR Analog và thuật toán khử nhiễu.
*   **`motors.py`**: Điều khiển động cơ PWM và các hàm di chuyển cơ bản.
*   **`pid.py`**: Bộ điều khiển bám tường (Wall following).
*   **`navigation.py`**: Quản lý điều hướng nâng cao và tạo quỹ đạo (profile vận tốc, quay sớm).
*   **`maze.py`**: Thuật toán giải mê cung (Flood Fill/DFS) và bản đồ.
*   **`webserver.py`**: Máy chủ web dùng cho điều khiển từ xa, theo dõi trạng thái và cấu hình PID.
*   **`main.py`**: Vòng lặp điều khiển chính (Hardware Timer 10ms, Threading).
*   **`encoders.py`**: Đọc encoder để đo tốc độ và quãng đường xe.
*   **`calibrate_encoder.py`**: Script hỗ trợ hiệu chuẩn và kiểm tra encoder.

## 🚀 Quy trình làm việc nhóm
1.  **Pull:** Luôn chạy `git pull` trước khi bắt đầu code.
2.  **Branch:** Làm tính năng mới trên nhánh riêng (ví dụ: `feature-maze`).
3.  **Commit:** Ghi chú rõ ràng những gì đã thay đổi.
4.  **Sync:** `Push` code lên ít nhất một lần sau mỗi buổi làm việc.

## 📌 Lưu ý kỹ thuật
*   Tần số PWM Motor: 20kHz.
*   Chu kỳ ngắt PID: 10ms.
*   Hỗ trợ đa luồng (Threading) cho web server và bộ điều khiển chính.
*   Ngưỡng cảm biến nhận tường (Threshold): Cần hiệu chỉnh lại khi thay đổi môi trường ánh sáng.

