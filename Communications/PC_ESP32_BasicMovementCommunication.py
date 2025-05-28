import threading
import time
import pygame
from pynput import keyboard
from PC_Client import connect_to_server,send_message,receive_message

sock = connect_to_server()

# 保存按键状态和顺序
pressed_keys = []
valid_keys = {'w': 'w', 's': 's', 'a': 'a', 'd': 'd'}
input_state = {"keyboard": None, "joystick": None}
last_sent = ""

def resolve_command():
    return input_state['joystick'] or input_state["keyboard"] 

def send_current_command():
    global last_sent
    command = resolve_command()
    if command != last_sent:
        msg = command if command else 'p'
        send_message(sock, msg)
        print(receive_message(sock))
        last_sent = command

def on_press(key):
    try:
        k = key.char.lower()
        if k in valid_keys and k not in pressed_keys:
            pressed_keys.append(k)
            input_state['keyboard'] = valid_keys[pressed_keys[0]]
            send_current_command()
    except AttributeError:
        if key == keyboard.Key.esc:
            print("[PC] Abort")
            sock.close()
            return False  # 停止监听

def on_release(key):
    try:
        k = key.char.lower()
        if k in pressed_keys:
            pressed_keys.remove(k)
            input_state['keyboard'] = valid_keys[pressed_keys[0]] if pressed_keys else None
            send_current_command()
    except AttributeError:
        pass  # 忽略非字符键释放

# 启动监听器


def get_joystick_command(x,y,deadzone=0.05):
    if abs(x) < deadzone and abs(y) < deadzone:
        return None
    elif abs(x) < abs(y):
        return 's' if y > 0 else 'w'
    else:
        return 'd' if x > 0 else 'a'
    
def joystick_listener():
    pygame.init()

    joystick = None
    has_joystick = False

    global input_state

    last_status = None

    while True:
        # 刷新手柄状态
        #pygame.joystick.quit()
        pygame.joystick.init()
        joystick_count = pygame.joystick.get_count()

        if joystick_count > 0:
            if not has_joystick:
                try:
                    pygame.joystick.init()
                    joystick = pygame.joystick.Joystick(0)
                    joystick.init()
                    has_joystick = True
                    if last_status != True:
                        print("[PC] Joystick detected")
                        last_status = True
                except pygame.error:
                    joystick = None
                    has_joystick = False
        else:
            if has_joystick:
                joystick = None
                has_joystick = False
                input_state["joystick"] = None
                send_current_command()
                pygame.joystick.quit()
                pygame.joystick.init()
                if last_status != False:
                    print("[PC] No joystick detected")
                    last_status = False
            else:
                pygame.joystick.quit()
                pygame.joystick.init()


        if has_joystick and joystick is not None and joystick.get_init():
            try:
                pygame.event.pump()
                x = joystick.get_axis(0)
                y = joystick.get_axis(1)
                command = get_joystick_command(x, y)
                input_state["joystick"] = command
                send_current_command()
                time.sleep(0.05)  # 维持高频率
            except pygame.error:
                print("[PC] Joystick error — unplugged?")
                joystick = None
                has_joystick = False
                input_state["joystick"] = None
                send_current_command()
                last_status = False
        else:
            time.sleep(1.5)



if __name__ == "__main__":
    print("[PC] Control started. Press ESC to exit.")

    try: 
        threading.Thread(target=joystick_listener, daemon=True).start()
    except Exception as e:
        print(f"[ERROR] {e}")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()