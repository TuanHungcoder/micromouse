import network
import socket
import time
import config
import json

HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta charset="UTF-8">
    <title>Micromouse Controller</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --text-color: #f8fafc;
            --cell-bg: #1e293b;
            --wall-color: #ef4444;
            --robot-color: #3b82f6;
            --target-color: #10b981;
            --btn-bg: #334155;
            --btn-hover: #475569;
        }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            text-align: center; 
            margin: 0;
            padding: 20px;
            background-color: var(--bg-color); 
            color: var(--text-color);
        }
        h2 { 
            background: linear-gradient(90deg, #3b82f6, #10b981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 30px;
        }
        
        /* Maze Grid */
        #maze-container {
            display: inline-block;
            background-color: var(--cell-bg);
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            margin-bottom: 30px;
        }
        .maze-row {
            display: flex;
        }
        .maze-cell {
            width: 50px;
            height: 50px;
            box-sizing: border-box;
            border: 1px dashed #334155;
            position: relative;
            background-color: #0f172a;
            transition: all 0.3s ease;
        }
        .wall-n { border-top: 4px solid var(--wall-color) !important; }
        .wall-e { border-right: 4px solid var(--wall-color) !important; }
        .wall-s { border-bottom: 4px solid var(--wall-color) !important; }
        .wall-w { border-left: 4px solid var(--wall-color) !important; }
        
        .visited-cell {
            background-color: #1e293b !important;
        }
        
        .robot {
            position: absolute;
            top: 10px;
            left: 10px;
            width: 30px;
            height: 30px;
            background-color: var(--robot-color);
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 0 10px var(--robot-color);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 10;
        }
        .robot::after {
            content: '';
            width: 0; 
            height: 0; 
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-bottom: 12px solid white;
            position: absolute;
        }
        .heading-1 { transform: rotate(0deg); }   /* North */
        .heading-2 { transform: rotate(90deg); }  /* East */
        .heading-4 { transform: rotate(180deg); } /* South */
        .heading-8 { transform: rotate(270deg); } /* West */
        


        .btn-start {
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            font-weight: bold;
            font-size: 22px;
            padding: 15px 30px;
            border-radius: 50px;
            border: none;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
            cursor: pointer;
            transition: all 0.2s;
            margin-bottom: 25px;
            width: 80%;
            max-width: 300px;
        }
        .btn-start:active { transform: scale(0.95); }

        .btn-reset {
            background: linear-gradient(135deg, #f43f5e, #e11d48);
            color: white;
            font-weight: bold;
            font-size: 18px;
            padding: 12px 25px;
            border-radius: 50px;
            border: none;
            box-shadow: 0 4px 15px rgba(244, 63, 94, 0.4);
            cursor: pointer;
            transition: all 0.2s;
            margin-bottom: 25px;
            width: 80%;
            max-width: 300px;
        }
        .btn-reset:active { transform: scale(0.95); }

        /* Controls */
        .grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; max-width: 250px; margin: 0 auto; }
        .empty { visibility: hidden; }
        .button {
            padding: 20px;
            font-size: 20px;
            cursor: pointer;
            color: #fff;
            background-color: var(--btn-bg);
            border: none;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: all 0.1s;
            user-select: none;
            -webkit-user-select: none;
        }
        .button:active { background-color: var(--btn-hover); transform: scale(0.95); }
        .stop { background-color: #ef4444; }
        .stop:active { background-color: #dc2626; }
        .status { margin-top: 20px; color: #94a3b8; font-size: 14px; }
    </style>
</head>
<body>
    <h2>MICROMOUSE 5x5 LIVE MAP</h2>
    
    <div id="maze-container">
        <!-- Grid will be generated here -->
    </div>
    
    <div>
        <button class="btn-start" onclick="startMaze()">🚀 BẮT ĐẦU CHẠY</button>
        <br>
        <button class="btn-reset" onclick="resetMaze()">🔄 XÓA BẢN ĐỒ</button>
    </div>
    
    <div class="grid">
        <div class="empty"></div>
        <button class="button" onmousedown="sendCmd('forward')" onmouseup="sendCmd('stop')" ontouchstart="sendCmd('forward')" ontouchend="sendCmd('stop')">▲</button>
        <div class="empty"></div>
        
        <button class="button" onmousedown="sendCmd('left')" onmouseup="sendCmd('stop')" ontouchstart="sendCmd('left')" ontouchend="sendCmd('stop')">◄</button>
        <button class="button stop" onclick="sendCmd('stop')">■</button>
        <button class="button" onmousedown="sendCmd('right')" onmouseup="sendCmd('stop')" ontouchstart="sendCmd('right')" ontouchend="sendCmd('stop')">►</button>
        
        <div class="empty"></div>
        <button class="button" onmousedown="sendCmd('backward')" onmouseup="sendCmd('stop')" ontouchstart="sendCmd('backward')" ontouchend="sendCmd('stop')">▼</button>
        <div class="empty"></div>
    </div>
    
    <div class="status" id="statusText">Đang tải bản đồ...</div>
    
    <script>
        const MAZE_SIZE = 5;
        
        function initMaze() {
            const container = document.getElementById('maze-container');
            container.innerHTML = '';
            
            // Vẽ từ trên xuống dưới (y giảm dần theo trục tung trong toán học)
            for(let y = MAZE_SIZE - 1; y >= 0; y--) {
                const row = document.createElement('div');
                row.className = 'maze-row';
                for(let x = 0; x < MAZE_SIZE; x++) {
                    const cell = document.createElement('div');
                    cell.className = 'maze-cell';
                    cell.id = `cell-${x}-${y}`;
                    
                    row.appendChild(cell);
                }
                container.appendChild(row);
            }
        }

        function updateMap() {
            fetch('/map')
                .then(response => response.json())
                .then(data => {
                    // Xóa robot cũ
                    const oldRobot = document.getElementById('robot');
                    if(oldRobot) oldRobot.remove();
                    
                    // Cập nhật tường cho từng ô
                    for(let y = 0; y < MAZE_SIZE; y++) {
                        for(let x = 0; x < MAZE_SIZE; x++) {
                            const cell = document.getElementById(`cell-${x}-${y}`);
                            if(!cell) continue;
                            
                            const val = data.walls[y][x];
                            let classes = ['maze-cell'];
                            if(val & 1) classes.push('wall-n');
                            if(val & 2) classes.push('wall-e');
                            if(val & 4) classes.push('wall-s');
                            if(val & 8) classes.push('wall-w');
                            if(data.visited && data.visited[y][x]) classes.push('visited-cell');
                            
                            // Giữ lại element con (robot)
                            const children = Array.from(cell.children);
                            cell.className = classes.join(' ');
                            children.forEach(c => cell.appendChild(c));
                        }
                    }
                    
                    // Đặt robot mới
                    const currentCell = document.getElementById(`cell-${data.x}-${data.y}`);
                    if(currentCell) {
                        const robot = document.createElement('div');
                        robot.id = 'robot';
                        robot.className = `robot heading-${data.heading}`;
                        currentCell.appendChild(robot);
                    }
                    document.getElementById('statusText').innerText = "Cập nhật thành công!";
                })
                .catch(e => {
                    document.getElementById('statusText').innerText = "Mất kết nối: " + e.message;
                });
        }

        function sendCmd(cmd) {
            document.getElementById('statusText').innerText = "Đang gửi lệnh: " + cmd;
            fetch('/' + cmd).catch(e => console.log(e));
        }

        function startMaze() {
            document.getElementById('statusText').innerText = "Đang bắt đầu giải mã mê cung...";
            fetch('/start').catch(e => console.log(e));
        }

        function resetMaze() {
            if (confirm("Bạn có chắc muốn xóa toàn bộ bản đồ và chạy lại từ đầu không?")) {
                document.getElementById('statusText').innerText = "Đang xóa dữ liệu...";
                fetch('/reset').catch(e => console.log(e));
            }
        }

        // Khởi tạo
        initMaze();
        // Cập nhật map mỗi 500ms
        setInterval(updateMap, 500);
    </script>
</body>
</html>
"""

def setup_ap():
    # Tắt chế độ Station
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    
    # Bật chế độ Access Point
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    
    # Cấu hình tên mạng và mật khẩu
    # authmode=3 tương ứng với WPA2-PSK
    if len(config.WIFI_PASSWORD) >= 8:
        ap.config(essid=config.WIFI_SSID, password=config.WIFI_PASSWORD, authmode=3)
    else:
        ap.config(essid=config.WIFI_SSID, authmode=0) # Mạng không mật khẩu nếu pass quá ngắn
        
    time.sleep(1) # Đợi AP khởi tạo
            
    print('=====================================')
    print('ĐÃ PHÁT WIFI (Chế độ Access Point)!')
    print('Tên WiFi (SSID):', config.WIFI_SSID)
    print('Mật khẩu:', config.WIFI_PASSWORD if len(config.WIFI_PASSWORD) >= 8 else "(Không có)")
    print('IP Address của mạch:', ap.ifconfig()[0])
    print('>>> Hãy dùng điện thoại bắt WiFi này và truy cập: http://' + ap.ifconfig()[0])
    print('=====================================')
    return True

def start_server(motors, maze):
    if not setup_ap():
        print("Web Server không thể khởi động vì lỗi WiFi.")
        return
        
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 80))
    s.listen(5)
    print('Web Server đang chạy trên port 80...')
    
    while True:
        try:
            conn, addr = s.accept()
            request = conn.recv(1024)
            request = str(request)
            
            # Bỏ qua các kết nối rỗng
            if len(request) < 5:
                conn.close()
                continue
                
            # Xử lý API /map
            if request.find('GET /map') == 2:
                data = {
                    "walls": maze.walls,
                    "visited": getattr(maze, "visited", []),
                    "x": maze.x,
                    "y": maze.y,
                    "heading": maze.heading
                }
                response = json.dumps(data)
                
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: application/json\n')
                conn.send('Connection: close\n\n')
                conn.sendall(response)
                conn.close()
                continue
                
            # Xử lý lệnh START
            if request.find('GET /start') == 2:
                maze.started = True
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: text/plain\n')
                conn.send('Connection: close\n\n')
                conn.sendall('Started')
                conn.close()
                continue
                
            # Xử lý lệnh RESET
            if request.find('GET /reset') == 2:
                maze.reset_maze()
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: text/plain\n')
                conn.send('Connection: close\n\n')
                conn.sendall('Reset')
                conn.close()
                continue

            # Phân tích lệnh điều khiển thủ công
            if request.find('GET /forward') == 2:
                motors.drive(config.BASE_SPEED, config.BASE_SPEED)
            elif request.find('GET /backward') == 2:
                motors.drive(-config.BASE_SPEED, -config.BASE_SPEED)
            elif request.find('GET /left') == 2:
                motors.drive(-config.BASE_SPEED, config.BASE_SPEED)
            elif request.find('GET /right') == 2:
                motors.drive(config.BASE_SPEED, -config.BASE_SPEED)
            elif request.find('GET /stop') == 2:
                motors.stop()
                
            # Trả về HTML cho trình duyệt (nếu request là trang chủ)
            if request.find('GET / ') == 2:
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: text/html\n')
                conn.send('Connection: close\n\n')
                conn.sendall(HTML_PAGE)
                
            conn.close()
        except Exception as e:
            try:
                conn.close()
            except:
                pass
