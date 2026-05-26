"""
Script cho xe chạy thẳng liên tục với PID bám tường,
ghi lại giá trị cảm biến và vị trí vào file text để phân tích.

Cách dùng:
  1. Đặt xe vào mê cung
  2. Chạy script: import data_logger; data_logger.main()
  3. Xe sẽ tự chạy sau 3 giây
  4. Bấm Ctrl+C để dừng
  5. Tải file "sensor_data.csv" về máy tính để phân tích
"""
import time
import math
import config
from sensors import SensorArray
from encoders import SystemEncoders
from motors import MotorController
from pid import PID

# Tần suất ghi log (mỗi bao nhiêu ms ghi 1 dòng)
LOG_INTERVAL_MS = 50

def main():
    print("==============================================")
    print("  CHẠY LIÊN TỤC + GHI LOG CẢM BIẾN & VỊ TRÍ")
    print("==============================================")
    
    # Khởi tạo phần cứng
    sensors = SensorArray()
    encoders = SystemEncoders()
    motors = MotorController()
    wall_pid = PID(kp=config.KP, ki=config.KI, kd=config.KD)
    
    # Thông số chuyển đổi encoder -> mm
    wheel_circumference = config.WHEEL_DIAMETER * math.pi  # ~106.8mm
    mm_per_tick = wheel_circumference / config.TICKS_PER_REV  # ~0.0763 mm/tick
    
    # Tạo file log mới với header
    filename = "sensor_data.csv"
    with open(filename, "w") as f:
        f.write("time_ms,dist_mm,enc_L,enc_R,sen_L,sen_FL,sen_FR,sen_R,error,correction,has_L,has_F,has_R\n")
    
    print(f">>> File log: {filename}")
    print(f">>> Tốc độ: {config.BASE_SPEED}%")
    print(f">>> Log mỗi {LOG_INTERVAL_MS}ms")
    print(">>> Xe sẽ chạy sau 3 giây... Đặt xe vào vị trí!")
    time.sleep(3)
    
    encoders.reset_all()
    wall_pid.reset()
    
    start_time = time.ticks_ms()
    last_time = start_time
    last_log_time = start_time
    line_count = 0
    
    try:
        while True:
            current_time = time.ticks_ms()
            dt = time.ticks_diff(current_time, last_time) / 1000.0
            if dt <= 0:
                dt = 0.001
            last_time = current_time
            
            # Đọc encoder
            enc_l = encoders.left.get_ticks()
            enc_r = encoders.right.get_ticks()
            avg_ticks = (enc_l + enc_r) / 2.0
            dist_mm = avg_ticks * mm_per_tick
            
            # Đọc cảm biến
            sensors.read_sensors()
            has_left, has_front, has_right = sensors.check_walls_for_maze()
            
            # Tính PID
            error = sensors.get_steering_error()
            correction = wall_pid.compute(error, dt)
            
            # Điều khiển motor
            left_speed = config.BASE_SPEED + correction
            right_speed = config.BASE_SPEED - correction
            motors.drive(left_speed, right_speed)
            
            # Ghi log theo tần suất cài đặt
            elapsed_since_log = time.ticks_diff(current_time, last_log_time)
            if elapsed_since_log >= LOG_INTERVAL_MS:
                elapsed_ms = time.ticks_diff(current_time, start_time)
                
                try:
                    with open(filename, "a") as f:
                        f.write(f"{elapsed_ms},{dist_mm:.1f},{enc_l},{enc_r},"
                                f"{sensors.values[0]},{sensors.values[1]},"
                                f"{sensors.values[2]},{sensors.values[3]},"
                                f"{error:.0f},{correction:.2f},"
                                f"{int(has_left)},{int(has_front)},{int(has_right)}\n")
                    line_count += 1
                except:
                    pass  # Bỏ qua lỗi ghi file để không làm gián đoạn xe
                
                last_log_time = current_time
                
                # In ra console mỗi 20 dòng (~1 giây) để theo dõi
                if line_count % 20 == 0:
                    print(f"[{elapsed_ms/1000:.1f}s] dist={dist_mm:.0f}mm  "
                          f"L={sensors.values[0]} FL={sensors.values[1]} "
                          f"FR={sensors.values[2]} R={sensors.values[3]}  "
                          f"err={error:.0f}")
            
            time.sleep_ms(10)
            
    except KeyboardInterrupt:
        motors.stop()
        elapsed_ms = time.ticks_diff(time.ticks_ms(), start_time)
        print(f"\n>>> Đã dừng xe!")
        print(f">>> Thời gian chạy: {elapsed_ms/1000:.1f} giây")
        print(f">>> Quãng đường: {dist_mm:.0f} mm")
        print(f">>> Đã ghi {line_count} dòng vào '{filename}'")
        print(f">>> Dùng mpremote để tải file: mpremote cp :{filename} .")

if __name__ == "__main__":
    main()
