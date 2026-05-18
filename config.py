# --- Cảm biến IR ---
SENSOR_PINS = [34, 35, 36, 39]
IR_EN_PIN = 27

# --- Motor TB6612 ---
M_L_IN1 = 5
M_L_IN2 = 17
M_L_PWM = 16

M_R_IN1 = 18
M_R_IN2 = 19
M_R_PWM = 21

# Đảo chiều phần mềm: 1 = bình thường, -1 = đảo (khi 2 bánh cùng dấu mà 1 tiến 1 lùi)
# Thường chỉ cần MOTOR_R_SIGN = -1 (motor phải lắp quay ngược motor trái)
MOTOR_L_SIGN = 1
MOTOR_R_SIGN = -1

# --- Encoder ---
ENC_L_A = 4
ENC_L_B = 15
ENC_R_A = 22
ENC_R_B = 23

# --- Ngưỡng cảm biến ---
SIDE_WALL_THRESHOLD = 500
FRONT_WALL_THRESHOLD = 800
TARGET_WALL_VAL = 1200

# --- Điều khiển (PWM duty 0–1023) ---
BASE_SPEED = 400
MAX_STEER = 350

KP = 0.8
KI = 0.0
KD = 0.15

# --- Vật lý ---
TICKS_PER_REV = 360
WHEEL_DIAMETER = 34

# Chu kỳ vòng lặp điều khiển (ms)
LOOP_PERIOD_MS = 10
