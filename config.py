# --- CẤU HÌNH CHÂN SENSOR (Module 8 mắt) ---
# Điền chân GPIO của ESP32 tương ứng nối với D1 -> D8 của module
SENSOR_PINS = [32, 33, 34, 35, 36, 39, 2, 4] 
IR_EN_PIN = 15 # Chân bật/tắt LED hồng ngoại (nối với chân IR của module)

# --- CẤU HÌNH CHÂN MOTOR DRIVER (L298N hoặc TB6612) ---
M_L_IN1 = 25
M_L_IN2 = 26
M_L_PWM = 27

M_R_IN1 = 14
M_R_IN2 = 12
M_R_PWM = 13

# --- THÔNG SỐ PID & TỐC ĐỘ ---
# Tốc độ nền (0 - 1023) - Tăng lên khi xe đã chạy ổn định
BASE_SPEED = 400 

KP = 15.0  # Tăng cái này trước để xe phản ứng với vạch
KI = 0.0   # Tạm thời để 0
KD = 2.0   # Tăng cái này để giảm độ lắc (vẫy đuôi)