"""设备活跃监测与离线告警。

按源记录最后一次收到帧的时间；超过阈值自动触发 critical 告警，
并在恢复后发出在线事件。家属端不得静音或关闭关键预警，所以这里
只负责广播事件，不提供任何关闭开关。
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable

from .bus import broadcast


@dataclass
class SourceHeartbeat:
    last_seen_ms: int = 0
    offline_since_ms: int | None = None
    online: bool = True
    last_payload_ms: int = 0


@dataclass
class DeviceMonitor:
    timeout_s: float = 5.0
    now_ms: Callable[[], int] = lambda: int(time.time() * 1000)
    heartbeats: dict[str, SourceHeartbeat] = field(default_factory=dict)

    def touch(self, source: str, payload_ts_ms: int | None = None) -> None:
        hb = self.heartbeats.setdefault(source, SourceHeartbeat())
        now = self.now_ms()
        hb.last_seen_ms = payload_ts_ms or now
        hb.last_payload_ms = payload_ts_ms or now

    def check(self) -> list[dict]:
        now = self.now_ms()
        events: list[dict] = []
        timeout_ms = int(self.timeout_s * 1000)
        for source, hb in self.heartbeats.items():
            if hb.last_seen_ms == 0:
                continue
            gap = now - hb.last_seen_ms
            if gap > timeout_ms and hb.online:
                hb.online = False
                hb.offline_since_ms = now
                events.append(
                    {
                        "type": "device_offline",
                        "data": {
                            "source": source,
                            "timestamp_ms": now,
                            "last_seen_ms": hb.last_seen_ms,
                            "level": "critical",
                            "message": f"{source} 连续 {self.timeout_s:.0f}s 未收到数据",
                        },
                    }
                )
            elif gap <= timeout_ms and not hb.online:
                hb.online = True
                hb.offline_since_ms = None
                events.append(
                    {
                        "type": "device_online",
                        "data": {
                            "source": source,
                            "timestamp_ms": now,
                            "last_seen_ms": hb.last_seen_ms,
                            "level": "yellow",
                            "message": f"{source} 已恢复在线",
                        },
                    }
                )
        return events

    async def publish_checks(self) -> None:
        for event in self.check():
            await broadcast(event)
