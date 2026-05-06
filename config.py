# --- CẤU HÌNH CHÂN SENSOR (Module 4 mắt) ---
# Điền chân GPIO của ESP32 tương ứng nối với D1 -> D8 của module
SENSOR_PINS = [34, 35, 36, 39] 
IR_EN_PIN = 27 # Chân bật/tắt LED hồng ngoại (nối với chân IR của module)



SIDE_WALL_THRESHOLD = 500  # Lớn hơn số này coi như có tường bên
FRONT_WALL_THRESHOLD = 800 # Lớn hơn số này coi như đâm tường trước
TARGET_WALL_VAL = 1200     # Giá trị chuẩn khi xe cách đều 2 tường

# Thông số vật lý (Cần hiệu chỉnh dựa trên bánh xe thực tế)
TICKS_PER_REV = 360 # Số xung trên mỗi vòng quay của motor
WHEEL_DIAMETER = 34 # Đường kính bánh xe (mm)

KP = 15.0  # Tăng cái này trước để xe phản ứng với vạch
KI = 0.0   # Tạm thời để 0
KD = 2.0   # Tăng cái này để giảm độ lắc (vẫy đuôi)
