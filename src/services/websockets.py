from fastapi import WebSocket, WebSocketDisconnect
from typing import List
from src.schemas.emails import Email as EmailSchema
import json

class ConnectionManager:
    """Gerencia conexões WebSocket ativas e a transmissão de mensagens."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Aceita e adiciona uma nova conexão."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove uma conexão desconectada."""
        self.active_connections.remove(websocket)

    async def broadcast(self, message: EmailSchema):
        """Envia uma mensagem para todos os clientes conectados."""

        try:
            data_to_send = {
                "id": message.get("id", ""),
                "subject": message.get("subject", ""),
                "body": message.get("body", ""),
                "category": message.get("category", ""),
                "date": message.get("date", "").isoformat()      
            }

            json_string = json.dumps(data_to_send)
        except Exception as e:
            print(f"Erro ao preparar mensagem para broadcast: {e}")
            return
        disconnected_connections = []
        for connection in self.active_connections:
            try:
                await connection.send(json_string)
            except WebSocketDisconnect:
                disconnected_connections.append(connection)
            except Exception as e:
                print(f"Erro ao enviar para conexão: {e}")
                disconnected_connections.append(connection)

        for connection in disconnected_connections:
            if connection in self.active_connections:
                self.active_connections.remove(connection)


manager = ConnectionManager()