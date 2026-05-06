from machine import Pin, ADC
import time
import config

class SensorArray:
    def __init__(self):
        # Chân điều khiển cụm LED hồng ngoại phát (IR Emitter)
        self.ir_en = Pin(config.IR_EN_PIN, Pin.OUT)
        self.ir_en.value(0) # Tắt LED lúc khởi động để tiết kiệm pin
        
        # Khởi tạo 4 kênh ADC (Analog to Digital)
        self.adcs = []
        for pin_num in config.SENSOR_PINS:
            adc = ADC(Pin(pin_num))
            adc.atten(ADC.ATTN_11DB) # Cấu hình đọc dải điện áp 0-3.3V (Giá trị từ 0 - 4095)
            self.adcs.append(adc)
            
        # Mảng lưu giá trị sạch sau khi xử lý nhiễu
        # Quy ước: [Trái, Trước-Trái, Trước-Phải, Phải]
        self.values = [0, 0, 0, 0]

    def read_sensors(self):
        """Thuật toán đọc cảm biến và khử nhiễu ánh sáng môi trường"""
        ambient = [0, 0, 0, 0]
        raw = [0, 0, 0, 0]

        # 1. Đọc ánh sáng môi trường (Lúc LED phát đang TẮT)
        self.ir_en.value(0)
        time.sleep_us(50) # Đợi ADC ổn định
        for i in range(4): 
            ambient[i] = self.adcs[i].read()

        # 2. Đọc mức sáng thực tế (Lúc BẬT LED phát)
        self.ir_en.value(1)
        time.sleep_us(60) # Chờ LED sáng hết công suất
        for i in range(4): 
            raw[i] = self.adcs[i].read()
        self.ir_en.value(0) # Tắt ngay lập tức để tránh nóng bóng LED

        # 3. Lọc nhiễu: Giá trị thực = Ánh sáng phản xạ - Ánh sáng môi trường
        for i in range(4):
            val = raw[i] - ambient[i]
            self.values[i] = max(0, val) # Dùng max(0) để tránh ra số âm do sai số

    def get_steering_error(self):
        """Tính toán sai số (Error) để đưa vào bộ PID bám tường"""
        left_val = self.values[0]
        right_val = self.values[3]
        
        # Lấy ngưỡng đo từ file config
        THRESHOLD = config.SIDE_WALL_THRESHOLD 
        TARGET = config.TARGET_WALL_VAL # Giá trị kỳ vọng khi xe đi chính giữa
        
        # Trường hợp 1: Có tường ở cả 2 bên (Tín hiệu tốt nhất)
        if left_val > THRESHOLD and right_val > THRESHOLD: 
            return left_val - right_val # Lấy hiệu số làm độ lệch
            
        # Trường hợp 2: Chỉ bám được tường trái
        elif left_val > THRESHOLD:
            return left_val - TARGET
            
        # Trường hợp 3: Chỉ bám được tường phải
        elif right_val > THRESHOLD:
            return TARGET - right_val
            
        # Trường hợp 4: Đường trống, ngã tư -> Không có sai số
        return 0

    def check_walls_for_maze(self):
        """Chuyển đổi giá trị Analog sang trạng thái True/False cho thuật toán Maze"""
        SIDE_TH = config.SIDE_WALL_THRESHOLD
        FRONT_TH = config.FRONT_WALL_THRESHOLD
        
        has_left = self.values[0] > SIDE_TH
        has_right = self.values[3] > SIDE_TH
        
        # Tường phía trước dùng trung bình cộng của 2 mắt cảm biến chéo
        front_avg = (self.values[1] + self.values[2]) / 2
        has_front = front_avg > FRONT_TH
        
        return has_left, has_front, has_right