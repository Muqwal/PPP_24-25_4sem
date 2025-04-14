import socket
import os
import time
import json
import struct

LISTEN_PORT = 9090
ENCODING = 'utf-8'
HEADER_LENGTH = 8
LOG_FILE = 'server_activities.log'

def get_timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def get_data(sock):
    header = sock.recv(HEADER_LENGTH, socket.MSG_WAITALL)
    length = struct.unpack('!Q', header)[0]
    return b'' if length == 0 else sock.recv(length, socket.MSG_WAITALL)

def send_data(sock, message):
    header = struct.pack('!Q', len(message))
    packet = header + message
    sent_bytes = 0
    while sent_bytes < len(packet):
        sent = sock.send(packet[sent_bytes:])
        if sent == 0:
            raise ConnectionError("Client disconnected")
        sent_bytes += sent

def log_activity(message):
    with open(LOG_FILE, 'a') as log:
        log.write(f"[{get_timestamp()}] {message}\n")

def get_process_list():
    return os.popen("tasklist" if os.name == 'nt' else "ps -aux").read()

def terminate_process(process_id):
    try:
        if os.name == 'nt':
            os.system(f"taskkill /F /PID {process_id}")
        else:
            os.system(f"kill -9 {process_id}")
        return True
    except:
        return False

def handle_connection(client_sock, client_addr):
    log_activity(f"New connection from {client_addr}")
    
    try:
        while True:
            request = get_data(client_sock)
            if not request:
                continue
                
            command = request.decode(ENCODING)
            
            if command == 'get tasks':
                log_activity("Processing task list request")
                processes = get_process_list()
                send_data(client_sock, processes.encode(ENCODING))
                send_data(client_sock, b'')
                
            elif command.startswith('terminate '):
                pid = command.split()[1]
                log_activity(f"Attempting to terminate process {pid}")
                if terminate_process(pid):
                    log_activity(f"Successfully terminated process {pid}")
                else:
                    log_activity(f"Failed to terminate process {pid}")
                    
    except Exception as e:
        log_activity(f"Error: {str(e)}")
    finally:
        client_sock.close()
        log_activity(f"Closed connection with {client_addr}")

def start_server():
    server_sock = socket.socket()
    server_sock.bind(('', LISTEN_PORT))
    server_sock.listen(1)
    log_activity("Server started and listening for connections")
    
    try:
        while True:
            conn, addr = server_sock.accept()
            handle_connection(conn, addr)
    except KeyboardInterrupt:
        log_activity("Server shutdown by administrator")
    finally:
        server_sock.close()

a = 3

if __name__ == "__main__":
    start_server()