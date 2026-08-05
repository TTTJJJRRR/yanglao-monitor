"""真实雷达数据源骨架（M1 接入点）。

M0 阶段雷达未到货，这里先用占位实现，保证 'real' 数据通道能端到端打通：
- 现在：返回带 ``source='real'`` 的有效生命体征（mock 占位，便于联调）。
- M1 接入：把 mmVital-Signs 的相位信号 → 生命体征估计算法移植进来，
  解析 TI IWR6843AOP 的 OOB TLV 帧（参考 TI Industrial Toolbox 的
  ``xwr64xxAOP_mmw_demo.bin`` 与 lightinfection/TI_IWR6843AOP 的串口协议）。

移植要点（详见 deliverables/tech-plan/opensource-porting-guide）：
- mmVital-Signs 的 vital_signs_estimator 输出 breath_rate / heart_rate，
  直接映射到本项目平坦契约字段。
- 雷达偶发空帧（坑 B）：返回 ``None`` 的字段由调用方决定落库或跳过，
  不要违反 VitalRecord 的非空约束。
"""
import random
import time

from ..models import VitalSource


class MmVitalSource:
    """占位：真实雷达生命体征源。M1 替换为 mmVital 解析逻辑。"""

    def __init__(self, device_id: str = "RADAR_01"):
        self.device_id = device_id

    def next_vital(self) -> dict | None:
        """返回一帧生命体征。M1 改为解析雷达串口 / TLV；现占位返回有效帧。

        返回 ``None`` 表示当前无有效帧（雷达遮挡 / 初始化中），调用方应跳过落库。
        """
        # TODO(M1): 接入 mmVital 解析，替换下方占位随机生成
        return {
            "timestamp_ms": int(time.time() * 1000),
            "device_id": self.device_id,
            "breath_rate": round(random.uniform(13, 19), 1),
            "heart_rate": round(random.uniform(62, 95), 1),
            "chest_displacement_mm": round(random.uniform(1.5, 7), 1),
            "motion_flag": random.choice([True, False]),
            "ahi_index": None,
            "source": VitalSource.real.value,
        }
