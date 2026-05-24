import time
import _thread
import config
from sensors import SensorArray
from encoders import SystemEncoders
from motors import MotorController
from pid import PID
from maze import MazeSolver, NORTH, EAST, SOUTH, WEST
from navigation import RobotNavigator

def setup():
    print("Đang khởi động hệ thống Micromouse...")
    sensors = SensorArray()
    encoders = SystemEncoders()
    motors = MotorController()
    
    wall_pid = PID(kp=config.KP, ki=config.KI, kd=config.KD)
    maze = MazeSolver()
    navigator = RobotNavigator(motors, encoders, sensors, wall_pid)
    
    return sensors, encoders, motors, wall_pid, maze, navigator

def get_relative_direction(current_heading, target_heading):
    """Tính toán hướng rẽ tương đối từ hướng tuyệt đối"""
    if target_heading == current_heading:
        return 0 # Đi thẳng
    elif (current_heading == NORTH and target_heading == EAST) or \
         (current_heading == EAST and target_heading == SOUTH) or \
         (current_heading == SOUTH and target_heading == WEST) or \
         (current_heading == WEST and target_heading == NORTH):
        return 1 # Rẽ phải
    elif (current_heading == NORTH and target_heading == WEST) or \
         (current_heading == WEST and target_heading == SOUTH) or \
         (current_heading == SOUTH and target_heading == EAST) or \
         (current_heading == EAST and target_heading == NORTH):
        return -1 # Rẽ trái
    else:
        return 2 # Quay đầu 180 độ

def update_position(x, y, heading):
    """Cập nhật tọa độ theo hướng đi thẳng"""
    if heading == NORTH: return x, y + 1
    elif heading == SOUTH: return x, y - 1
    elif heading == EAST: return x + 1, y
    elif heading == WEST: return x - 1, y
    return x, y

def control_loop(sensors, encoders, motors, wall_pid, maze, navigator):
    if config.AUTO_MODE_ENABLED:
        print("Chế độ: TỰ ĐỘNG (Giải mã mê cung)")
    else:
        print("Chế độ: THỦ CÔNG (Điều khiển qua Web)")
    
    try:
        if not config.AUTO_MODE_ENABLED:
            print(">>> Đợi 3 giây để ổn định mạng WiFi trước khi chạy động cơ...")
            time.sleep(3)
            
        last_time = time.ticks_ms()
        while True:
            current_time = time.ticks_ms()
            dt = time.ticks_diff(current_time, last_time) / 1000.0
            if dt <= 0: dt = 0.001
            last_time = current_time

            if config.AUTO_MODE_ENABLED and not getattr(maze, 'started', False):
                motors.stop()
                print("Đang chờ lệnh START từ giao diện Web...")
                while not getattr(maze, 'started', False):
                    time.sleep(0.5)
                print("Đã nhận lệnh START! Rút tay ra trong 2 giây...")
                time.sleep(2)
                
                last_time = time.ticks_ms() # Reset lại thời gian sau khi chờ
                continue
                
            # Nếu đang ở chế độ thủ công (AUTO_MODE_ENABLED = False)
            # -> Chạy chế độ CHỈNH PID ĐI THẲNG VÔ TẬN
            if not config.AUTO_MODE_ENABLED:
                sensors.read_sensors()
                error = sensors.get_steering_error()
                correction = wall_pid.compute(error, dt)
                
                left_speed = config.BASE_SPEED + correction
                right_speed = config.BASE_SPEED - correction
                
                motors.drive(left_speed, right_speed)
                time.sleep_ms(10)
                continue
                
            # 1. Đọc tường xung quanh khi đang đứng ở tâm ô
            sensors.read_sensors()
            has_left, has_front, has_right = sensors.check_walls_for_maze()
            
            # Lưu lại giá trị cảm biến để hiển thị trên web
            maze.last_sensors = sensors.values[:]
            
            heading = maze.heading
            
            # Tính hướng tuyệt đối của các bức tường so với xe
            front_dir = heading
            right_dir = EAST if heading == NORTH else SOUTH if heading == EAST else WEST if heading == SOUTH else NORTH
            left_dir = WEST if heading == NORTH else NORTH if heading == EAST else EAST if heading == SOUTH else SOUTH
            
            # 2. Cập nhật bản đồ mê cung
            maze.mark_visited(maze.x, maze.y)
            if has_front: maze.set_wall(maze.x, maze.y, front_dir)
            if has_right: maze.set_wall(maze.x, maze.y, right_dir)
            if has_left: maze.set_wall(maze.x, maze.y, left_dir)
            
            # Chạy thuật toán Flood Fill cập nhật khoảng cách tới ô chưa khám phá gần nhất
            maze.flood_fill_update()
            
            # Kiểm tra xem đã khám phá xong chưa (tất cả các ô hoặc không còn ô nào tới được)
            if maze.is_fully_mapped() or maze.distances[maze.y][maze.x] == 255:
                print("===========================")
                print("ĐÃ HOÀN TẤT GIẢI MÃ BẢN ĐỒ! 🗺️")
                print("===========================")
                motors.stop()
                maze.started = False
                continue
                
            # 3. Lấy hướng đi tối ưu từ Flood Fill
            best_heading = maze.get_best_move()
            
            # 4. Xoay xe tại chỗ theo hướng mới
            rel_dir = get_relative_direction(heading, best_heading)
            
            if rel_dir == 1:
                navigator.turn_right()
            elif rel_dir == -1:
                navigator.turn_left()
            elif rel_dir == 2:
                navigator.turn_around()
                
            # 5. Tiến thẳng 1 ô để đến TÂM ô tiếp theo
            navigator.move_straight(config.CELL_SIZE)
            motors.stop() # Dừng xe lại để ô tiếp theo đọc cảm biến tĩnh
            time.sleep_ms(150) # Nghỉ một chút cho xe hết rung lắc
                
            # Cập nhật hướng thực tế của xe sau khi xoay
            maze.heading = best_heading
            
            # Cập nhật tọa độ x, y
            maze.x, maze.y = update_position(maze.x, maze.y, maze.heading)
            
    except KeyboardInterrupt:
        motors.stop()
        print("Đã dừng khẩn cấp!")

def webserver_loop(motors, maze, wall_pid):
    import webserver
    print("[Ngầm] Khởi chạy Web Server...")
    # Chạy HTTP Server, hàm này sẽ block (chạy vô tận) trong luồng này
    webserver.start_server(motors, maze, wall_pid)

def main():
    # Khởi tạo phần cứng 1 lần để dùng chung
    sensors, encoders, motors, wall_pid, maze, navigator = setup()
    
    # Tăng kích thước stack cho luồng Web Server để tránh lỗi Stack Overflow khi xử lý JSON
    try:
        _thread.stack_size(8192)
    except:
        pass
        
    # Khởi động luồng Web Server ở background, truyền đối tượng motors, maze và wall_pid vào
    _thread.start_new_thread(webserver_loop, (motors, maze, wall_pid))
    
    # Chạy luồng điều khiển xe ở luồng chính
    control_loop(sensors, encoders, motors, wall_pid, maze, navigator)

if __name__ == "__main__":
    main()