# 🐭 Dự án Micromouse ESP32 - MicroPython

Dự án phát triển robot giải mê cung sử dụng vi điều khiển ESP32, lập trình bằng ngôn ngữ MicroPython.

## 🛠 Cấu trúc dự án
*   **`config.py`**: Cấu hình chân (Pinout), thông số PID và các hằng số hệ thống.
*   **`sensors.py`**: Xử lý 4 cảm biến IR Analog và thuật toán khử nhiễu.
*   **`motors.py`**: Điều khiển động cơ PWM và các hàm di chuyển cơ bản.
*   **`pid.py`**: Bộ điều khiển bám tường (Wall following).
*   **`maze.py`**: Thuật toán giải mê cung (Flood Fill).
*   **`main.py`**: Vòng lặp điều khiển chính (Hardware Timer 10ms).
*   **`encoders.py`**: Đo tốc độ xe.

## 🚀 Quy trình làm việc nhóm
1.  **Pull:** Luôn chạy `git pull` trước khi bắt đầu code.
2.  **Branch:** Làm tính năng mới trên nhánh riêng (ví dụ: `feature-maze`).
3.  **Commit:** Ghi chú rõ ràng những gì đã thay đổi.
4.  **Sync:** `Push` code lên ít nhất một lần sau mỗi buổi làm việc.

## 📌 Lưu ý kỹ thuật
*   Tần số PWM Motor: 20kHz.
*   Chu kỳ ngắt PID: 10ms.
*   Ngưỡng cảm biến nhận tường (Threshold): Cần hiệu chỉnh lại khi thay đổi môi trường ánh sáng.

Đây là chu kỳ bạn sẽ lặp đi lặp lại hàng chục lần mỗi ngày.
git pull: LUÔN LUÔN chạy lệnh này đầu buổi code để lấy code mới nhất mà bạn mình đã up lên.
git add .: Gom tất cả những thay đổi bạn vừa sửa (ví dụ: vừa chỉnh xong $K_p$ trong config.py).
git commit -m "Mô tả ngắn gọn": Đóng gói các thay đổi và đặt tên cho nó (ví dụ: "Fix lỗi quay 90 độ").
git push: Đẩy gói code đó lên GitHub cho bạn mình thấy.
