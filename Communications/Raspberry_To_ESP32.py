import serial
import time

# 根据你的操作系统设置正确的串口：
# Windows: COM3、COM5 等
# Linux/Mac: /dev/ttyUSB0 或 /dev/tty.SLAB_USBtoUART
PORT = 'COM3'  #  替换为你的设备

ser = serial.Serial(PORT, baudrate=115200, timeout=1)
time.sleep(2)

def send_command(cmd: str):
    ser.write((cmd + '\n').encode('utf-8'))

def read_response():
    if ser.in_waiting:
        return ser.readline().decode('utf-8').strip()
    return None

if __name__ == "__main__":
    while True:
        msg = input("Enter message: ")
        if msg.lower() == "exit" or msg.lower() == "quit":
            print("[PC] Aborting.")
            break
        elif msg.lower() != "listen":
            send_command(msg)
            time.sleep(0.2)
        response = read_response()
        print(f"ESP32 respond: {response}")    