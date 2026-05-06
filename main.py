import time
import config
from sensors import SensorArray
from encoders import SystemEncoders
from motors import MotorController
from pid import PID
from maze import MazeSolver

def setup():
    print("Đang khởi động hệ thống Micromouse...")
    # Khởi tạo các module
    sensors = SensorArray()
    encoders = SystemEncoders()
    motors = MotorController()
    
    # Bộ PID (Thông số này cần bạn chỉnh lại lúc chạy thực tế)
    wall_pid = PID(kp=1.5, ki=0.0, kd=0.5)
    maze = MazeSolver()
    
    return sensors, encoders, motors, wall_pid, maze

def main():
    sensors, encoders, motors, wall_pid, maze = setup()
    
    print("Đã sẵn sàng! Rút tay ra trong 3 giây...")
    time.sleep(3)
    
    # Biến theo dõi thời gian cho PID
    last_time = time.ticks_ms()

    try:
        while True:
            # Tính thời gian trôi qua (dt) cho hàm PID
            current_time = time.ticks_ms()
            dt = time.ticks_diff(current_time, last_time) / 1000.0 # Đổi ra giây
            
            # Tránh chia cho 0 nếu vòng lặp chạy quá nhanh
            if dt <= 0:
                dt = 0.001 
            last_time = current_time

            # 1. Đọc mắt cảm biến
            sensors.read_sensors()
            has_left, has_front, has_right = sensors.check_walls_for_maze()
            
            # 2. Xử lý vật cản phía trước
            if has_front and (sensors.values[1] + sensors.values[2] > 2000):
                # Nếu đâm tường -> Dừng khẩn cấp
                motors.stop()
                print("Có tường phía trước! Đang tính toán quay đầu...")
                # Tương lai sẽ gọi hàm quay xe ở đây
                time.sleep(1) 
                continue

            # 3. Tính toán giữ thăng bằng (PID)
            error = sensors.get_steering_error()
            correction = wall_pid.compute(error, dt)

            # 4. Truyền lệnh xuống Motor
            # Base speed là tốc độ đi thẳng mặc định (ví dụ: 40%)
            left_speed = config.BASE_SPEED + correction
            right_speed = config.BASE_SPEED - correction
            
            motors.drive(left_speed, right_speed)

            # Nghỉ 10ms để giải phóng CPU (Tạo chu kỳ vòng lặp ổn định)
            time.sleep_ms(10)
            
    except KeyboardInterrupt:
        # Nhấn Ctrl+C trên Pymakr/Thonny sẽ nhảy vào đây
        motors.stop()
        print("Đã dừng khẩn cấp!")

if __name__ == "__main__":
    main()