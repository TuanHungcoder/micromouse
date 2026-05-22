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
        Tính lại toàn bộ bảng distances bằng BFS từ đích ra ngoài.

        Tại sao cần?
          - Manhattan distance ban đầu không biết tường → sai khi gặp vật cản.
          - Mỗi lần robot phát hiện tường mới, một số đường bị chặn,
            khoảng cách thực tế thay đổi → phải tính lại.

        Cách hoạt động (BFS từ đích):
          ┌─────────────────────────────────────┐
          │  Đích = 0                           │
          │  Hàng xóm không bị tường cản = 1   │
          │  Tiếp theo = 2, 3, 4 ...           │
          │  Sóng lan ra, vòng qua tường        │
          └─────────────────────────────────────┘
          Robot chỉ cần luôn bước sang ô có
          distances nhỏ hơn → tự tìm đường tối ưu.

        Độ phức tạp: O(N²) — với N=16 chỉ 256 ô, rất nhanh.
        """

        # ── Bước 1: Reset toàn bảng về "vô cực" ──────────────────────
        # Không thể patch từng ô vì tường mới có thể làm thay đổi
        # khoảng cách của nhiều ô ở xa theo hiệu ứng dây chuyền.
        INF = 255
        for y in range(MAZE_SIZE):
            for x in range(MAZE_SIZE):
                self.distances[y][x] = INF

        # ── Bước 2: Gieo các ô đích vào queue ────────────────────────
        # Đích chuẩn Micromouse: 4 ô trung tâm (7,7)(8,7)(7,8)(8,8)
        # Tất cả cùng = 0, BFS sẽ lan ra đồng thời từ cả 4 ô.
        queue = deque()

        for tx, ty in [
            (self.target_x,     self.target_y    ),
            (self.target_x + 1, self.target_y    ),
            (self.target_x,     self.target_y + 1),
            (self.target_x + 1, self.target_y + 1),
        ]:
            if 0 <= tx < MAZE_SIZE and 0 <= ty < MAZE_SIZE:
                self.distances[ty][tx] = 0
                queue.append((tx, ty))

        # ── Bước 3: BFS lan rộng ─────────────────────────────────────
        while queue:
            cx, cy = queue.popleft()
            next_dist = self.distances[cy][cx] + 1

            for direction, (dx, dy, _) in _DIR_META.items():
                nx, ny = cx + dx, cy + dy

                # Bỏ qua nếu ra ngoài biên
                if not (0 <= nx < MAZE_SIZE and 0 <= ny < MAZE_SIZE):
                    continue

                # Có tường → sóng không lan qua được
                if self.has_wall(cx, cy, direction):
                    continue

                # Chỉ cập nhật ô chưa được tính (còn = INF)
                # → đảm bảo mỗi ô nhận khoảng cách ngắn nhất
                if self.distances[ny][nx] == INF:
                    self.distances[ny][nx] = next_dist
                    queue.append((nx, ny))

    # ------------------------------------------------------------------ #
    #  ĐIỀU HƯỚNG                                                         #
    # ------------------------------------------------------------------ #

    def get_best_move(self):
        """
        Tìm hướng đi tới ô hàng xóm có distances nhỏ nhất.
        Nếu không có hướng nào "xuống dốc" → trigger flood_fill_update() một lần,
        rồi tìm lại (không đệ quy — dùng vòng lặp để tránh stack overflow).
        """
        for attempt in range(2):   # lần 1: tìm bình thường; lần 2: sau flood fill
            min_dist = self.distances[self.y][self.x]
            best_dir = None

            for direction, (dx, dy, _) in _DIR_META.items():
                nx, ny = self.x + dx, self.y + dy
                if not (0 <= nx < MAZE_SIZE and 0 <= ny < MAZE_SIZE):
                    continue
                if self.has_wall(self.x, self.y, direction):
                    continue
                if self.distances[ny][nx] < min_dist:
                    min_dist = self.distances[ny][nx]
                    best_dir = direction

            if best_dir is not None:
                return best_dir

            # Lần 1 thất bại → flood fill rồi thử lại lần 2
            if attempt == 0:
                self.flood_fill_update()

        # Nếu vẫn không tìm được (ô bị cô lập hoàn toàn), giữ nguyên hướng
        return self.heading

    def move(self, direction):
        """Di chuyển robot một bước theo direction."""
        dx, dy, _ = _DIR_META[direction]
        self.x       += dx
        self.y       += dy
        self.heading  = direction

    def is_at_target(self):
        """Kiểm tra robot đã đến vùng đích chưa."""
        return (self.target_x     <= self.x <= self.target_x + 1 and
                self.target_y     <= self.y <= self.target_y + 1)

    # ------------------------------------------------------------------ #
    #  VÒNG LẶP CHÍNH (gọi mỗi chu kỳ từ firmware)                       #
    # ------------------------------------------------------------------ #

    def step(self, sensor_walls: dict):
        """
        Một chu kỳ hoàn chỉnh:
          1. Nhận dữ liệu cảm biến → cập nhật tường
          2. Nếu tường mới làm bản đồ cũ sai → flood fill
          3. Chọn hướng tốt nhất → di chuyển

        Args:
            sensor_walls: dict {NORTH|EAST|SOUTH|WEST: True/False}
                          True = có tường ở hướng đó.
                          Ví dụ từ firmware: {NORTH: False, EAST: True, SOUTH: False, WEST: True}
        """
        # Bước 1: Cập nhật tường từ cảm biến
        walls_changed = False
        for direction, blocked in sensor_walls.items():
            if blocked and not self.has_wall(self.x, self.y, direction):
                self.set_wall(self.x, self.y, direction)
                walls_changed = True

        # Bước 2: Tường mới → distances có thể sai → tính lại
        if walls_changed:
            self.flood_fill_update()

        # Bước 3: Chọn và thực hiện bước đi tốt nhất
        if not self.is_at_target():
            best = self.get_best_move()
            self.move(best)

        return self.is_at_target()

        pass # Tạm thời để trống để bạn ghép nối cảm biến trước
