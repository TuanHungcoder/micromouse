# Mặc định kích thước mê cung Micromouse tiêu chuẩn là 16x16, sửa thành 4x4
MAZE_SIZE = 4

# Quy ước hướng bằng Bitmask (Để tiết kiệm RAM)
# Dùng các số mũ của 2 (1, 2, 4, 8) để có thể cộng dồn mà không bị trùng
NORTH = 1
EAST  = 2
SOUTH = 4
WEST  = 8

class MazeSolver:
    def __init__(self):
        # Mê cung 16x16 lưu khoảng cách tới đích
        self.distances = [[0 for _ in range(MAZE_SIZE)] for _ in range(MAZE_SIZE)]
        # Mê cung 16x16 lưu thông tin tường
        self.walls = [[0 for _ in range(MAZE_SIZE)] for _ in range(MAZE_SIZE)]
        # Theo dõi các ô đã được đi qua
        self.visited = [[False for _ in range(MAZE_SIZE)] for _ in range(MAZE_SIZE)]
        
        # Tọa độ đích (Giữa mê cung)
        self.target_x = 2
        self.target_y = 2
        
        # Tọa độ và hướng hiện tại của xe (Mặc định xuất phát ở góc dưới trái)
        self.x = 0
        self.y = 0
        self.heading = NORTH
        
        # Biến trạng thái để đợi lệnh Start từ web
        self.started = False
        self.is_first_move = True
        
        self.init_distances()
        self.init_boundary_walls()

    def init_boundary_walls(self):
        """Đã tắt: Không vẽ sẵn tường biên, bắt buộc xe phải dùng cảm biến để tự nhận diện."""
        pass

    def init_distances(self):
        """
        Khởi tạo khoảng cách ban đầu (Manhattan distance) khi chưa biết tường.
        Công thức: d = |x - target_x| + |y - target_y|
        """
        for y in range(MAZE_SIZE):
            for x in range(MAZE_SIZE):
                self.distances[y][x] = abs(x - self.target_x) + abs(y - self.target_y)

    def reset_maze(self):
        """Xóa toàn bộ dữ liệu tường và đường đi để chạy lại từ đầu"""
        self.walls = [[0 for _ in range(MAZE_SIZE)] for _ in range(MAZE_SIZE)]
        self.visited = [[False for _ in range(MAZE_SIZE)] for _ in range(MAZE_SIZE)]
        self.x = 0
        self.y = 0
        self.heading = NORTH
        self.started = False
        self.is_first_move = True
        self.init_distances()
        self.init_boundary_walls()

    def has_wall(self, x, y, direction):
        """Kiểm tra xem ô (x, y) có tường ở hướng 'direction' không"""
        # Phép toán thao tác bit (Bitwise AND)
        return (self.walls[y][x] & direction) != 0

    def set_wall(self, x, y, direction):
        """Ghi nhận có tường và cập nhật luôn cho cả ô hàng xóm"""
        if x < 0 or x >= MAZE_SIZE or y < 0 or y >= MAZE_SIZE:
            return
            
        # Thêm tường cho ô hiện tại (Phép toán Bitwise OR)
        self.walls[y][x] |= direction
        
        # Tường có 2 mặt, phải thêm cho cả ô hàng xóm
        if direction == NORTH and y < MAZE_SIZE - 1:
            self.walls[y + 1][x] |= SOUTH
        elif direction == SOUTH and y > 0:
            self.walls[y - 1][x] |= NORTH
        elif direction == EAST and x < MAZE_SIZE - 1:
            self.walls[y][x + 1] |= WEST
        elif direction == WEST and x > 0:
            self.walls[y][x - 1] |= EAST

    def mark_visited(self, x, y):
        """Đánh dấu ô đã đi qua"""
        if 0 <= x < MAZE_SIZE and 0 <= y < MAZE_SIZE:
            self.visited[y][x] = True

    def is_fully_mapped(self):
        """Kiểm tra xem toàn bộ các ô đã được khám phá chưa"""
        for y in range(MAZE_SIZE):
            for x in range(MAZE_SIZE):
                if not self.visited[y][x]:
                    return False
        return True

    def get_best_move(self):
        """Tìm ô hàng xóm có khoảng cách (distance) nhỏ nhất để đi tới.
        Nếu có nhiều ô cùng khoảng cách min, ƯU TIÊN ĐI THẲNG để hạn chế rẽ."""
        min_dist = 255
        best_dirs = []
        
        # Danh sách các hướng có thể đi (N, E, S, W) và độ dời (dx, dy)
        neighbors = [
            (NORTH, 0, 1),
            (EAST, 1, 0),
            (SOUTH, 0, -1),
            (WEST, -1, 0)
        ]
        
        for dir_val, dx, dy in neighbors:
            nx, ny = self.x + dx, self.y + dy
            
            # Nếu tọa độ hợp lệ và KHÔNG có tường cản
            if 0 <= nx < MAZE_SIZE and 0 <= ny < MAZE_SIZE:
                if not self.has_wall(self.x, self.y, dir_val):
                    dist = self.distances[ny][nx]
                    # Nếu ô này gần đích hơn
                    if dist < min_dist:
                        min_dist = dist
                        best_dirs = [dir_val]
                    # Nếu khoảng cách bằng với min hiện tại
                    elif dist == min_dist:
                        best_dirs.append(dir_val)
                        
        # TRÌNH TỰ ƯU TIÊN: Đi thẳng > Rẽ phải > Rẽ trái > Quay đầu
        if self.heading in best_dirs:
            return self.heading
            
        right_dir = EAST if self.heading == NORTH else SOUTH if self.heading == EAST else WEST if self.heading == SOUTH else NORTH
        if right_dir in best_dirs:
            return right_dir
            
        left_dir = WEST if self.heading == NORTH else NORTH if self.heading == EAST else EAST if self.heading == SOUTH else SOUTH
        if left_dir in best_dirs:
            return left_dir
            
        if len(best_dirs) > 0:
            return best_dirs[0]
            
        return self.heading

    def flood_fill_update(self):
        """
        Thuật toán Flood Fill (Breadth-First Search) để tính lại khoảng cách 
        từ tất cả các ô đến đích dựa trên thông tin tường đã biết.
        """
        # Reset toàn bộ khoảng cách về 255 (vô cực)
        for y in range(MAZE_SIZE):
            for x in range(MAZE_SIZE):
                self.distances[y][x] = 255
                
        # Khởi tạo Queue với tất cả các ô CHƯA KHÁM PHÁ (Đích đến)
        queue = []
        for y in range(MAZE_SIZE):
            for x in range(MAZE_SIZE):
                if not self.visited[y][x]:
                    self.distances[y][x] = 0
                    queue.append((x, y))
                    
        # Nếu đã đi hết các ô, không cần chạy lan tỏa nữa
        if not queue:
            return
        
        
        # Các hướng di chuyển
        neighbors = [
            (NORTH, 0, 1),
            (EAST, 1, 0),
            (SOUTH, 0, -1),
            (WEST, -1, 0)
        ]
        
        # Bắt đầu duyệt Queue
        while len(queue) > 0:
            cx, cy = queue.pop(0)
            
            # Kiểm tra 4 ô hàng xóm
            for dir_val, dx, dy in neighbors:
                nx, ny = cx + dx, cy + dy
                
                # Nếu tọa độ hợp lệ và KHÔNG có tường cản giữa ô hiện tại và ô hàng xóm
                if 0 <= nx < MAZE_SIZE and 0 <= ny < MAZE_SIZE:
                    if not self.has_wall(cx, cy, dir_val):
                        # Nếu ô hàng xóm chưa được duyệt
                        if self.distances[ny][nx] == 255:
                            self.distances[ny][nx] = self.distances[cy][cx] + 1
                            queue.append((nx, ny))

    def get_relative_direction(self, current_heading, target_heading):
        """Tính toán hướng rẽ tương đối từ hướng tuyệt đối"""
        if target_heading == current_heading: return 0 # Đi thẳng
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

    def get_shortest_path_actions(self, start_x, start_y, start_heading, target_x, target_y):
        """Tính toán chuỗi hành động chạy liên tục từ điểm xuất phát đến đích"""
        # Tạm thời đổi target để flood fill chạy đúng
        original_target_x, original_target_y = self.target_x, self.target_y
        self.target_x, self.target_y = target_x, target_y
        self.flood_fill_update()
        
        actions = []
        cx, cy, cheading = start_x, start_y, start_heading
        
        while (cx, cy) != (target_x, target_y):
            # Tính hướng đi tốt nhất tại ô (cx, cy)
            temp_x, temp_y, temp_heading = self.x, self.y, self.heading
            self.x, self.y, self.heading = cx, cy, cheading
            best_heading = self.get_best_move()
            self.x, self.y, self.heading = temp_x, temp_y, temp_heading
            
            # Tính hướng rẽ
            rel_dir = self.get_relative_direction(cheading, best_heading)
            
            if rel_dir == 0:
                # Đang đi thẳng
                if len(actions) > 0 and isinstance(actions[-1], int):
                    actions[-1] += 1
                else:
                    actions.append(1)
            else:
                # Rẽ (R: Right, L: Left, U: U-turn)
                if rel_dir == 1: actions.append('R')
                elif rel_dir == -1: actions.append('L')
                elif rel_dir == 2: actions.append('U')
                
                # Sau khi rẽ thì tiến 1 ô (Tâm của ô tiếp theo)
                actions.append(1)
                
            cheading = best_heading
            if cheading == NORTH: cy += 1
            elif cheading == SOUTH: cy -= 1
            elif cheading == EAST: cx += 1
            elif cheading == WEST: cx -= 1
            
            if len(actions) > 100: break # An toàn
                
        # Phục hồi target cũ
        self.target_x, self.target_y = original_target_x, original_target_y
        self.flood_fill_update()
        
        return actions