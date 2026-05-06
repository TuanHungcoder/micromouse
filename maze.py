# Mặc định kích thước mê cung Micromouse tiêu chuẩn là 16x16
MAZE_SIZE = 16

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
        
        # Tọa độ đích (Giữa mê cung)
        self.target_x = 7
        self.target_y = 7
        
        # Tọa độ và hướng hiện tại của xe (Mặc định xuất phát ở góc dưới trái)
        self.x = 0
        self.y = 0
        self.heading = NORTH
        
        self.init_distances()

    def init_distances(self):
        """
        Khởi tạo khoảng cách ban đầu (Manhattan distance) khi chưa biết tường.
        Công thức: d = |x - target_x| + |y - target_y|
        """
        for y in range(MAZE_SIZE):
            for x in range(MAZE_SIZE):
                self.distances[y][x] = abs(x - self.target_x) + abs(y - self.target_y)

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

    def get_best_move(self):
        """Tìm ô hàng xóm có khoảng cách (distance) nhỏ nhất để đi tới"""
        min_dist = 255 # Khởi tạo một số thật lớn
        best_dir = self.heading # Mặc định giữ nguyên hướng
        
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
                    # Nếu ô này gần đích hơn
                    if self.distances[ny][nx] < min_dist:
                        min_dist = self.distances[ny][nx]
                        best_dir = dir_val
                        
        return best_dir

    def flood_fill_update(self):
        """
        Đây là linh hồn của thuật toán. Khi phát hiện ngõ cụt hoặc đường đi dài hơn dự kiến,
        hàm này sẽ tính toán lại toàn bộ bản đồ độ cao. (Sẽ viết phức tạp hơn sau).
        """
        pass # Tạm thời để trống để bạn ghép nối cảm biến trước