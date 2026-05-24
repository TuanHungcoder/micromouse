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
        
        # Biến tích lũy cho bộ lọc không gian Gaussian
        left_sum = 0.0
        right_sum = 0.0
        weight_sum = 0.0
        
        # Thông số phân bố chuẩn: Đỉnh (mu) ở giữa ô
        mu = target_ticks / 2.0
        # Giảm độ sắc nhọn của tâm (flatten curve) bằng cách tăng sigma
        sigma = target_ticks / 2.5
        
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
            
            # Đọc cảm biến để PID bám tường
            self.sensors.read_sensors()
            
            # === BỘ LỌC KHÔNG GIAN GAUSSIAN ===
            if sigma > 0:
                weight = math.exp(-((current_ticks - mu)**2) / (2 * sigma**2))
            else:
                weight = 1.0
                
            left_sum += self.sensors.values[0] * weight
            right_sum += self.sensors.values[3] * weight
            weight_sum += weight
            # ==================================
            
            # === LOGIC DỪNG KẾT HỢP (SENSOR FUSION) ===
            FL = self.sensors.values[1]
            FR = self.sensors.values[2]
            front_avg = (FL + FR) / 2.0
            
            # Phát hiện tường trước từ xa (dựa vào FRONT_WALL_THRESHOLD)
            has_front_wall_far = (FL > 250 and FR > 250) and (front_avg > config.FRONT_WALL_THRESHOLD)
            
            if has_front_wall_far:
                # Có tường trước: Tạm gác Encoder, tin tưởng tuyệt đối vào Cảm biến!
                # Cho xe chạy đến khi giá trị cảm biến đạt TARGET_FRONT_WALL_VAL (Giá trị đo được khi ở đúng tâm ô)
                if front_avg >= config.TARGET_FRONT_WALL_VAL:
                    break
                # An toàn: Nếu Encoder chạy lố quá 20% mà vẫn chưa đạt target thì dừng (chống kẹt)
                elif current_ticks > target_ticks * 1.2:
                    break
            else:
                # Đường trước trống: Bắt buộc dừng hoàn toàn dựa vào Encoder
                if current_ticks >= target_ticks:
                    break
            # ==========================================
                
            error = self.sensors.get_steering_error()
            correction = self.pid.compute(error, dt)
            
            # Tính toán tốc độ gốc (Trapezoidal Velocity Profile - Giảm tốc mượt mà)
            current_base_speed = config.BASE_SPEED
            remaining_ticks = target_ticks - current_ticks
            brake_distance_ticks = 40.0 * self.ticks_per_mm # Bắt đầu giảm tốc trước 40mm
            
            if not has_front_wall_far and 0 < remaining_ticks < brake_distance_ticks:
                # Ép tốc độ giảm dần từ 100% xuống 30% khi gần đến đích
                min_speed_ratio = 0.3
                ratio = min_speed_ratio + (1.0 - min_speed_ratio) * (remaining_ticks / brake_distance_ticks)
                current_base_speed = config.BASE_SPEED * ratio
                
            left_speed = current_base_speed + correction
            right_speed = current_base_speed - correction
            
            self.motors.drive(left_speed, right_speed)
            time.sleep_ms(10)
            
        # GIẢM TỐC TỪ TỪ (Soft Deceleration) ĐỂ BẢO VỆ MẠCH CẦU H TB6612
        # Vì xe đã được giảm tốc chủ động xuống còn rất chậm (30%) trước khi thoát vòng lặp,
        # bước này chỉ làm nhiệm vụ hãm nốt lượng tốc độ nhỏ nhoi còn lại trong 100ms.
        for i in range(4, -1, -1):
            ratio = i / 4.0
            self.motors.drive(left_speed * ratio, right_speed * ratio)
            time.sleep_ms(25)
            
        self.motors.stop()  # Trả về Coast an toàn
            
        # Tính trung bình có trọng số sau khi hoàn thành 1 ô
        if weight_sum > 0:
            self.sensors.scanned_left = left_sum / weight_sum
            self.sensors.scanned_right = right_sum / weight_sum

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
        
        # BÙ TRỪ TOÁN HỌC: 
        # Do WHEEL_DISTANCE đã được hạ xuống để trừ hao quán tính cho góc 90 độ, 
        # quán tính là một hằng số (không tăng gấp đôi khi quãng đường gấp đôi).
        # Nên khi góc tăng lên 180 độ, xe sẽ bị hụt khoảng 20 độ.
        compensated_angle = abs(angle_degrees)
        if compensated_angle == 180:
            compensated_angle += 20
            
        # Khoảng cách 1 bánh xe cần di chuyển trên cung tròn
        arc_length_mm = (compensated_angle / 360.0) * turning_circle_circumference
        
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
