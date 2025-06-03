from fastapi import APIRouter, WebSocket, Depends, HTTPException
from app.websocket.manager import manager
from app.core.config import WebSocketMessage
from app.celery.tasks import encode_data, decode_data
from typing import Dict, Any
import json
from celery.result import AsyncResult
from starlette.websockets import WebSocketDisconnect

router = APIRouter()

@router.websocket("/ws/{user_id}/{task_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, task_id: str):
    await manager.connect(websocket, user_id, task_id)
    try:
        data = await websocket.receive_json()
        operation = data.get("operation")
        input_data = data.get("data")
        
        if not operation or not input_data:
            await websocket.send_json({
                "status": "ERROR",
                "message": "Invalid request format"
            })
            return

        try:
            # Start notification
            start_message = WebSocketMessage(
                status="STARTED",
                task_id=task_id,
                operation=operation
            )
            await manager.send_message(start_message, user_id, task_id)

            # Process the task
            if operation == "encode":
                task = encode_data.delay(input_data)
            elif operation == "decode":
                huffman_codes = data.get("huffman_codes")
                padding = data.get("padding")
                if not huffman_codes or padding is None:
                    await websocket.send_json({
                        "status": "ERROR",
                        "message": "Missing huffman_codes or padding for decode operation"
                    })
                    return
                task = decode_data.delay(input_data, huffman_codes, padding)
            else:
                await websocket.send_json({
                    "status": "ERROR",
                    "message": "Invalid operation"
                })
                return

            # Wait for the task to complete with timeout
            result = AsyncResult(task.id)
            task_result = result.get(timeout=30)  # 30 seconds timeout

            # Send completion notification
            complete_message = WebSocketMessage(
                status="COMPLETED",
                task_id=task_id,
                operation=operation,
                result=task_result if isinstance(task_result, dict) else {"result": task_result}
            )
            await manager.send_message(complete_message, user_id, task_id)

        except TimeoutError:
            if manager.get_connection(user_id, task_id):
                await websocket.send_json({
                    "status": "ERROR",
                    "message": "Task timed out"
                })
        except Exception as e:
            if manager.get_connection(user_id, task_id):
                await websocket.send_json({
                    "status": "ERROR",
                    "message": f"Task error: {str(e)}"
                })

    except WebSocketDisconnect:
        manager.disconnect(user_id, task_id)
    except Exception as e:
        if manager.get_connection(user_id, task_id):
            await websocket.send_json({
                "status": "ERROR",
                "message": str(e)
            })
    finally:
        manager.disconnect(user_id, task_id) 