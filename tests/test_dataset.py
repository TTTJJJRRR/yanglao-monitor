import os
import sys
from pathlib import Path

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "backend"))

import numpy as np

from app.inference.mmwave_cnn.dataset import RadarDataset, A_TO_BEHAVIOR, BEHAVIOR_TO_INDEX
from app.inference.mmwave_cnn.preprocess import load_mmwave_frames


def test_fixture_loader_maps_actions():
    fixture_root = Path(_ROOT) / "tests" / "fixtures" / "mmwave"
    dataset = RadarDataset(fixture_root)
    assert len(dataset) == 8
    assert dataset.class_count == 8
    labels = [sample.label for sample in dataset]
    expected = list(A_TO_BEHAVIOR.values())
    assert labels == expected


def test_training_pairs_are_indexed_by_behavior():
    fixture_root = Path(_ROOT) / "tests" / "fixtures" / "mmwave"
    dataset = RadarDataset(fixture_root)
    pairs = dataset.to_training_pairs()
    assert len(pairs) == 8
    for frames, label in pairs:
        assert isinstance(frames, list)
        assert isinstance(label, int)
        assert 0 <= label < 8


def test_empty_fixture_directory_is_safe():
    tmp_root = Path(_ROOT) / "tests" / "fixtures" / "empty"
    tmp_root.mkdir(parents=True, exist_ok=True)
    dataset = RadarDataset(tmp_root)
    assert len(dataset) == 0


if __name__ == "__main__":
    test_fixture_loader_maps_actions()
    test_training_pairs_are_indexed_by_behavior()
    test_empty_fixture_directory_is_safe()
    print("ALL TESTS PASSED")
