from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))

from main import run_analysis


st.set_page_config(
    page_title="SafeTrace-AI",
    page_icon="🛡️",
    layout="wide",
)


st.title("SafeTrace-AI")

st.caption(
    "AI-assisted semantic change-impact analysis for "
    "safety requirements and verification evidence"
)

st.info(
    "Deterministic Python performs change detection, traceability, "
    "and evidence assessment. The local LLM provides advisory "
    "semantic explanations for human review."
)


with st.sidebar:
    st.header("Analysis Options")

    use_llm = st.checkbox(
        "Use Ollama explanations",
        value=True,
    )

    run_button = st.button(
        "Run SafeTrace-AI Analysis",
        type="primary",
    )


if run_button:
    with st.spinner("Analyzing requirements and evidence..."):
        results = run_analysis(
            use_llm=use_llm,
        )

    st.success(
        f"Analysis complete. "
        f"{len(results)} changed requirements found."
    )

    for result in results:
        st.divider()

        st.subheader(
            f"{result['requirement_id']} — "
            f"{result['title']}"
        )

        status = result["status"]

        if status == "RE_VERIFICATION_REQUIRED":
            st.error(status)
        else:
            st.warning(status)

        old_col, new_col = st.columns(2)

        with old_col:
            st.markdown("### Old Requirement")
            st.write(
                result["old_requirement"]
            )

        with new_col:
            st.markdown("### New Requirement")
            st.write(
                result["new_requirement"]
            )

        st.markdown("### Deterministic Finding")

        st.write(
            result["reason"]
        )

        st.markdown("### Affected Verification Evidence")

        evidence_col_1, evidence_col_2 = st.columns(2)

        with evidence_col_1:
            st.markdown("**Test Cases**")

            if result["test_case_ids"]:
                for test_case_id in result["test_case_ids"]:
                    st.code(
                        test_case_id,
                        language=None,
                    )
            else:
                st.write("None")

        with evidence_col_2:
            st.markdown("**Test Results**")

            if result["test_result_ids"]:
                for test_result_id in result["test_result_ids"]:
                    st.code(
                        test_result_id,
                        language=None,
                    )
            else:
                st.write("None")

        st.markdown("### LLM Advisory Explanation")

        if result["llm_explanation"]:
            st.write(
                result["llm_explanation"]
            )
        else:
            st.info(
                "LLM analysis was disabled for this run."
            )

        st.caption(
            "AI-generated explanations are advisory and "
            "require human engineering review."
        )

        