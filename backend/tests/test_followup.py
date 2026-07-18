from unittest.mock import patch


def _create_response(client, seeded_question):
    session_result = client.post("/sessions/", json={"role": "AI Engineer"})
    session_id = session_result.json()["id"]

    response_result = client.post(
        "/responses/",
        json={
            "session_id": session_id,
            "question_id": seeded_question.id,
            "answer_text": "I would use hybrid retrieval with reranking.",
        },
    )
    return response_result.json()["id"]


@patch("app.routers.responses.generate_followup")
@patch("app.routers.responses.get_groq_client")
def test_generate_follow_up_at_frontend_route(
    mock_get_client,
    mock_generate_followup,
    client,
    seeded_question,
):
    mock_client = object()
    mock_get_client.return_value = mock_client
    mock_generate_followup.return_value = {
        "should_follow_up": True,
        "follow_up_question": "How would you measure retrieval quality?",
        "reasoning": "The answer did not explain its evaluation strategy.",
    }
    response_id = _create_response(client, seeded_question)

    result = client.post(f"/responses/{response_id}/follow-up")

    assert result.status_code == 200
    assert result.json() == mock_generate_followup.return_value
    mock_generate_followup.assert_called_once_with(
        mock_client,
        seeded_question.text,
        "I would use hybrid retrieval with reranking.",
    )


def test_follow_up_for_missing_response(client):
    result = client.post("/responses/999/follow-up")

    assert result.status_code == 404
    assert result.json()["detail"] == "Response not found"
