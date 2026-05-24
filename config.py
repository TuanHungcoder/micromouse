# --- CẤU HÌNH CHÂN SENSOR (Module 4 mắt) ---
# Điền chân GPIO của ESP32 tương ứng với từng mắt cảm biến
SENSOR_L_PIN = 35   # Mắt tường TRÁI
SENSOR_FL_PIN = 34  # Mắt chéo TRƯỚC - TRÁI
SENSOR_FR_PIN = 39  # Mắt chéo TRƯỚC - PHẢI
SENSOR_R_PIN = 36   # Mắt tường PHẢI
IR_EN_PIN = 27 # Chân bật/tắt LED hồng ngoại (nối với chân IR của module)

# --- CẤU HÌNH CHÂN MOTOR DRIVER (TB6612) ---
MOT_L_PWM = 21  
MOT_L_DIR1 = 19 
MOT_L_DIR2 = 18 

MOT_R_PWM = 16  
MOT_R_DIR1 = 5
MOT_R_DIR2 = 17

# --- THÔNG SỐ PID & TỐC ĐỘ ---
# Tốc độ nền (0 - 100) - Tăng lên khi xe đã chạy ổn định
BASE_SPEED = 50

# Hệ số cân bằng động cơ (Motor Multiplier)
# Nếu bánh trái quay chậm hơn bánh phải, hãy giảm hệ số bánh phải (vd: 0.95) hoặc tăng bánh trái (vd: 1.05)
MOTOR_LEFT_MULTIPLIER = 1.015  # Tăng lên 1 chút do bánh trái đang quay chậm hơn
MOTOR_RIGHT_MULTIPLIER = 1.0

# --- CHÂN ENCODER ---
ENC_L_A = 23
ENC_L_B = 22
ENC_R_A = 4 # Đảo để đồng bộ với bánh phải
ENC_R_B = 15

SIDE_WALL_THRESHOLD = 500   # Lớn hơn số này coi như có tường bên
FRONT_WALL_THRESHOLD = 500  # Ngưỡng nhận diện tường trước (Nhỏ hơn TARGET_FRONT_WALL_VAL để bắt từ xa)
TARGET_WALL_VAL = 1000      # Giá trị chuẩn khi xe cách đều 2 tường 2 bên (Tâm ô)
TARGET_FRONT_WALL_VAL = 700 # Giá trị chuẩn của mắt trước khi xe ở tâm ô và đối diện bức tường

# Thông số vật lý (Cần hiệu chỉnh dựa trên bánh xe thực tế)
GEAR_RATIO = 100          # Tỷ số truyền của hộp giảm tốc
MOTOR_BASE_TICKS = 7      # Số xung trên 1 vòng quay gốc của động cơ (Bạn vừa đo ra chính xác loại 7 xung)
# Số xung trên mỗi vòng quay của BÁNH XE (Do ngắt bắt cả sườn lên/xuống nên nhân 2)
TICKS_PER_REV = 1400      # Tương đương: 7 * 2 * 100 = 1400

WHEEL_DIAMETER = 34 # Đường kính bánh xe (mm)
WHEEL_DISTANCE = 70 # Khoảng cách giữa 2 bánh xe (mm) - Dùng để tính góc quay
CELL_SIZE = 180     # Chiều dài 1 ô vuông của mê cung (mm)

# --- THÔNG SỐ PID BÁM TƯỜNG (Dùng Cảm biến hồng ngoại) ---
KP = 0.007   # Đã giảm KP xuống 6 để bớt gắt
KI = 0.0   # TUYỆT ĐỐI KHÔNG DÙNG KI (Nguyên nhân chính làm xe lắc liên tục)
KD = 0.0004  # Tăng KD lên bằng KP để dập tắt dao động

# --- CẤU HÌNH WIFI & ĐIỀU KHIỂN ---
WIFI_SSID = "Micromouse"
WIFI_PASSWORD = "12345678"

# Biến trạng thái để xác định chế độ điều khiển
# True: Chạy tự động (thuật toán mê cung)
# False: Chạy thẳng vô tận để (Chỉnh PID qua Web)
AUTO_MODE_ENABLED = True