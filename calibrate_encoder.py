import time
from encoders import SystemEncoders

def calibrate():
    print("=====================================================")
    print("         CHƯƠNG TRÌNH ĐO XUNG ENCODER THỰC TẾ        ")
    print("=====================================================")
    print("1. Hãy lấy bút dạ hoặc băng dính đánh dấu 1 vạch trên BÁNH XE.")
    print("2. Đặt xe xuống đất hoặc đánh dấu 1 mốc cố định trên thân xe.")
    print("3. Dùng tay quay BÁNH XE đúng 1 vòng tròn (360 độ).")
    print("4. Đọc số XUNG hiện ra trên màn hình. Đó chính là TICKS_PER_REV của bạn!")
    print("Bấm Ctrl+C để thoát.")
    print("-----------------------------------------------------")
    
    encoders = SystemEncoders()
    encoders.reset_all()
    
    try:
        while True:
            left = abs(encoders.left.get_ticks())
            right = abs(encoders.right.get_ticks())
            print(f"XUNG TRÁI: {left}  |  XUNG PHẢI: {right}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nĐã kết thúc đo.")

if __name__ == "__main__":
    calibrate()
