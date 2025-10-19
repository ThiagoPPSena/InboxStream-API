from typing import List, Dict
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    """
    Gerencia as conexões WebSocket ativas e lida com broadcast de mensagens.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Aceita a conexão e a adiciona ao pool."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a conexão do pool."""
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Envia uma mensagem para uma única conexão."""
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """Envia uma mensagem para *todas* as conexões ativas (a notificação!)."""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                self.disconnect(connection)
            except Exception as e:
                print(f"Erro ao enviar broadcast: {e}")

manager = ConnectionManager()