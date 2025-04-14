import socket
import os
import json
import struct
import time

SERVER_HOST = 'localhost'
SERVER_PORT = 9090
ENCODING = 'utf-8'
HEADER_SIZE = 8

COMMAND_HELP = {
    "get tasks": "Display running processes on server",
    "terminate [ID]": "Stop process by ID",
    "clear": "Clear terminal",
    "disconnect": "Close connection"
}

def current_timestamp():
    return time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())

def receive_data(sock):
    header = sock.recv(HEADER_SIZE, socket.MSG_WAITALL)
    data_len = struct.unpack('!Q', header)[0]
    return b'' if data_len == 0 else sock.recv(data_len, socket.MSG_WAITALL)

def send_data(sock, data):
    header = struct.pack('!Q', len(data))
    packet = header + data
    total_sent = 0
    while total_sent < len(packet):
        sent = sock.send(packet[total_sent:])
        if sent == 0:
            raise RuntimeError("Connection broken")
        total_sent += sent

def process_command(client_sock):
    user_input = input(f"{SERVER_HOST}$ ").strip()
    
    if not user_input:
        return 'invalid'
    
    if user_input == 'help':
        print("\nAvailable commands:")
        for cmd, desc in COMMAND_HELP.items():
            print(f"  {cmd.ljust(15)} - {desc}")
        return 'internal'
    
    elif user_input == 'clear':
        os.system('cls' if os.name == 'nt' else 'clear')
        return 'internal'
    
    elif user_input == 'disconnect':
        return 'terminate'
    
    elif user_input == 'get tasks':
        send_data(client_sock, user_input.encode(ENCODING))
        send_data(client_sock, b'')
        return 'receive'
    
    elif user_input.startswith('terminate '):
        send_data(client_sock, user_input.encode(ENCODING))
        send_data(client_sock, b'')
        return 'internal'
    
    else:
        print("Unknown command. Type 'help' for available commands")
        return 'invalid'

def run_client():
    connection = socket.socket()
    connection.connect((SERVER_HOST, SERVER_PORT))
    
    try:
        while True:
            status = process_command(connection)
            
            if status == 'invalid':
                continue
                
            if status == 'receive':
                output_file = f"process_list_{current_timestamp()}.txt"
                with open(output_file, 'w') as f:
                    while True:
                        data = receive_data(connection)
                        if not data:
                            break
                        decoded = data.decode(ENCODING)
                        print(decoded)
                        f.write(decoded + '\n')
                print(f"Results saved to {output_file}")
                
            if status == 'terminate':
                break
                
    except Exception as err:
        print(f"Error occurred: {err}")
    finally:
        connection.close()

def a():
    pass

if __name__ == "__main__":
    run_client()