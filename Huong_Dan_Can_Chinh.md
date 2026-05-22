# HƯỚNG DẪN CÂN CHỈNH DỰ ÁN MICROMOUSE TỪ A ĐẾN Z

Việc cân chỉnh (Tuning) là bước BẮT BUỘC để robot có thể chạy ổn định trong mê cung thực tế. 
Vui lòng làm theo đúng thứ tự các bước dưới đây để điều chỉnh các biến trong file `config.py`.

---

## BƯỚC 1: CÂN CHỈNH CẢM BIẾN HỒNG NGOẠI (IR SENSORS)
**Mục đích:** Tìm ngưỡng nhận diện tường và mức tham chiếu chuẩn.
**Thông số cần thay đổi:** `SIDE_WALL_THRESHOLD`, `FRONT_WALL_THRESHOLD`, `TARGET_WALL_VAL`

**Cách làm:**
1. Tạo một file kịch bản tạm thời tên là `test_sensors.py` trên bo mạch ESP32 với nội dung sau:
```python
import time
from sensors import SensorArray

sensors = SensorArray()
while True:
    sensors.read_sensors()
    print(f"Trái: {sensors.values[0]:<5} | TrướcTrái: {sensors.values[1]:<5} | TrướcPhải: {sensors.values[2]:<5} | Phải: {sensors.values[3]:<5}")
    time.sleep_ms(200)
```
2. Chạy file trên trong phần mềm Thonny (hoặc IDE bạn đang dùng) và xem màn hình Terminal/Console.
3. Đặt xe vào chính giữa 1 ô mê cung chuẩn có 2 bức tường ở 2 bên:
   - Ghi lại giá trị của mắt Trái và mắt Phải. Lấy số ở giữa (Trung bình cộng) của chúng điền vào **`TARGET_WALL_VAL`**. (Đây là vạch đích để PID duy trì).
4. Bỏ bức tường bên trái (hoặc phải) ra khỏi mê cung:
   - Quan sát giá trị mắt trái lúc này tụt xuống bao nhiêu.
   - Chọn một con số nằm GIAO GIỮA mức lúc có tường (cao) và mức không có tường (thấp). Điền con số đó vào **`SIDE_WALL_THRESHOLD`**.
5. Đặt một bức tường chắn ngang đầu xe ở khoảng cách khoảng 3-4cm (Đó là khoảng cách lý tưởng để đầu xe có đủ không gian xoay cua):
   - Đọc giá trị trung bình cộng của 2 mắt "Trước Trái" và "Trước Phải".
   - Điền kết quả thu được vào **`FRONT_WALL_THRESHOLD`**.

---

## BƯỚC 2: CÂN CHỈNH KÍCH THƯỚC & ENCODER
**Mục đích:** Giúp xe đi chính xác 1 ô mê cung (chuẩn 180mm) và quay góc tại chỗ chính xác 90 độ.
**Thông số cần thay đổi:** `TICKS_PER_REV`, `WHEEL_DIAMETER`, `WHEEL_DISTANCE`

**Cách làm:**
1. **`WHEEL_DIAMETER` (Đường kính bánh xe):**
   - Dùng thước kẹp (Caliper) đo đường kính của bánh xe (tính cả lốp cao su). Đơn vị là mm (Ví dụ: 34 hoặc 43). Điền vào config.
2. **`TICKS_PER_REV` (Số xung 1 vòng quay của bánh xe):**
   - Bạn cần tra cứu thông số kỹ thuật động cơ. Ví dụ: động cơ có tỉ số truyền 1:34, số xung nam châm là 11 xung/vòng motor. => 1 vòng bánh xe = 34 * 11 = 374 xung.
   - **CỰC KỲ LƯU Ý:** Vì code của bạn dùng `IRQ_RISING | IRQ_FALLING` nên độ phân giải bị nhân đôi. Bạn phải lấy con số tính được nhân thêm cho 2. (Ví dụ 374 * 2 = 748). Điền 748 vào `TICKS_PER_REV`.
3. **`WHEEL_DISTANCE` (Khoảng cách giữa 2 bánh):**
   - Đo khoảng cách từ TÂM bề rộng bánh xe trái đến TÂM bề rộng bánh xe phải (mm). (Đừng đo từ mép ngoài).
   - Chạy thử hàm xoay 90 độ (`navigator.turn_left()`).
   - Nếu xe quay lố qua mốc 90 độ: **Tăng** số `WHEEL_DISTANCE` lên một chút.
   - Nếu xe quay chưa tới mốc 90 độ: **Giảm** số `WHEEL_DISTANCE` đi một chút.

---

## BƯỚC 3: CÂN CHỈNH PID BÁM TƯỜNG (WALL FOLLOWER)
**Mục đích:** Giúp xe chạy thẳng mượt mà ở giữa 2 bức tường, không bị xiên vẹo hay cọ quẹt.
**Thông số cần thay đổi:** `KP`, `KD`, `BASE_SPEED`. (Thường giữ `KI = 0`).

**Cách làm:**
1. Đặt thông số ban đầu an toàn: `KP = 1.0`, `KI = 0.0`, `KD = 0.0`, `BASE_SPEED = 300` (Để tốc độ chậm để dễ quan sát).
2. Viết một lệnh cho xe chạy thẳng dài vô tận trên 1 hành lang thẳng.
3. **Chỉnh khâu `KP` (Proportional):**
   - Tăng dần giá trị `KP` (VD: 3, 5, 10, 15...).
   - Hiện tượng: Khi có `KP`, xe bị lệch sẽ lập tức bẻ lái về tâm. Nhưng nếu KP quá to, xe bẻ lái quá gắt gây ra hiện tượng đánh võng (lắc lư đuôi liên tục giữa 2 bức tường).
   - Hãy dừng tăng khi bạn thấy xe đánh võng nhẹ, không bị mất kiểm soát.
4. **Chỉnh khâu `KD` (Derivative):**
   - Tăng dần `KD` (VD: 0.5, 1, 2, 5).
   - Hiện tượng: Khâu `KD` sẽ "dự đoán" độ đánh võng của đầu xe và hãm nó lại. Xe sẽ dần dần hết lắc lư đuôi và đi thẳng tắp lướt trên đường.
5. **Đẩy cao `BASE_SPEED`:**
   - Sau khi xe đã đi thẳng mượt, bạn có thể tăng dần `BASE_SPEED` lên 400, 500, 600... để xe chạy nhanh hơn.
   - Lưu ý: Chạy càng nhanh thì bạn sẽ phải quay lại tinh chỉnh nhỏ cặp `KP, KD` thêm một chút để duy trì sự mượt mà.
