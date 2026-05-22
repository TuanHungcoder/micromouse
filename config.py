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

# --- CHÂN ENCODER ---
ENC_L_A = 23
ENC_L_B = 22
ENC_R_A = 4 # Đảo để đồng bộ với bánh phải
ENC_R_B = 15

SIDE_WALL_THRESHOLD = 500  # Lớn hơn số này coi như có tường bên
FRONT_WALL_THRESHOLD = 800 # Lớn hơn số này coi như đâm tường trước
TARGET_WALL_VAL = 1200     # Giá trị chuẩn khi xe cách đều 2 tường

# Thông số vật lý (Cần hiệu chỉnh dựa trên bánh xe thực tế)
GEAR_RATIO = 100          # Tỷ số truyền của hộp giảm tốc
MOTOR_BASE_TICKS = 7      # Số xung trên 1 vòng quay gốc của động cơ (Bạn vừa đo ra chính xác loại 7 xung)
# Số xung trên mỗi vòng quay của BÁNH XE (Do ngắt bắt cả sườn lên/xuống nên nhân 2)
TICKS_PER_REV = 1400      # Tương đương: 7 * 2 * 100 = 1400

WHEEL_DIAMETER = 34 # Đường kính bánh xe (mm)
WHEEL_DISTANCE = 105 # Khoảng cách giữa 2 bánh xe (mm) - Dùng để tính góc quay
CELL_SIZE = 150     # Chiều dài 1 ô vuông của mê cung (mm)

# --- THÔNG SỐ PID BÁM TƯỜNG (Dùng Cảm biến hồng ngoại) ---
KP = 15.0  # Tăng cái này trước để xe phản ứng với vạch
KI = 0.0   # Tạm thời để 0
KD = 2.0   # Tăng cái này để giảm độ lắc (vẫy đuôi)

# --- CẤU HÌNH WIFI & ĐIỀU KHIỂN ---
WIFI_SSID = "Micromouse"
WIFI_PASSWORD = "12345678"

# Biến trạng thái để xác định chế độ điều khiển
# True: Chạy tự động (thuật toán mê cung)
# False: Chạy thủ công (qua Web)
AUTO_MODE_ENABLED = True