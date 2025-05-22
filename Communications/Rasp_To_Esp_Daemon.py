# esp32_serial_backend.py

import serial
import threading
import queue
import time

# 初始化串口对象
ser = serial.Serial('COM5', 115200, timeout=1)
time.sleep(2)  # 等待 ESP32 启动

# 写入消息的队列
write_queue = queue.Queue()

# 外部接口：可供其他模块调用
def send_to_esp32(message: str):
    write_queue.put(message)

# 串口写入线程
def serial_writer():
    while True:
        msg = write_queue.get()
        if msg == "EXIT":
            break
        ser.write((msg + '\n').encode())
        print(f"[WRITE] Sent: {msg}")

# 串口读取线程
def serial_reader():
    while True:
        if ser.in_waiting:
            try:
                line = ser.readline().decode().strip()
                if line:
                    print(f"[READ] Received: {line}")
                    handle_message(line)
            except UnicodeDecodeError:
                continue
        time.sleep(0.1)

# 消息处理函数（可定制）
def handle_message(message):
    print(f"[ESP32] {message}")

# 启动后台服务
def start_serial_service():
    threading.Thread(target=serial_reader, daemon=True).start()
    threading.Thread(target=serial_writer, daemon=True).start()
    print("[SERVICE] Serial communication threads started.")
