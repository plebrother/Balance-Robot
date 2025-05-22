from pynput import keyboard
from PC_Client import connect_to_server,send_message,receive_message

sock = connect_to_server()

# 保存按键状态和顺序
pressed_keys = []
valid_keys = {'w': 'forward', 's': 'backward'}

def send_current_command():
    if pressed_keys:
        key = pressed_keys[0]
        send_message(sock, valid_keys[key])
        print(receive_message(sock))
    else:
        send_message(sock, 'stop')
        print(receive_message(sock))

def on_press(key):
    try:
        k = key.char.lower()
        if k in valid_keys and k not in pressed_keys:
            pressed_keys.append(k)
            send_message(sock, valid_keys[pressed_keys[0]])
            print(receive_message(sock))
    except AttributeError:
        if key == keyboard.Key.esc:
            print("退出程序")
            sock.close()
            return False  # 停止监听

def on_release(key):
    try:
        k = key.char.lower()
        if k in pressed_keys:
            pressed_keys.remove(k)
            send_current_command()
    except AttributeError:
        pass  # 忽略非字符键释放

# 启动监听器
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
