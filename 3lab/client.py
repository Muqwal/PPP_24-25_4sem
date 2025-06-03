import asyncio
import websockets
import json
import click
import uuid
from typing import Dict, Any
from websocket import create_connection, WebSocketException
import sys
from tqdm import tqdm
import time

class WebSocketClient:
    def __init__(self, user_id: str, base_url: str = "ws://localhost:8000"):
        self.user_id = user_id
        self.base_url = base_url
        self.active_tasks: Dict[str, Any] = {}
        self.progress_bars: Dict[str, tqdm] = {}

    def create_connection(self, task_id: str, max_retries: int = 3) -> str:
        """Create a new WebSocket connection for a task with retry logic"""
        for attempt in range(max_retries):
            try:
                url = f"{self.base_url}/ws/{self.user_id}/{task_id}"
                ws = create_connection(url, timeout=30)
                return ws
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to connect after {max_retries} attempts: {str(e)}")
                time.sleep(1)

    def encode_data(self, data: str) -> Dict[str, Any]:
        """Encode data using Huffman coding"""
        task_id = str(uuid.uuid4())
        ws = None
        try:
            ws = self.create_connection(task_id)

            # Send encode request
            request = {
                "operation": "encode",
                "data": data
            }
            ws.send(json.dumps(request))

            # Process responses
            while True:
                try:
                    response = json.loads(ws.recv())
                    status = response.get("status")

                    if status == "STARTED":
                        print(f"\nStarting encoding task {task_id}")
                        self.progress_bars[task_id] = tqdm(total=100, desc="Encoding")
                    
                    elif status == "PROGRESS":
                        progress = response.get("progress", 0)
                        if task_id in self.progress_bars:
                            self.progress_bars[task_id].update(progress - self.progress_bars[task_id].n)
                    
                    elif status == "COMPLETED":
                        if task_id in self.progress_bars:
                            self.progress_bars[task_id].close()
                        return response.get("result", {})
                    
                    elif status == "ERROR":
                        print(f"Error: {response.get('message')}")
                        return {}

                except WebSocketException:
                    print("Connection closed unexpectedly")
                    return {}

        except Exception as e:
            print(f"Error: {str(e)}")
            return {}
        finally:
            if ws:
                try:
                    ws.close()
                except:
                    pass

    def decode_data(self, encoded_data: str, huffman_codes: Dict[str, str], padding: int) -> str:
        """Decode data using Huffman coding"""
        task_id = str(uuid.uuid4())
        ws = None
        try:
            ws = self.create_connection(task_id)

            # Send decode request
            request = {
                "operation": "decode",
                "data": encoded_data,
                "huffman_codes": huffman_codes,
                "padding": padding
            }
            ws.send(json.dumps(request))

            # Process responses
            while True:
                try:
                    response = json.loads(ws.recv())
                    status = response.get("status")

                    if status == "STARTED":
                        print(f"\nStarting decoding task {task_id}")
                        self.progress_bars[task_id] = tqdm(total=100, desc="Decoding")
                    
                    elif status == "PROGRESS":
                        progress = response.get("progress", 0)
                        if task_id in self.progress_bars:
                            self.progress_bars[task_id].update(progress - self.progress_bars[task_id].n)
                    
                    elif status == "COMPLETED":
                        if task_id in self.progress_bars:
                            self.progress_bars[task_id].close()
                        return response.get("result", {}).get("result", "")
                    
                    elif status == "ERROR":
                        print(f"Error: {response.get('message')}")
                        return ""

                except WebSocketException:
                    print("Connection closed unexpectedly")
                    return ""

        except Exception as e:
            print(f"Error: {str(e)}")
            return ""
        finally:
            if ws:
                try:
                    ws.close()
                except:
                    pass

@click.group()
def cli():
    """Console client for WebSocket-based Huffman coding service"""
    pass

@cli.command()
@click.option('--user-id', prompt='Enter your user ID', help='Your user ID')
@click.option('--data', prompt='Enter data to encode', help='Data to encode')
def encode(user_id: str, data: str):
    """Encode data using Huffman coding"""
    client = WebSocketClient(user_id)
    result = client.encode_data(data)
    if result:
        print("\nEncoding result:")
        print(f"Encoded data: {result['encoded_data']}")
        print(f"Huffman codes: {json.dumps(result['huffman_codes'], indent=2)}")
        print(f"Padding: {result['padding']}")

@cli.command()
@click.option('--user-id', prompt='Enter your user ID', help='Your user ID')
@click.option('--encoded-data', prompt='Enter encoded data', help='Encoded data to decode')
@click.option('--huffman-codes', prompt='Enter Huffman codes (as JSON)', help='Huffman codes as JSON string')
@click.option('--padding', prompt='Enter padding', type=int, help='Padding used in encoding')
def decode(user_id: str, encoded_data: str, huffman_codes: str, padding: int):
    """Decode data using Huffman coding"""
    try:
        huffman_dict = json.loads(huffman_codes)
    except json.JSONDecodeError:
        print("Error: Invalid Huffman codes JSON format")
        return

    client = WebSocketClient(user_id)
    result = client.decode_data(encoded_data, huffman_dict, padding)
    if result:
        print("\nDecoded result:")
        print(result)

@cli.command()
def interactive():
    """Start interactive mode"""
    user_id = click.prompt('Enter your user ID')
    client = WebSocketClient(user_id)
    
    while True:
        click.echo("\nAvailable commands:")
        click.echo("1. Encode data")
        click.echo("2. Decode data")
        click.echo("3. Exit")
        
        try:
            choice = click.prompt('Enter your choice (1-3)', type=int)
            
            if choice == 1:
                data = click.prompt('Enter data to encode')
                result = client.encode_data(data)
                if result:
                    click.echo("\nEncoding result:")
                    click.echo(f"Encoded data: {result['encoded_data']}")
                    click.echo(f"Huffman codes: {json.dumps(result['huffman_codes'], indent=2)}")
                    click.echo(f"Padding: {result['padding']}")
            
            elif choice == 2:
                encoded_data = click.prompt('Enter encoded data')
                huffman_codes = click.prompt('Enter Huffman codes (as JSON)')
                try:
                    huffman_dict = json.loads(huffman_codes)
                except json.JSONDecodeError:
                    click.echo("Error: Invalid Huffman codes JSON format")
                    continue
                padding = click.prompt('Enter padding', type=int)
                
                result = client.decode_data(encoded_data, huffman_dict, padding)
                if result:
                    click.echo("\nDecoded result:")
                    click.echo(result)
            
            elif choice == 3:
                break
            
            else:
                click.echo("Invalid choice")
        
        except Exception as e:
            click.echo(f"Error: {str(e)}")
            continue

if __name__ == '__main__':
    cli() 