import json
from unittest.mock import MagicMock, patch


def make_fake_groq_response(overall_score=7.5, technical=8, clarity=7, depth=7,
                             feedback="Solid answer with room to improve on depth."):
    fake_content = json.dumps({
        "criteria_scores": {
            "technical_accuracy": technical,
            "clarity": clarity,
            "depth": depth,
        },
        "overall_score": overall_score,
        "feedback": feedback,
    })
    fake_completion = MagicMock()
    fake_completion.choices[0].message.content = fake_content
    return fake_completion


def _setup_response(client, seeded_question):
    session_resp = client.post(
        "/sessions/",
        json={"role": "AI Engineer", "candidate_name": "Ada"},
    )
    session_id = session_resp.json()["id"]

    resp = client.post("/responses/", json={
        "session_id": session_id,
        "question_id": seeded_question.id,
        "answer_text": "I'd use hybrid search with reranking and strict grounding.",
    })
    return resp.json()["id"]


@patch("app.routers.evaluations.get_groq_client")
def test_create_evaluation_success(mock_get_client, client, seeded_question):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = make_fake_groq_response()
    mock_get_client.return_value = mock_client

    response_id = _setup_response(client, seeded_question)

    result = client.post(f"/evaluations/{response_id}")
    assert result.status_code == 200
    data = result.json()
    assert data["overall_score"] == 7.5
    assert data["criteria_scores"]["technical_accuracy"] == 8


@patch("app.routers.evaluations.get_groq_client")
def test_create_evaluation_malformed_llm_output(mock_get_client, client, seeded_question):
    """Simulates Groq returning JSON that doesn't match our schema -- e.g. score out of range."""
    fake_completion = MagicMock()
    fake_completion.choices[0].message.content = json.dumps({
        "criteria_scores": {"technical_accuracy": 15, "clarity": 7, "depth": 7},  # invalid: >10
        "overall_score": 7.5,
        "feedback": "test",
    })
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = fake_completion
    mock_get_client.return_value = mock_client

    response_id = _setup_response(client, seeded_question)

    result = client.post(f"/evaluations/{response_id}")
    assert result.status_code == 502


def test_evaluate_nonexistent_response(client):
    result = client.post("/evaluations/999")
    assert result.status_code == 404


@patch("app.routers.evaluations.get_groq_client")
def test_cannot_evaluate_twice(mock_get_client, client, seeded_question):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = make_fake_groq_response()
    mock_get_client.return_value = mock_client

    response_id = _setup_response(client, seeded_question)
    client.post(f"/evaluations/{response_id}")

    second_attempt = client.post(f"/evaluations/{response_id}")
    assert second_attempt.status_code == 400

@patch("app.routers.evaluations.get_groq_client")
def test_evaluation_repairs_after_bad_first_attempt(mock_get_client, client, seeded_question):
    bad_response = MagicMock()
    bad_response.choices[0].message.content = json.dumps({
        "criteria_scores": {"technical_accuracy": 15, "clarity": 7, "depth": 7},  # invalid
        "overall_score": 7.5,
        "feedback": "test",
    })
    good_response = make_fake_groq_response(overall_score=6.0, technical=6, clarity=6, depth=6)

    mock_client = MagicMock()
    # first call returns bad output, second call (the repair) returns valid output
    mock_client.chat.completions.create.side_effect = [bad_response, good_response]
    mock_get_client.return_value = mock_client

    response_id = _setup_response(client, seeded_question)
    result = client.post(f"/evaluations/{response_id}")

    assert result.status_code == 200
    assert result.json()["overall_score"] == 6.0
    assert mock_client.chat.completions.create.call_count == 2