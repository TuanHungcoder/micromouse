from machine import Pin
import config

class Encoder:
    def __init__(self, pin_a, pin_b):
        self.pa = Pin(pin_a, Pin.IN, Pin.PULL_UP)
        self.pb = Pin(pin_b, Pin.IN, Pin.PULL_UP)
        self.ticks = 0
        
        # Thiết lập ngắt cho pha A
        self.pa.irq(handler=self._callback, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING)

    def _callback(self, pin):
        # Logic giải mã tín hiệu Quadrature (Pha A và B)
        # Nếu trạng thái Pha A khác Pha B -> Đang tiến (hoặc ngược lại tùy cách đấu dây)
        if self.pa.value() != self.pb.value():
            self.ticks += 1
        else:
            self.ticks -= 1

    def get_ticks(self):
        return self.ticks

    def reset(self):
        self.ticks = 0

class SystemEncoders:
    def __init__(self):
        self.left = Encoder(config.ENC_L_A, config.ENC_L_B)
        self.right = Encoder(config.ENC_R_A, config.ENC_R_B)