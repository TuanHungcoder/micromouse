import time
import math
import config

class RobotNavigator:
    def __init__(self, motors, encoders, sensors, pid):
        self.motors = motors
        self.encoders = encoders
        self.sensors = sensors
        self.pid = pid
        
        # Tính toán thông số chuyển đổi từ mm sang xung encoder
        self.wheel_circumference = config.WHEEL_DIAMETER * math.pi
        self.ticks_per_mm = config.TICKS_PER_REV / self.wheel_circumference
        
    def move_straight(self, distance_mm):
        """Di chuyển thẳng một quãng đường cho trước, có sử dụng PID bám tường"""
        target_ticks = distance_mm * self.ticks_per_mm
        
        self.encoders.reset_all()
        self.pid.reset()
        
        last_time = time.ticks_ms()
        
        while True:
            current_time = time.ticks_ms()
            dt = time.ticks_diff(current_time, last_time) / 1000.0
            if dt <= 0:
                dt = 0.001
            last_time = current_time
            
            # Tính trung bình số xung của 2 bánh để biết quãng đường đã đi
            left_ticks = self.encoders.left.get_ticks()
            right_ticks = self.encoders.right.get_ticks()
            current_ticks = (left_ticks + right_ticks) / 2.0
            
            # Nếu đạt đủ quãng đường thì kết thúc vòng lặp (không tắt động cơ)
            if current_ticks >= target_ticks:
                break
                
            # Đọc cảm biến để PID bám tường
            self.sensors.read_sensors()
            has_left, has_front, has_right = self.sensors.check_walls_for_maze()
            
            # Xử lý đâm tường khẩn cấp
            if has_front and (self.sensors.values[1] + self.sensors.values[2] > 2000):
                self.motors.stop()
                break
                
            error = self.sensors.get_steering_error()
            correction = self.pid.compute(error, dt)
            
            left_speed = config.BASE_SPEED + correction
            right_speed = config.BASE_SPEED - correction
            
            self.motors.drive(left_speed, right_speed)
            time.sleep_ms(10)

    def curve_turn_only(self, angle_degrees, R=40.0):
        """Chỉ thực hiện bo cua vòng cung vi sai bằng Cosine Velocity Profile"""
        print(f"Đang bo cua mượt (Cosin) {angle_degrees} độ...")
        
        W = config.WHEEL_DISTANCE
        constant_ratio = (R - W/2.0) / (R + W/2.0)
        
        outer_speed = config.BASE_SPEED
        constant_inner_speed = config.BASE_SPEED * constant_ratio
        
        # Để góc quay vẫn đủ 90 độ với đồ thị Cosin, 
        # độ sụt giảm tốc độ ở đỉnh cua (apex) phải gấp đôi đường tròn tĩnh
        delta_v = 2.0 * (outer_speed - constant_inner_speed)
        
        arc_length_outer = (abs(angle_degrees) / 360.0) * 2 * math.pi * (R + W/2.0)
        target_ticks_outer = arc_length_outer * self.ticks_per_mm
        
        self.encoders.reset_all()
        
        while True:
            left_ticks = abs(self.encoders.left.get_ticks())
            right_ticks = abs(self.encoders.right.get_ticks())
            
            # Tính phần trăm hoàn thành vòng cua (p: 0.0 -> 1.0)
            if angle_degrees > 0:
                p = left_ticks / target_ticks_outer
            else:
                p = right_ticks / target_ticks_outer
                
            if p >= 1.0:
                break
                
            # Đồ thị hình chuông (Hanning window)
            f_p = (1.0 - math.cos(2 * math.pi * p)) / 2.0
            inner_speed = outer_speed - delta_v * f_p
            
            if angle_degrees > 0:
                self.motors.drive(outer_speed, inner_speed)
            else:
                self.motors.drive(inner_speed, outer_speed)
                
            time.sleep_ms(10)

    def _turn_angle(self, angle_degrees):
        """Hàm xoay góc cơ bản, angle > 0 là xoay phải, angle < 0 là xoay trái"""
        print(f"Đang quay {angle_degrees} độ...")
        
        # TRƯỚC KHI QUAY: Dừng hẳn xe lại để triệt tiêu hoàn toàn quán tính
        self.motors.stop()
        time.sleep_ms(150)
        
        # Chu vi vòng tròn do 2 bánh xe tạo ra khi quay tại chỗ
        turning_circle_circumference = config.WHEEL_DISTANCE * math.pi
        
        # Khoảng cách 1 bánh xe cần di chuyển trên cung tròn
        arc_length_mm = (abs(angle_degrees) / 360.0) * turning_circle_circumference
        
        # Số xung tương ứng
        target_ticks = arc_length_mm * self.ticks_per_mm
        
        self.encoders.reset_all()
        
        # Tốc độ quay (Chậm hơn đi thẳng để đảm bảo chính xác)
        turn_speed = config.BASE_SPEED * 0.8
        
        while True:
            left_ticks = abs(self.encoders.left.get_ticks())
            right_ticks = abs(self.encoders.right.get_ticks())
            
            avg_ticks = (left_ticks + right_ticks) / 2.0
            
            if avg_ticks >= target_ticks:
                self.motors.stop()
                # Nghỉ ngắn sau khi quay để xe ổn định
                time.sleep_ms(100)
                break
                
            if angle_degrees > 0:
                # Quay phải: bánh trái tiến, bánh phải lùi
                self.motors.drive(turn_speed, -turn_speed)
            else:
                # Quay trái: bánh trái lùi, bánh phải tiến
                self.motors.drive(-turn_speed, turn_speed)
                
            time.sleep_ms(10)

    def turn_right(self):
        """Quay phải 90 độ tại chỗ"""
        self._turn_angle(90)
        
    def turn_left(self):
        """Quay trái 90 độ tại chỗ"""
        self._turn_angle(-90)
        
    def turn_around(self):
        """Quay đầu 180 độ tại chỗ"""
        self._turn_angle(180)
