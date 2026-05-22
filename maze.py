# ============================================================
# Micromouse Maze Solver — Flood Fill Algorithm
# Kích thước mê cung tiêu chuẩn 16x16
# ============================================================

from collections import deque

MAZE_SIZE = 16

# Quy ước hướng bằng Bitmask (tiết kiệm RAM)
# Dùng số mũ của 2 để cộng dồn không bị trùng
NORTH = 1
EAST  = 2
SOUTH = 4
WEST  = 8

# Bảng tra nhanh: hướng → (dx, dy) → hướng đối diện
_DIR_META = {
    NORTH: ( 0,  1, SOUTH),
    EAST:  ( 1,  0, WEST ),
    SOUTH: ( 0, -1, NORTH),
    WEST:  (-1,  0, EAST ),
}


class MazeSolver:
    def __init__(self):
        # Mê cung 16x16 lưu khoảng cách tới đích
        self.distances = [[0] * MAZE_SIZE for _ in range(MAZE_SIZE)]
        # Mê cung 16x16 lưu thông tin tường (bitmask)
        self.walls     = [[0] * MAZE_SIZE for _ in range(MAZE_SIZE)]

        # Tọa độ đích (4 ô trung tâm: 7,7 → 8,8)
        self.target_x = 7
        self.target_y = 7

        # Vị trí và hướng xuất phát (góc dưới trái, mặt hướng Bắc)
        self.x       = 0
        self.y       = 0
        self.heading = NORTH

        self._init_boundary_walls()
        self.init_distances()

    # ------------------------------------------------------------------ #
    #  KHỞI TẠO                                                           #
    # ------------------------------------------------------------------ #

    def _init_boundary_walls(self):
        """Đặt tường bao quanh biên ngoài mê cung (luôn tồn tại)."""
        for i in range(MAZE_SIZE):
            self.walls[0][i]           |= SOUTH   # cạnh dưới
            self.walls[MAZE_SIZE-1][i] |= NORTH   # cạnh trên
            self.walls[i][0]           |= WEST    # cạnh trái
            self.walls[i][MAZE_SIZE-1] |= EAST    # cạnh phải

    def init_distances(self):
        """
        Khởi tạo khoảng cách ban đầu bằng Manhattan distance khi chưa biết tường.
        Công thức: d = |x - target_x| + |y - target_y|
        Flood fill sẽ tinh chỉnh lại sau mỗi lần phát hiện tường mới.
        """
        for y in range(MAZE_SIZE):
            for x in range(MAZE_SIZE):
                self.distances[y][x] = abs(x - self.target_x) + abs(y - self.target_y)

    # ------------------------------------------------------------------ #
    #  THAO TÁC TƯỜNG                                                     #
    # ------------------------------------------------------------------ #

    def has_wall(self, x, y, direction):
        """Kiểm tra ô (x, y) có tường ở hướng direction không (Bitwise AND)."""
        return bool(self.walls[y][x] & direction)

    def set_wall(self, x, y, direction):
        """
        Ghi nhận tường tại ô (x, y) hướng direction.
        Tự động cập nhật ô hàng xóm (tường có 2 mặt).
        """
        if not (0 <= x < MAZE_SIZE and 0 <= y < MAZE_SIZE):
            return

        dx, dy, opposite = _DIR_META[direction]
        self.walls[y][x] |= direction           # mặt này

        nx, ny = x + dx, y + dy
        if 0 <= nx < MAZE_SIZE and 0 <= ny < MAZE_SIZE:
            self.walls[ny][nx] |= opposite      # mặt kia của cùng bức tường

    # ------------------------------------------------------------------ #
    #  FLOOD FILL                                                          #
    # ------------------------------------------------------------------ #

    def flood_fill_update(self):
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
