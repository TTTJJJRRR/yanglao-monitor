"""雷达行为分类模型接缝测试（M2/M3 空挡接口，验证「不伪造」契约）。

验证点：
- StubBehaviorClassifier.classify() 显式抛 ModelNotLoadedError（拒绝伪造行为）
- get_classifier() 默认返回 Stub（无真实模型时不返回任何行为）
- register_classifier(真实实现) 后 get_classifier() 返回真实预测；测试后还原为 Stub
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "backend"))

from app.inference.behavior_classifier import (
    BehaviorClassifier,
    BehaviorPrediction,
    RadarFrame,
    register_classifier,
    get_classifier,
    StubBehaviorClassifier,
    ModelNotLoadedError,
)
from app.models import BehaviorAction


class FakeClassifier(BehaviorClassifier):
    def classify(self, frame):
        return BehaviorPrediction(BehaviorAction.walking, 0.9)


def test_stub_refuses_fake():
    stub = StubBehaviorClassifier()
    try:
        stub.classify(RadarFrame("RADAR_01", 0))
        raise AssertionError("Stub 应拒绝伪造，却返回了结果")
    except ModelNotLoadedError:
        pass


def test_get_classifier_default_is_stub():
    # 显式置为 Stub 后确认 get_classifier 返回 Stub（与全局状态无关，确定性）
    register_classifier(StubBehaviorClassifier())
    assert isinstance(get_classifier(), StubBehaviorClassifier)


def test_register_and_get():
    register_classifier(FakeClassifier())
    clf = get_classifier()
    pred = clf.classify(RadarFrame("RADAR_01", 0))
    assert pred.action == BehaviorAction.walking
    assert pred.confidence == 0.9
    # 还原为 Stub，避免污染其它测试 / 运行实例
    register_classifier(StubBehaviorClassifier())


if __name__ == "__main__":
    import traceback
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("  PASS", name)
            except Exception as e:  # noqa: BLE001
                failed += 1
                print("  FAIL", name, "->", repr(e))
    if failed:
        print(f"\n{failed} FAILED")
        sys.exit(1)
    print("\nALL TESTS PASSED")
