# esp32_serial_backend.py

import serial
import threading
import queue
import time


ser = serial.Serial('COM5', 115200, timeout=1)
time.sleep(2)  


write_queue = queue.Queue()


def send_to_esp32(message: str):
    write_queue.put(message)


def serial_writer():
    while True:
        msg = write_queue.get()
        if msg == "EXIT":
            break
        ser.write((msg + '\n').encode())
        print(f"[WRITE] Sent: {msg}")


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


def handle_message(message):
    print(f"[ESP32] {message}")


def start_serial_service():
    threading.Thread(target=serial_reader, daemon=True).start()
    threading.Thread(target=serial_writer, daemon=True).start()
    print("[SERVICE] Serial communication threads started.")
