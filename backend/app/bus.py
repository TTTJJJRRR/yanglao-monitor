"""全局 WebSocket 客户端集合与广播函数。

从 main 抽出，避免 routers（如 edge）反向 import main 造成循环依赖。
"""
from fastapi import WebSocket

clients: set[WebSocket] = set()


async def broadcast(message: dict) -> None:
    stale: list[WebSocket] = []
    for client in clients:
        try:
            await client.send_json(message)
        except Exception:
            stale.append(client)
    for client in stale:
        clients.discard(client)
