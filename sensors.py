from machine import Pin, ADC
import time
import config

class SensorArray:
    def __init__(self):
        self.ir_en = Pin(config.IR_EN_PIN, Pin.OUT)
        self.ir_en.value(0)
        
        self.adcs = []
        for pin_num in config.SENSOR_PINS:
            adc = ADC(Pin(pin_num))
            adc.atten(ADC.ATTN_11DB) # Đọc dải 0-3.3V (Giá trị 0-4095)
            self.adcs.append(adc)
            
        self.values = [0, 0, 0, 0]

    def read_sensors(self):
        ambient = [0, 0, 0, 0]
        raw = [0, 0, 0, 0]

        # 1. Đọc nhiễu môi trường (LED tắt)
        self.ir_en.value(0)
        time.sleep_us(50)
        for i in range(4): ambient[i] = self.adcs[i].read()

        # 2. Đọc tín hiệu thực (LED bật)
        self.ir_en.value(1)
        time.sleep_us(60)
        for i in range(4): raw[i] = self.adcs[i].read()
        self.ir_en.value(0) # Tắt ngay để tiết kiệm pin

        # 3. Trừ nhiễu
        for i in range(4):
            val = raw[i] - ambient[i]
            self.values[i] = max(0, val) # Không để số âm

    def get_steering_error(self):
        # Tính toán độ lệch giữa tường trái và tường phải
        left_val = self.values[0]
        right_val = self.values[3]
        
        th = config.SIDE_WALL_THRESHOLD

        if left_val > th and right_val > th:
            return left_val - right_val

        elif left_val > th:
            return left_val - config.TARGET_WALL_VAL

        elif right_val > th:
            return config.TARGET_WALL_VAL - right_val
            
        # Không có tường nào ở 2 bên
        return 0