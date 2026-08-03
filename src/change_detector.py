from pathlib import Path

from data_loader import load_yaml


def normalize_text(text: str) -> str:
    """Normalize whitespace so formatting-only differences are ignored."""
    return " ".join(text.split())


def index_requirements(requirements: list[dict]) -> dict[str, dict]:
    """Create a lookup dictionary using requirement IDs as keys."""
    return {
        requirement["id"]: requirement
        for requirement in requirements
    }


def detect_changes(
    requirements_v1: list[dict],
    requirements_v2: list[dict],
) -> list[dict]:
    """Compare two requirement versions and return change information."""
    v1_by_id = index_requirements(requirements_v1)
    v2_by_id = index_requirements(requirements_v2)

    changes = []

    for requirement_id, old_requirement in v1_by_id.items():
        new_requirement = v2_by_id.get(requirement_id)

        if new_requirement is None:
            changes.append(
                {
                    "id": requirement_id,
                    "change_type": "removed",
                }
            )
            continue

        old_text = normalize_text(old_requirement["text"])
        new_text = normalize_text(new_requirement["text"])

        if old_text != new_text:
            changes.append(
                {
                    "id": requirement_id,
                    "change_type": "modified",
                    "old_text": old_text,
                    "new_text": new_text,
                }
            )
        else:
            changes.append(
                {
                    "id": requirement_id,
                    "change_type": "unchanged",
                }
            )

    for requirement_id in v2_by_id:
        if requirement_id not in v1_by_id:
            changes.append(
                {
                    "id": requirement_id,
                    "change_type": "added",
                }
            )

    return changes


if __name__ == "__main__":
    v1_data = load_yaml(
        Path("data/case_study/requirements_v1.yaml")
    )

    v2_data = load_yaml(
        Path("data/case_study/requirements_v2.yaml")
    )

    changes = detect_changes(
        v1_data["requirements"],
        v2_data["requirements"],
    )

    for change in changes:
        print(f'{change["id"]}: {change["change_type"]}')




        