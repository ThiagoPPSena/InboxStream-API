from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.services.websockets import manager

router = APIRouter(tags=["WebSockets"])

@router.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint principal para estabelecer e manter a conexão WebSocket.
    """
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            pass

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Cliente desconectado.")
    except Exception as e:
        manager.disconnect(websocket)
        print(f"Erro inesperado no WebSocket: {e}")