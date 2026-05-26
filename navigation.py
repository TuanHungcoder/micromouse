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
        
        # Lưu trạng thái chạy liên tục để không bị mất xung dư khi gọi hàm liên tiếp
        self.was_continuous = False
        self.last_target_ticks = 0
        
    def move_straight(self, distance_mm, continuous=False):
        """Di chuyển thẳng, hỗ trợ khử sai số dọc (Edge Detection) và không phanh nếu continuous=True"""
        target_ticks = distance_mm * self.ticks_per_mm
        
        # Nếu đang trong chuỗi chạy liên tục, KHÔNG reset encoder về 0
        # Mà chỉ trừ đi quãng đường của ô trước. Điều này giúp giữ lại phần xung dư (overshoot/coasting)
        # sinh ra trong quá trình main.py xử lý thuật toán!
        if self.was_continuous:
            self.encoders.left.ticks -= int(self.last_target_ticks)
            self.encoders.right.ticks -= int(self.last_target_ticks)
        else:
            self.encoders.reset_all()
            
        self.was_continuous = continuous
        self.last_target_ticks = target_ticks
        self.edge_detected_this_cell = False
        
        self.pid.reset()
        
        last_time = time.ticks_ms()
        
        # Biến tích lũy cho bộ lọc không gian Gaussian
        left_sum = 0.0
        right_sum = 0.0
        weight_sum = 0.0
        
        # Biến cho Edge Detection (Nhận diện sườn xung để khử sai số tĩnh)
        prev_left = self.sensors.values[0]
        prev_right = self.sensors.values[3]
        TICKS_PER_CELL = config.CELL_SIZE * self.ticks_per_mm
        
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
            
            left_val = self.sensors.values[0]
            right_val = self.sensors.values[3]
            
            # === EDGE DETECTION (DÙNG CẢM BIẾN LÀM MỐC CHO ENCODER) ===
            EDGE_THRESHOLD = config.SIDE_WALL_THRESHOLD
            
            # Cờ đánh dấu đã nhận diện mép tường trong ô này chưa
            if not hasattr(self, 'edge_detected_this_cell'):
                self.edge_detected_this_cell = False
                
            if not self.edge_detected_this_cell:
                # Cửa sổ quét hẹp lại (25% - 55% quãng đường) để tránh xe lắc lư (wobble) gây nhiễu
                # Ranh giới vật lý nằm ở khoảng 38% (65mm / 170mm).
                progress = current_ticks / (config.CELL_SIZE * self.ticks_per_mm)
                
                if 0.25 < progress < 0.55:
                    edge_triggered = False
                    
                    # Phải tuột xuống dưới 50% Threshold mới được coi là có khoảng trống (tránh nhiễu)
                    if (prev_left > EDGE_THRESHOLD and left_val < EDGE_THRESHOLD * 0.5) or \
                       (prev_left < EDGE_THRESHOLD * 0.5 and left_val > EDGE_THRESHOLD):
                        edge_triggered = True
                        
                    if (prev_right > EDGE_THRESHOLD and right_val < EDGE_THRESHOLD * 0.5) or \
                       (prev_right < EDGE_THRESHOLD * 0.5 and right_val > EDGE_THRESHOLD):
                        edge_triggered = True
                        
                    if edge_triggered:
                        # Vị trí thực tế của tâm bánh xe khi cảm biến vừa qua mép tường
                        actual_dist_mm = (config.CELL_SIZE / 2.0) - config.SENSOR_OFFSET + getattr(config, 'OVERSHOOT_COMPENSATION', 10)
                        actual_ticks = actual_dist_mm * self.ticks_per_mm
                        
                        # ÉP BUỘC Encoder phải nhận giá trị thực tế này
                        if current_ticks > 0:
                            correction_factor = actual_ticks / current_ticks
                            self.encoders.left.ticks = int(self.encoders.left.ticks * correction_factor)
                            self.encoders.right.ticks = int(self.encoders.right.ticks * correction_factor)
                            
                        self.edge_detected_this_cell = True
            
            prev_left = left_val
            prev_right = right_val
            # ======================================================
            
            # === BỘ LỌC KHÔNG GIAN TÌM TƯỜNG Ô MỚI ===
            # Theo ý tưởng của bạn: Bắt đầu lấy trung bình TỪ LÚC xảy ra sự thay đổi đột ngột (mép tường)
            # Ta cộng thêm 20mm vào mốc bắt đầu để mắt cảm biến đi lố qua hẳn cái cột vách tường, tránh đọc nhầm cột thành tường!
            boundary_ticks = (config.CELL_SIZE / 2.0 - config.SENSOR_OFFSET + 20) * self.ticks_per_mm
            
            if (self.edge_detected_this_cell and current_ticks > actual_ticks + 20*self.ticks_per_mm) or current_ticks > boundary_ticks:
                left_sum += left_val
                right_sum += right_val
                weight_sum += 1.0  # Dùng weight_sum như một biến đếm (read_count)
            # ==================================
            
            # === LOGIC DỪNG KẾT HỢP (SENSOR FUSION) ===
            FL = self.sensors.values[1]
            FR = self.sensors.values[2]
            front_avg = (FL + FR) / 2.0
            
            # Phát hiện tường trước từ xa
            has_front_wall_far = (FL > 250 and FR > 250) and (front_avg > config.FRONT_WALL_THRESHOLD)
            
            # Tính năng Khám Phá Liên Tục (Continuous Exploration):
            # HỦY bỏ trạng thái continuous NGAY LẬP TỨC nếu bất ngờ phát hiện tường trước!
            if has_front_wall_far and continuous:
                continuous = False
                
            if has_front_wall_far and not continuous:
                # Có tường trước: Tạm gác Encoder, tin tưởng tuyệt đối vào Cảm biến!
                if front_avg >= config.TARGET_FRONT_WALL_VAL:
                    break
                elif current_ticks > target_ticks * 1.2:
                    break
            else:
                # Đường trước trống hoặc đang chạy Continuous: Dùng Encoder
                if current_ticks >= target_ticks:
                    break
            # ==========================================
                
            error = self.sensors.get_steering_error()
            correction = self.pid.compute(error, dt)
            
            # Tính toán tốc độ gốc (Trapezoidal Velocity Profile - Giảm tốc mượt mà)
            current_base_speed = config.BASE_SPEED
            remaining_ticks = target_ticks - current_ticks
            brake_distance_ticks = 40.0 * self.ticks_per_mm # Khôi phục lại 40mm
            
            # CHỈ GIẢM TỐC NẾU KHÔNG CHẠY CONTINUOUS
            if not continuous:
                if not has_front_wall_far and 0 < remaining_ticks < brake_distance_ticks:
                    min_speed_ratio = 0.3 # Khôi phục 30% để tránh lỗi tụt áp / stall motor (không đủ lực kéo)
                    ratio = min_speed_ratio + (1.0 - min_speed_ratio) * (remaining_ticks / brake_distance_ticks)
                    current_base_speed = config.BASE_SPEED * ratio
                
            left_speed = current_base_speed + correction
            right_speed = current_base_speed - correction
            
            self.motors.drive(left_speed, right_speed)
            time.sleep_ms(10)
            
        # NẾU CHẠY CONTINUOUS, THOÁT NGAY LẬP TỨC ĐỂ LAO VÀO GÓC CUA!
        if continuous:
            return
            
        # DỪNG CHÍNH XÁC TẠI TÂM Ô
        # Áp dụng phanh điện từ (Short Brake) trong thời gian siêu ngắn (50ms)
        # Vì xe đã bò rất chậm (15%) nên phanh lúc này cực kỳ an toàn, không giật, không hại mạch
        self.motors.brake()
        time.sleep_ms(50)
        self.motors.stop()  # Trả về Coast an toàn để bảo vệ IC cầu H
            
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
        self.was_continuous = False

        
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
        self.was_continuous = False

        
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
