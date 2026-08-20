from pathlib import Path
import sys

import pytest

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

import main


def test_llm_is_blocked_without_authorized_role(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The analysis must not call the LLM without an authorized role."""

    llm_calls = []

    def fake_generate_explanation(prompt: str) -> str:
        llm_calls.append(prompt)
        return "This function should not have been called."

    monkeypatch.setattr(
        main,
        "generate_explanation",
        fake_generate_explanation,
    )

    results = main.run_analysis(
        use_llm=True,
    )

    assert llm_calls == []

    for result in results:
        assert result["governance_status"] == "UNAUTHORIZED_ROLE"
        assert result["ai_execution_allowed"] is False
        assert result["llm_explanation"] is None


def test_llm_is_blocked_until_authorization_is_granted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An allowed role must still explicitly authorize AI execution."""

    llm_calls = []

    def fake_generate_explanation(prompt: str) -> str:
        llm_calls.append(prompt)
        return "This function should not have been called."

    monkeypatch.setattr(
        main,
        "generate_explanation",
        fake_generate_explanation,
    )

    results = main.run_analysis(
        use_llm=True,
        reviewer_role="requirements_engineer",
        authorization_granted=False,
    )

    assert llm_calls == []

    for result in results:
        assert (
            result["governance_status"]
            == "AUTHORIZATION_REQUIRED"
        )
        assert result["ai_execution_allowed"] is False
        assert result["llm_explanation"] is None


def test_llm_runs_after_valid_authorization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An authorized role may enable the bounded LLM explanation."""

    llm_calls = []

    def fake_generate_explanation(prompt: str) -> str:
        llm_calls.append(prompt)
        return "Mocked advisory explanation."

    monkeypatch.setattr(
        main,
        "generate_explanation",
        fake_generate_explanation,
    )

    results = main.run_analysis(
        use_llm=True,
        reviewer_role="verification_engineer",
        authorization_granted=True,
    )

    assert len(llm_calls) == 4

    for result in results:
        assert result["governance_status"] == "AUTHORIZED"
        assert result["ai_execution_allowed"] is True
        assert (
            result["llm_explanation"]
            == "Mocked advisory explanation."
        )


def test_disabled_ai_is_recorded_as_not_requested() -> None:
    """A deterministic-only run should record that AI was not requested."""

    results = main.run_analysis(
        use_llm=False,
    )

    for result in results:
        assert result["governance_status"] == "AI_NOT_REQUESTED"
        assert result["ai_execution_allowed"] is False
        assert result["llm_explanation"] is None

        