"""Streamlit page for deterministic AI-governance decisions."""

from pathlib import Path
import sys

import streamlit as st

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1]),
)

from governance_authorization import evaluate_ai_authorization
from governance_policy import (
    find_policy_for_activity,
    load_governance_policies,
)


st.set_page_config(
    page_title="SafeTrace-AI Governance",
    page_icon="🛡️",
    layout="wide",
)


st.title("SafeTrace-AI Governance")

st.caption(
    "Deterministic policies define whether AI assistance is "
    "permitted, requires human authorization, or is restricted."
)

st.info(
    "This page evaluates governance policy before any AI execution. "
    "It does not call Ollama."
)


policies = load_governance_policies()


st.header("1. Governance Policy Overview")

policy_rows = [
    {
        "Policy ID": policy["id"],
        "Version": policy["version"],
        "Activity": policy["activity"],
        "Decision": policy["decision"],
    }
    for policy in policies
]

st.dataframe(
    policy_rows,
    use_container_width=True,
    hide_index=True,
)


st.header("2. Select an Activity")

activity_labels = {
    "summarize_low_consequence_change": (
        "Summarize a low-consequence change"
    ),
    "explain_safety_requirement_impact": (
        "Explain a safety-requirement impact"
    ),
    "modify_authoritative_trace_link": (
        "Modify an authoritative trace link"
    ),
}

selected_activity = st.selectbox(
    "Engineering activity",
    options=list(activity_labels),
    format_func=lambda activity: activity_labels[activity],
)

selected_policy = find_policy_for_activity(
    selected_activity,
    policies,
)


st.subheader("Applicable Policy")

policy_col_1, policy_col_2 = st.columns(2)

with policy_col_1:
    st.write("**Policy ID**")
    st.code(
        selected_policy["id"],
        language=None,
    )

    st.write("**Policy version**")
    st.code(
        selected_policy["version"],
        language=None,
    )

with policy_col_2:
    st.write("**Policy decision**")
    st.code(
        selected_policy["decision"],
        language=None,
    )

    st.write("**Allowed roles**")

    if selected_policy["allowed_roles"]:
        for role in selected_policy["allowed_roles"]:
            st.code(
                role,
                language=None,
            )
    else:
        st.write("No role may authorize this activity.")

st.write("**Policy reason**")
st.write(selected_policy["reason"])


st.header("3. Human Authorization")

role_options = [
    "No role selected",
    "requirements_engineer",
    "verification_engineer",
    "safety_engineer",
    "guest",
]

selected_role_label = st.selectbox(
    "Reviewer role",
    options=role_options,
)

reviewer_role = (
    None
    if selected_role_label == "No role selected"
    else selected_role_label
)

authorization_granted = st.checkbox(
    "I explicitly authorize bounded AI assistance for this activity."
)


authorization = evaluate_ai_authorization(
    selected_policy,
    reviewer_role=reviewer_role,
    authorization_granted=authorization_granted,
)


st.header("4. Governance Decision")

status = authorization["status"]

if status in {"PERMITTED", "AUTHORIZED"}:
    st.success(
        f"{status}: AI execution is allowed for this activity."
    )
elif status in {
    "AUTHORIZATION_REQUIRED",
    "UNAUTHORIZED_ROLE",
}:
    st.warning(
        f"{status}: AI execution remains blocked."
    )
else:
    st.error(
        f"{status}: AI execution is restricted."
    )

decision_col_1, decision_col_2 = st.columns(2)

with decision_col_1:
    st.write("**Policy applied**")
    st.code(
        authorization["policy_id"],
        language=None,
    )

    st.write("**Reviewer role**")
    st.code(
        authorization["reviewer_role"] or "None",
        language=None,
    )

with decision_col_2:
    st.write("**Authorization status**")
    st.code(
        authorization["status"],
        language=None,
    )

    st.write("**AI execution allowed**")
    st.code(
        str(authorization["ai_execution_allowed"]),
        language=None,
    )

st.write("**Decision reason**")
st.write(authorization["reason"])


st.divider()

st.caption(
    "The governance decision is produced by deterministic policy "
    "logic. The LLM does not select or modify the policy."
)
