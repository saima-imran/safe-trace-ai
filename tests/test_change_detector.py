from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from change_detector import detect_changes
from data_loader import load_yaml


def test_detects_modified_and_unchanged_requirements() -> None:
    """The controlled dataset should produce the expected change statuses."""

    requirements_v1_data = load_yaml(
        Path("data/case_study/requirements_v1.yaml")
    )

    requirements_v2_data = load_yaml(
        Path("data/case_study/requirements_v2.yaml")
    )

    changes = detect_changes(
        requirements_v1_data["requirements"],
        requirements_v2_data["requirements"],
    )

    changes_by_id = {
        change["id"]: change["change_type"]
        for change in changes
    }

    assert changes_by_id["SSR-001"] == "modified"
    assert changes_by_id["SSR-002"] == "modified"
    assert changes_by_id["SSR-003"] == "modified"
    assert changes_by_id["SSR-004"] == "modified"
    assert changes_by_id["SSR-005"] == "unchanged"
    assert changes_by_id["SSR-006"] == "unchanged"

    