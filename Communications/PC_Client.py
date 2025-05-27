import socket

HOST = '192.168.8.102'  # server address
PORT = 65432        # server port

def connect_to_server(): #Connect to the server, return the socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((HOST, PORT))
        s.settimeout(None)
        return s
    except Exception as e:
        print(f"[PC] Connection error: {e}")
        return None

def send_message(sock, message): #send a string to the server

    try:
        sock.sendall(message.encode())
    except Exception as e:
        print(f"[PC] Send error: {e}")

def receive_message(sock): #listen and receive a string from server, return the string

    try:
        data = sock.recv(1024)
        if data:
            return data.decode()
        else:
            return None  # Connection failed?
    except Exception as e:
        print(f"[PC] Receive error: {e}")
        return None

if __name__ == "__main__": # run this file alone to debug

    sock = connect_to_server()
    if sock:
        while True:
            msg = input("Enter message: ").strip()
            if msg.lower() == "exit" or msg.lower() == "quit":
                print("[PC] Closing connection.")
                sock.close()
                break
            elif msg.lower() != "listen":
                send_message(sock, msg)
            response = receive_message(sock)
            print(f"Received: {response}")