from .celery_app import celery_app
from celery import Task
import time
import base64
from collections import Counter
import heapq
from typing import Dict, Any

class WebSocketTask(Task):
    _websocket_connections = {}

    @property
    def websocket_connections(self):
        return self._websocket_connections

    def update_state(self, task_id=None, state=None, meta=None):
        super().update_state(task_id=task_id, state=state, meta=meta)
        # WebSocket connection handling will be implemented in the WebSocket manager

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(data: str) -> Dict[str, str]:
    # Count frequency of each character
    frequency = Counter(data)
    
    # Create a priority queue to store nodes
    heap = []
    for char, freq in frequency.items():
        heapq.heappush(heap, HuffmanNode(char, freq))
    
    # Build Huffman tree
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        internal = HuffmanNode(None, left.freq + right.freq)
        internal.left = left
        internal.right = right
        heapq.heappush(heap, internal)
    
    # Generate Huffman codes
    codes = {}
    def generate_codes(node, code=""):
        if node.char is not None:
            codes[node.char] = code
            return
        generate_codes(node.left, code + "0")
        generate_codes(node.right, code + "1")
    
    if heap:
        generate_codes(heap[0])
    return codes

@celery_app.task(bind=True, base=WebSocketTask)
def encode_data(self, data: str) -> Dict[str, Any]:
    # Simulate progress
    total_steps = 5
    for step in range(total_steps):
        progress = (step + 1) * 20
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'PROGRESS',
                'task_id': self.request.id,
                'operation': 'encode',
                'progress': progress
            }
        )
        time.sleep(1)  # Simulate work
    
    # Generate Huffman codes
    huffman_codes = build_huffman_tree(data)
    
    # Encode data using Huffman codes
    encoded = ''.join(huffman_codes[char] for char in data)
    
    # Pad encoded data to make it divisible by 8
    padding = (8 - len(encoded) % 8) % 8
    encoded += '0' * padding
    
    # Convert binary string to bytes and then to base64
    encoded_bytes = int(encoded, 2).to_bytes((len(encoded) + 7) // 8, byteorder='big')
    base64_encoded = base64.b64encode(encoded_bytes).decode('utf-8')
    
    return {
        'encoded_data': base64_encoded,
        'huffman_codes': huffman_codes,
        'padding': padding
    }

@celery_app.task(bind=True, base=WebSocketTask)
def decode_data(self, encoded_data: str, huffman_codes: Dict[str, str], padding: int) -> str:
    # Simulate progress
    total_steps = 5
    for step in range(total_steps):
        progress = (step + 1) * 20
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'PROGRESS',
                'task_id': self.request.id,
                'operation': 'decode',
                'progress': progress
            }
        )
        time.sleep(1)  # Simulate work
    
    # Decode base64 to bytes and then to binary string
    encoded_bytes = base64.b64decode(encoded_data)
    binary = bin(int.from_bytes(encoded_bytes, byteorder='big'))[2:]
    
    # Remove padding
    binary = binary[:-padding] if padding else binary
    
    # Create reverse mapping of Huffman codes
    reverse_codes = {code: char for char, code in huffman_codes.items()}
    
    # Decode using Huffman codes
    decoded = ''
    current_code = ''
    for bit in binary:
        current_code += bit
        if current_code in reverse_codes:
            decoded += reverse_codes[current_code]
            current_code = ''
    
    return decoded 