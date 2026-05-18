from machine import Timer
import config
from sensors import SensorArray
from motors import RobotDrive
from pid import PID
import micropython

micropython.alloc_emergency_exception_buf(100)

sensors = SensorArray()
drive = RobotDrive()
steer_pid = PID(config.KP_STEER, config.KI_STEER, config.KD_STEER)

@micropython.native
def control_loop(timer):
    # 1. Cập nhật mảng giá trị cảm biến
    sensors.read_sensors()
    
    # 2. Lấy sai số hướng đi
    error = sensors.get_steering_error()

    # 3. Tính toán góc lái (Steer)
    steer_correction = steer_pid.compute(error, dt=0.01)

    # 4. Mix tốc độ
    # Lệch sang trái (error dương) -> bẻ lái sang phải (bánh trái nhanh, bánh phải chậm)
    left_speed = config.BASE_SPEED + steer_correction
    right_speed = config.BASE_SPEED - steer_correction

    # 5. Xuất PWM
    drive.drive(left_speed, right_speed)

print("Micromouse Wall Following Started...")
timer = Timer(0)
timer.init(period=10, mode=Timer.PERIODIC, callback=control_loop)

try:
    while True:
        # Ở đây sau này bạn sẽ viết logic nhận diện ngã tư, đếm ô Encoder
        pass
except KeyboardInterrupt:
    timer.deinit()
    drive.drive(0, 0)