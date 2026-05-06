from machine import Pin
import config

class Encoder:
    def __init__(self, pin_a, pin_b):
        # Khởi tạo 2 chân tín hiệu với điện trở kéo lên (Pull-up) để chống nhiễu
        self.pa = Pin(pin_a, Pin.IN, Pin.PULL_UP)
        self.pb = Pin(pin_b, Pin.IN, Pin.PULL_UP)
        
        # Biến lưu trữ tổng số xung
        self.ticks = 0
        
        # Thiết lập ngắt (Interrupt) cho Pha A
        # Kích hoạt ngắt ở cả sườn lên (RISING) và sườn xuống (FALLING) để tăng gấp đôi độ phân giải
        self.pa.irq(handler=self._callback, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING)

    def _callback(self, pin):
        """
        Hàm ngắt này tự động chạy mỗi khi Pha A thay đổi trạng thái.
        Không gọi lệnh print() hay sleep() ở đây để tránh làm treo vi điều khiển.
        """
        # Thuật toán giải mã Quadrature cơ bản:
        # So sánh trạng thái hiện tại của Pha A và Pha B để biết xe đang tiến hay lùi
        if self.pa.value() != self.pb.value():
            self.ticks += 1
        else:
            self.ticks -= 1

    def get_ticks(self):
        """Lấy giá trị xung hiện tại"""
        return self.ticks

    def reset(self):
        """Xóa bộ đếm về 0 (Thường dùng khi bắt đầu đi vào một ô mê cung mới)"""
        self.ticks = 0

class SystemEncoders:
    def __init__(self):
        # Khởi tạo 2 encoder cho bánh trái và bánh phải sử dụng thông số từ config.py
        self.left = Encoder(config.ENC_L_A, config.ENC_L_B)
        self.right = Encoder(config.ENC_R_A, config.ENC_R_B)
        
    def reset_all(self):
        """Hàm tiện ích để reset cả 2 bánh cùng lúc"""
        self.left.reset()
        self.right.reset()