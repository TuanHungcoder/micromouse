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

        /* Control Panel */
        .control-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 10px;
            max-width: 300px;
            margin: 0 auto 25px auto;
            background-color: var(--cell-bg);
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .control-title {
            grid-column: 1 / 4;
            margin-top: 0;
            color: #f59e0b;
            font-size: 18px;
            margin-bottom: 5px;
        }
        .btn-ctrl {
            background: #334155;
            color: white;
            border: none;
            padding: 15px 0;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: all 0.2s;
        }
        .btn-ctrl:active { transform: scale(0.95); background: #475569; }
        .btn-ctrl.stop { background: #e11d48; }
        .btn-ctrl.up { grid-column: 2; background: #3b82f6;}
        .btn-ctrl.left { grid-column: 1; }
        .btn-ctrl.right { grid-column: 3; }
        .btn-ctrl.down { grid-column: 2; }

        /* PID Tuner */
        .pid-container {
            background-color: var(--cell-bg);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            max-width: 300px;
            margin-left: auto;
            margin-right: auto;
        }
        .pid-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .pid-row label {
            font-weight: bold;
            font-size: 18px;
        }
        .pid-row input {
            width: 80px;
            padding: 5px;
            font-size: 16px;
            border-radius: 5px;
            border: 1px solid #475569;
            background-color: #0f172a;
            color: #fff;
            text-align: center;
        }
        .btn-save-pid {
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            color: white;
            font-weight: bold;
            padding: 8px 20px;
            border-radius: 5px;
            border: none;
            cursor: pointer;
            width: 100%;
            margin-top: 5px;
        }
        .btn-save-pid:active { transform: scale(0.95); }
        .status { margin-top: 20px; color: #94a3b8; font-size: 14px; }
    </style>
</head>
<body>
    <h2>MICROMOUSE 4x4 LIVE MAP</h2>
    
    <div id="maze-container">
        <!-- Grid will be generated here -->
    </div>
    
    <div style="max-width: 300px; margin: 0 auto 25px auto; background: var(--cell-bg); padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <h3 style="margin-top:0; color:#10b981; font-size:16px;">📊 KẾT QUẢ ĐO CẢM BIẾN</h3>
        <div style="display: flex; justify-content: space-between; font-family: monospace; font-size: 15px;">
            <div style="color: #60a5fa; text-align: center;"><b>TRÁI</b><br><span id="s-l">0</span></div>
            <div style="color: #fbbf24; text-align: center;"><b>C-TRÁI</b><br><span id="s-fl">0</span></div>
            <div style="color: #fbbf24; text-align: center;"><b>C-PHẢI</b><br><span id="s-fr">0</span></div>
            <div style="color: #60a5fa; text-align: center;"><b>PHẢI</b><br><span id="s-r">0</span></div>
        </div>
    </div>
    
    <div>
        <button class="btn-start" onclick="startMaze()">🚀 BẮT ĐẦU CHẠY</button>
        <br>
        <button class="btn-reset" onclick="resetMaze()">🔄 XÓA BẢN ĐỒ</button>
    </div>

    <div class="control-grid">
        <h3 class="control-title">ĐIỀU KHIỂN CĂN CHỈNH</h3>
        <div></div>
        <button class="btn-ctrl up" onclick="sendCmd('straight')">↑ Đi 4 Ô</button>
        <div></div>
        <button class="btn-ctrl left" onclick="sendCmd('left')">↰ Quay Trái</button>
        <button class="btn-ctrl stop" onclick="sendCmd('stop')">⏹ Dừng</button>
        <button class="btn-ctrl right" onclick="sendCmd('right')">↱ Quay Phải</button>
        <div></div>
        <button class="btn-ctrl down" onclick="sendCmd('around')">↻ Quay Đầu</button>
        <div></div>
    </div>
    
    <div class="pid-container">
        <h3 style="margin-top:0; color:#3b82f6;">TINH CHỈNH PID</h3>
        <div class="pid-row">
            <label>KP:</label>
            <input type="number" id="inputKP" step="0.5" value="0.0">
        </div>
        <div class="pid-row">
            <label>KD:</label>
            <input type="number" id="inputKD" step="0.5" value="0.0">
        </div>
        <div class="pid-row">
            <label>L_MULT:</label>
            <input type="number" id="inputLMult" step="0.01" value="1.0">
        </div>
        <button class="btn-save-pid" onclick="savePID()">💾 LƯU THÔNG SỐ</button>
    </div>
    
    <div class="status" id="statusText">Đang tải bản đồ...</div>
    
    <script>
        const MAZE_SIZE = 4;
        
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
                    
                    if (data.sensors) {
                        document.getElementById('s-l').innerText = data.sensors[0];
                        document.getElementById('s-fl').innerText = data.sensors[1];
                        document.getElementById('s-fr').innerText = data.sensors[2];
                        document.getElementById('s-r').innerText = data.sensors[3];
                    }
                    
                    document.getElementById('statusText').innerText = "Cập nhật thành công!";
                })
                .catch(e => {
                    document.getElementById('statusText').innerText = "Mất kết nối: " + e.message;
                });
        }

        function loadPID() {
            fetch('/get_pid')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('inputKP').value = data.kp;
                    document.getElementById('inputKD').value = data.kd;
                    if(data.lmult !== undefined) document.getElementById('inputLMult').value = data.lmult;
                })
                .catch(e => console.log(e));
        }

        function savePID() {
            const kp = document.getElementById('inputKP').value;
            const kd = document.getElementById('inputKD').value;
            const lmult = document.getElementById('inputLMult').value;
            document.getElementById('statusText').innerText = "Đang lưu thông số...";
            fetch(`/set_pid?kp=${kp}&kd=${kd}&lmult=${lmult}`)
                .then(r => r.text())
                .then(text => {
                    document.getElementById('statusText').innerText = "Lưu thông số thành công!";
                })
                .catch(e => {
                    document.getElementById('statusText').innerText = "Lỗi khi lưu PID!";
                });
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

        function sendCmd(action) {
            document.getElementById('statusText').innerText = "Đang gửi lệnh...";
            fetch('/cmd?action=' + action)
                .then(r => { document.getElementById('statusText').innerText = "Đã gửi lệnh: " + action; })
                .catch(e => { document.getElementById('statusText').innerText = "Lỗi gửi lệnh!"; });
        }

        // Khởi tạo
        initMaze();
        loadPID();
        // Cập nhật map mỗi 2000ms (2 giây) để tránh quá tải bộ đệm Socket (lỗi TIME_WAIT của ESP32)
        setInterval(updateMap, 2000);
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

def start_server(motors, maze, pid, command_queue=None):
    if not setup_ap():
        print("Web Server không thể khởi động vì lỗi WiFi.")
        return
        
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 80))
    s.listen(5)
    print('Web Server đang chạy trên port 80...')
    
    import gc
    
    while True:
        try:
            # Thu gom rác bộ nhớ để chống tràn RAM (Memory Leak) do tạo json liên tục
            gc.collect()
            
            conn, addr = s.accept()
            
            # Đặt timeout 2 giây để tránh bị treo (blocking) nếu trình duyệt mở connection mà không gửi data
            conn.settimeout(2.0)
            
            request = conn.recv(1024)
            request = str(request)
            
            # Bỏ qua các kết nối rỗng
            if len(request) < 5:
                conn.close()
                continue
                
            # Xử lý API /map
            if request.find('GET /map') == 2:
                if maze is not None:
                    data = {
                        "walls": maze.walls,
                        "visited": getattr(maze, "visited", []),
                        "x": maze.x,
                        "y": maze.y,
                        "heading": maze.heading,
                        "sensors": getattr(maze, "last_sensors", [0, 0, 0, 0])
                    }
                else:
                    data = {"walls": [[0]*4 for _ in range(4)], "x":0, "y":0, "heading":1, "sensors": [0,0,0,0]}
                response = json.dumps(data)
                
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: application/json\n')
                conn.send('Connection: close\n\n')
                conn.sendall(response)
                conn.close()
                continue
                
            # Xử lý lệnh START
            if request.find('GET /start') == 2:
                if maze is not None: maze.started = True
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: text/plain\n')
                conn.send('Connection: close\n\n')
                conn.sendall('Started')
                conn.close()
                continue
                
            # Xử lý lệnh RESET
            if request.find('GET /reset') == 2:
                if maze is not None: maze.reset_maze()
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: text/plain\n')
                conn.send('Connection: close\n\n')
                conn.sendall('Reset')
                conn.close()
                continue
                
            # Xử lý lệnh Điều Khiển Thủ Công (Căn Chỉnh)
            if request.find('GET /cmd?action=') == 2:
                start_idx = request.find('action=') + 7
                end_idx = request.find(' HTTP')
                action = request[start_idx:end_idx]
                
                if command_queue is not None:
                    command_queue.append(action)
                    
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: text/plain\n')
                conn.send('Connection: close\n\n')
                conn.sendall('OK')
                conn.close()
                continue

            # Lấy thông số PID
            if request.find('GET /get_pid') == 2:
                data = {"kp": pid.kp, "kd": pid.kd, "lmult": config.MOTOR_LEFT_MULTIPLIER}
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: application/json\n')
                conn.send('Connection: close\n\n')
                conn.sendall(json.dumps(data))
                conn.close()
                continue
                
            # Lưu thông số PID
            if request.find('GET /set_pid') == 2:
                try:
                    # Parse parameters: /set_pid?kp=6.0&kd=6.0
                    start_idx = request.find('?') + 1
                    end_idx = request.find(' HTTP')
                    params_str = request[start_idx:end_idx]
                    params = params_str.split('&')
                    for p in params:
                        k, v = p.split('=')
                        if k == 'kp': pid.kp = float(v)
                        if k == 'kd': pid.kd = float(v)
                        if k == 'lmult': config.MOTOR_LEFT_MULTIPLIER = float(v)
                except Exception as e:
                    print("Error parsing PID:", e)
                
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: text/plain\n')
                conn.send('Connection: close\n\n')
                conn.sendall('OK')
                conn.close()
                continue
                
            # Trả về HTML cho trình duyệt (nếu request là trang chủ)
            if request.find('GET / ') == 2:
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: text/html\n')
                conn.send('Connection: close\n\n')
                conn.sendall(HTML_PAGE)
                
            conn.close()
        except Exception as e:
            print("[Web Server Error]:", e)
            try:
                conn.close()
            except:
                pass
            time.sleep_ms(50)
