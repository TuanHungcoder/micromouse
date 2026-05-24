from machine import Pin, ADC
import time
import config

class SensorArray:
    def __init__(self):
        # Chân điều khiển cụm LED hồng ngoại phát (IR Emitter)
        self.ir_en = Pin(config.IR_EN_PIN, Pin.OUT)
        self.ir_en.value(0) # Tắt LED lúc khởi động để tiết kiệm pin
        
        # Khởi tạo 4 kênh ADC (Analog to Digital) theo thứ tự chuẩn
        # Quy ước mảng adcs: [Trái, Trước-Trái, Trước-Phải, Phải]
        sensor_pins = [
            config.SENSOR_L_PIN,
            config.SENSOR_FL_PIN,
            config.SENSOR_FR_PIN,
            config.SENSOR_R_PIN
        ]
        
        self.adcs = []
        for pin_num in sensor_pins:
            adc = ADC(Pin(pin_num))
            adc.atten(ADC.ATTN_11DB) # Cấu hình đọc dải điện áp 0-3.3V (Giá trị từ 0 - 4095)
            self.adcs.append(adc)
            
        # Mảng lưu giá trị sạch sau khi xử lý nhiễu
        # Quy ước: [Trái, Trước-Trái, Trước-Phải, Phải]
        self.values = [0, 0, 0, 0]
        
        # Biến lưu trữ giá trị quét động (đã qua bộ lọc Gaussian) khi xe di chuyển
        self.scanned_left = None
        self.scanned_right = None

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
        time.sleep_us(800) # Tăng từ 60us lên 800us để bóng thu quang (Phototransistor) có đủ thời gian mở
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
        # NHÂN 2 SAI SỐ: Vì khi có 2 tường, sai số = (L + d) - (R - d) = 2d. 
        # Nhưng khi có 1 tường, sai số chỉ là (L + d) - TARGET = 1d. 
        # Phải nhân 2 để lực hút về tường mạnh ngang với lúc có 2 tường.
        elif left_val > THRESHOLD:
            return (left_val - TARGET) * 2
            
        # Trường hợp 3: Chỉ bám được tường phải
        elif right_val > THRESHOLD:
            return (TARGET - right_val) * 2
            
        # Trường hợp 4: Đường trống, ngã tư -> Không có sai số
        return 0

    def check_walls_for_maze(self):
        """Chuyển đổi giá trị Analog sang trạng thái True/False cho thuật toán Maze"""
        SIDE_TH = config.SIDE_WALL_THRESHOLD
        FRONT_TH = config.FRONT_WALL_THRESHOLD
        
        # Ưu tiên dùng dữ liệu quét động (Gaussian) nếu có
        if self.scanned_left is not None:
            has_left = self.scanned_left > SIDE_TH
            self.values[0] = int(self.scanned_left) # Cập nhật cho UI và Log
            self.scanned_left = None  # Xóa sau khi dùng để không bị lặp lại ở ô tĩnh tiếp theo
        else:
            has_left = self.values[0] > SIDE_TH
            
        if self.scanned_right is not None:
            has_right = self.scanned_right > SIDE_TH
            self.values[3] = int(self.scanned_right) # Cập nhật cho UI và Log
            self.scanned_right = None
        else:
            has_right = self.values[3] > SIDE_TH
        
        FL = self.values[1]
        FR = self.values[2]
        
        # CHỐNG NHẬN NHẦM LỐI ĐI THÀNH TƯỜNG TRƯỚC:
        # Vì mắt trước là mắt chéo, nếu đường trống nhưng xe đi hơi lệch, 1 mắt chéo sẽ đập 
        # vào tường hông (trả về > 800), mắt kia chiếu ra khoảng không (trả về < 100).
        # Trung bình cộng vẫn > 500 khiến xe tưởng có tường trước.
        # Khắc phục: Yêu cầu CẢ 2 mắt chéo đều phải thấy vật cản (> 250) mới xác nhận là tường trước.
        front_avg = (FL + FR) / 2
        has_front = (FL > 250 and FR > 250) and (front_avg > FRONT_TH)
        
        return has_left, has_front, has_right