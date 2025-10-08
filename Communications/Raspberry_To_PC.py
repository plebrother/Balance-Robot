import socket

HOST = '0.0.0.0'
PORT = 65432

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Raspberry PI listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            print(f"Connected by {addr}")
            with conn:
                #conn.sendall(b"Welcome to the server!\n")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    print(f"Received from {addr}: {data.decode().strip()}")
                    conn.sendall(b"Echo: " + data)

if __name__ == "__main__":
    start_server()