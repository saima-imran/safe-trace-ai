"""Deterministic governance policies for AI-assisted activities."""

from pathlib import Path

from data_loader import load_yaml


POLICY_FILE = Path("config/governance_policies.yaml")

VALID_DECISIONS = {
    "AI_PERMITTED",
    "HUMAN_AUTHORIZATION_REQUIRED",
    "AI_RESTRICTED",
}


def load_governance_policies(
    policy_file: Path = POLICY_FILE,
) -> list[dict]:
    """Load and validate the configured AI-governance policies."""

    policy_data = load_yaml(policy_file)

    if not policy_data or "policies" not in policy_data:
        raise ValueError(
            "The governance policy file must contain a 'policies' list."
        )

    policies = policy_data["policies"]

    if not isinstance(policies, list):
        raise ValueError(
            "The 'policies' value must be a list."
        )

    policy_ids = set()

    for policy in policies:
        required_fields = {
            "id",
            "version",
            "activity",
            "decision",
            "reason",
            "allowed_roles",
        }

        missing_fields = required_fields - set(policy)

        if missing_fields:
            raise ValueError(
                f"Policy is missing required fields: "
                f"{sorted(missing_fields)}"
            )

        if policy["decision"] not in VALID_DECISIONS:
            raise ValueError(
                f"Policy '{policy['id']}' contains an invalid decision: "
                f"{policy['decision']}"
            )

        if policy["id"] in policy_ids:
            raise ValueError(
                f"Duplicate policy ID: {policy['id']}"
            )

        policy_ids.add(policy["id"])

    return policies


def find_policy_for_activity(
    activity: str,
    policies: list[dict],
) -> dict:
    """Return the governance policy for the requested activity."""

    matching_policies = [
        policy
        for policy in policies
        if policy["activity"] == activity
    ]

    if not matching_policies:
        raise ValueError(
            f"No governance policy exists for activity '{activity}'."
        )

    if len(matching_policies) > 1:
        raise ValueError(
            f"Multiple governance policies exist for activity '{activity}'."
        )

    return matching_policies[0]