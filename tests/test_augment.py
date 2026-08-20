import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "backend"))

import numpy as np

from app.inference.mmwave_cnn.preprocess import preprocess_sequence


def augment(frames):
    rng = np.random.default_rng(7)
    out = []
    theta = float(rng.uniform(-0.15, 0.15))
    c, s = np.cos(theta), np.sin(theta)
    rot = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]], dtype=np.float32)
    for frame in frames:
        pts = np.asarray(frame, dtype=np.float32).copy()
        if pts.size == 0:
            out.append(pts)
            continue
        pts = pts @ rot.T
        pts += rng.normal(0.0, 0.01, size=pts.shape).astype(np.float32)
        out.append(pts)
    return out


def test_augment_keeps_shape():
    frames = [np.zeros((10, 3), dtype=np.float32) for _ in range(4)]
    out = augment(frames)
    assert len(out) == len(frames)
    assert out[0].shape == (10, 3)


def test_augment_works_with_preprocess():
    frames = [np.zeros((10, 3), dtype=np.float32) for _ in range(4)]
    seq = preprocess_sequence(augment(frames))
    assert seq.shape == (32, 2, 32, 32)


if __name__ == "__main__":
    test_augment_keeps_shape()
    test_augment_works_with_preprocess()
    print("ALL TESTS PASSED")
