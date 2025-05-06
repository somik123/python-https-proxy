import socket
import threading
import ssl

# Define constants
HOST = '0.0.0.0'
PORT = 1925
BUFFER_SIZE = 4096

# Create SSL context for server-side socket
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem", password="11223344")  # Replace securely

def handle_client(client_socket):
    try:
        request = client_socket.recv(BUFFER_SIZE).decode('utf-8', errors='ignore')
        if not request:
            client_socket.close()
            return

        lines = request.splitlines()
        if not lines:
            client_socket.close()
            return

        parts = lines[0].strip().split()
        if len(parts) < 2:
            client_socket.close()
            return

        method = parts[0]
        url = parts[1]
        protocol = parts[2] if len(parts) > 2 else "HTTP/1.1"

        # Handle CONNECT method for HTTPS
        if method.upper() == "CONNECT":
            if ':' in url:
                host, port_str = url.split(':')
                port = int(port_str)
            else:
                host = url
                port = 443  # Default HTTPS port

            print(f"Establishing tunnel to {host}:{port}")

            # Acknowledge tunnel request to client
            client_socket.sendall(f"{protocol} 200 Connection Established\r\n\r\n".encode())

            # Upgrade the client connection to SSL
            client_ssl = context.wrap_socket(client_socket, server_side=True)

            # Connect to the real destination server
            server_socket = socket.create_connection((host, port))
            server_ssl = ssl.create_default_context().wrap_socket(server_socket, server_hostname=host)

            # Start bidirectional forwarding
            threading.Thread(target=forward_data, args=(client_ssl, server_ssl)).start()
            threading.Thread(target=forward_data, args=(server_ssl, client_ssl)).start()

        else:
            # Optional: handle GET/POST over HTTP here
            print(f"Ignoring non-CONNECT method: {method}")
            client_socket.close()

    except Exception as e:
        print(f"[!] Error in handle_client: {e}")
        client_socket.close()

def forward_data(source, destination):
    try:
        while True:
            data = source.recv(BUFFER_SIZE)
            if not data:
                break
            destination.sendall(data)
    except Exception as e:
        print(f"[!] Forwarding error: {e}")
    finally:
        source.close()
        destination.close()

def start_proxy():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_socket:
        proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxy_socket.bind((HOST, PORT))
        proxy_socket.listen(5)
        print(f"[+] HTTPS Proxy server running on {HOST}:{PORT}")

        while True:
            client_socket, addr = proxy_socket.accept()
            print(f"[>] Connection received from {addr}")
            threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()

if __name__ == "__main__":
    start_proxy()
