class PID:
    def __init__(self, kp, ki, kd, min_out=-100, max_out=100):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.min_out = min_out
        self.max_out = max_out
        
        self.prev_error = 0
        self.integral = 0

    def compute(self, error, dt):
        # 1. Khâu Tích phân (I)
        self.integral += error * dt
        # Anti-windup (Tránh tích phân cộng dồn quá lớn)
        self.integral = max(min(self.integral, 200), -200)

        # 2. Khâu Đạo hàm (D) - Tốc độ thay đổi của sai số
        derivative = (error - self.prev_error) / dt
        
        # 3. Khâu Tỉ lệ (P) + I + D
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        
        # Lưu lại sai số cho vòng lặp sau
        self.prev_error = error
        
        # Cắt gọt tín hiệu đầu ra để vừa với giới hạn của Motor
        return max(min(output, self.max_out), self.min_out)

    def reset(self):
        """Gọi hàm này ngay sau khi xe hoàn thành một pha rẽ cua 90 độ"""
        self.prev_error = 0
        self.integral = 0