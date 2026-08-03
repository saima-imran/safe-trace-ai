from pathlib import Path
import sys
from unittest.mock import Mock

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from llm_analyzer import build_prompt, generate_explanation


def test_build_prompt_contains_verified_facts() -> None:
    """The prompt should preserve the deterministic engineering facts."""

    prompt = build_prompt(
        old_requirement=(
            "The warning shall activate within 500 ms."
        ),
        new_requirement=(
            "The warning shall activate within 200 ms."
        ),
        evidence_status="RE_VERIFICATION_REQUIRED",
        deterministic_reason=(
            "The previous measured response time was 420 ms, "
            "which exceeds the updated 200 ms requirement."
        ),
    )

    assert "500 ms" in prompt
    assert "200 ms" in prompt
    assert "420 ms" in prompt
    assert "RE_VERIFICATION_REQUIRED" in prompt
    assert "Never claim ISO 26262 compliance" in prompt


def test_generate_explanation_returns_ollama_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The analyzer should return the explanation received from Ollama."""

    expected_explanation = (
        "The previous result passed the 500 ms requirement "
        "but does not satisfy the updated 200 ms requirement."
    )

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "response": expected_explanation,
    }

    def mock_post(
        url: str,
        json: dict,
        timeout: int,
    ) -> Mock:
        assert url == "http://localhost:11434/api/generate"
        assert json["model"] == "llama3.2:3b"
        assert json["stream"] is False
        assert timeout == 120

        return mock_response

    monkeypatch.setattr(requests, "post", mock_post)

    explanation = generate_explanation("Example prompt")

    assert explanation == expected_explanation


def test_generate_explanation_rejects_empty_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An empty Ollama response should raise a clear error."""

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "response": "   ",
    }

    monkeypatch.setattr(
        requests,
        "post",
        lambda *args, **kwargs: mock_response,
    )

    with pytest.raises(
        RuntimeError,
        match="Ollama returned an empty response",
    ):
        generate_explanation("Example prompt")

        