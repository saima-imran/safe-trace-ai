"""Authorize or block AI execution using a governance policy."""


def evaluate_ai_authorization(
    policy: dict,
    reviewer_role: str | None = None,
    authorization_granted: bool = False,
) -> dict:
    """Evaluate whether AI may execute under the selected policy."""

    decision = policy["decision"]

    if decision == "AI_PERMITTED":
        return {
            "policy_id": policy["id"],
            "status": "PERMITTED",
            "ai_execution_allowed": True,
            "reviewer_role": reviewer_role,
            "reason": policy["reason"],
        }

    if decision == "AI_RESTRICTED":
        return {
            "policy_id": policy["id"],
            "status": "RESTRICTED",
            "ai_execution_allowed": False,
            "reviewer_role": reviewer_role,
            "reason": policy["reason"],
        }

    if decision == "HUMAN_AUTHORIZATION_REQUIRED":
        allowed_roles = policy["allowed_roles"]

        if reviewer_role not in allowed_roles:
            return {
                "policy_id": policy["id"],
                "status": "UNAUTHORIZED_ROLE",
                "ai_execution_allowed": False,
                "reviewer_role": reviewer_role,
                "reason": (
                    "The selected role is not authorized to permit "
                    "AI use for this activity."
                ),
            }

        if not authorization_granted:
            return {
                "policy_id": policy["id"],
                "status": "AUTHORIZATION_REQUIRED",
                "ai_execution_allowed": False,
                "reviewer_role": reviewer_role,
                "reason": (
                    "An authorized human must explicitly permit "
                    "AI use before execution."
                ),
            }

        return {
            "policy_id": policy["id"],
            "status": "AUTHORIZED",
            "ai_execution_allowed": True,
            "reviewer_role": reviewer_role,
            "reason": (
                "AI use was explicitly authorized by an allowed role."
            ),
        }

    raise ValueError(
        f"Unsupported governance decision: {decision}"
    )

