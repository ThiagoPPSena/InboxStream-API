from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.services.websockets import manager

router = APIRouter(tags=["WebSockets"])

@router.websocket("/websocket")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint WebSocket para clientes que desejam receber notificações de e-mail.
    """
    await manager.connect(websocket)
    print(f"Cliente conectado: {websocket.client}")
    
    try:
        while True:
            data = await websocket.receive_text()
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Cliente desconectado: {websocket.client}")
    except Exception as e:
        manager.disconnect(websocket)
        print(f"Exceção no WebSocket: {e}")