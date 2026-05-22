from machine import Pin, PWM
import config

class Motor:
    def __init__(self, pwm_pin, dir_pin1, dir_pin2):
        # Khởi tạo PWM với tần số 20kHz (20000 Hz) để motor chạy êm, không bị nhiễu âm thanh
        self.pwm = PWM(Pin(pwm_pin), freq=20000)
        self.pwm.duty(0) # Mặc định cho dừng
        
        # 2 chân điều hướng cho mạch cầu H (ví dụ: TB6612FNG, DRV8833, L298N)
        self.dir1 = Pin(dir_pin1, Pin.OUT)
        self.dir2 = Pin(dir_pin2, Pin.OUT)

    def set_speed(self, speed):
        """
        Nhận giá trị tốc độ từ -100 (lùi tối đa) đến 100 (tiến tối đa)
        """
        # 1. Xử lý chiều quay
        if speed > 0:
            self.dir1.value(1)
            self.dir2.value(0)
        elif speed < 0:
            self.dir1.value(0)
            self.dir2.value(1)
        else:
            # Phanh động cơ (Brake)
            self.dir1.value(0)
            self.dir2.value(0)
            
        # 2. Xử lý tốc độ PWM
        # Ép tốc độ nằm trong khoảng an toàn từ 0 đến 100
        abs_speed = max(0, min(100, abs(speed)))
        
        # Chuyển đổi thang đo: % (0-100) sang Duty Cycle của ESP32 (0-1023)
        duty_val = int((abs_speed / 100.0) * 1023)
        self.pwm.duty(duty_val)

class MotorController:
    def __init__(self):
        # Khởi tạo 2 motor trái và phải dựa trên config
        self.left = Motor(config.MOT_L_PWM, config.MOT_L_DIR1, config.MOT_L_DIR2)
        self.right = Motor(config.MOT_R_PWM, config.MOT_R_DIR1, config.MOT_R_DIR2)
        
    def drive(self, left_speed, right_speed):
        """Hàm tiện ích để điều khiển cả 2 bánh cùng lúc"""
        self.left.set_speed(left_speed)
        self.right.set_speed(right_speed)
        
    def stop(self):
        """Dừng khẩn cấp"""
        self.drive(0, 0)