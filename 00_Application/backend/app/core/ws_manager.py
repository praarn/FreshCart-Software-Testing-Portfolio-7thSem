"""R6.7: in-memory pub/sub for order-status WebSocket subscribers."""
from collections import defaultdict

from fastapi import WebSocket


class OrderWsManager:
    def __init__(self) -> None:
        self._connections: dict[int, list[WebSocket]] = defaultdict(list)

    def connect(self, order_id: int, websocket: WebSocket) -> None:
        self._connections[order_id].append(websocket)

    def disconnect(self, order_id: int, websocket: WebSocket) -> None:
        if websocket in self._connections.get(order_id, []):
            self._connections[order_id].remove(websocket)

    async def broadcast(self, order_id: int, message: dict) -> None:
        for ws in list(self._connections.get(order_id, [])):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(order_id, ws)


manager = OrderWsManager()
