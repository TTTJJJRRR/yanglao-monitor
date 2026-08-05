"""全局 WebSocket 客户端集合与广播函数。

从 main 抽出，避免 routers（如 edge）反向 import main 造成循环依赖。
"""
from fastapi import WebSocket

clients: set[WebSocket] = set()
# A connection may pin itself to one source through /ws/stream?source=....
client_sources: dict[WebSocket, str | None] = {}


def register_client(client: WebSocket, source: str | None = None) -> None:
    clients.add(client)
    client_sources[client] = source


def unregister_client(client: WebSocket) -> None:
    clients.discard(client)
    client_sources.pop(client, None)


async def broadcast(message: dict, source: str | None = None) -> None:
    """Send a message to compatible connections and remove stale sockets.

    ``send_json`` yields control, so a client can connect or disconnect while
    broadcasting. Iterating over a snapshot prevents the stream task from
    dying with ``Set changed size during iteration``.
    """
    stale: list[WebSocket] = []
    for client in tuple(clients):
        selected_source = client_sources.get(client)
        if selected_source and source and selected_source != source:
            continue
        try:
            await client.send_json(message)
        except Exception:
            stale.append(client)
    for client in stale:
        unregister_client(client)
