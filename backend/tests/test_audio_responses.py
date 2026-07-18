from unittest.mock import MagicMock, patch

@patch("app.routers.responses.get_groq_client")
def test_submit_audio_response(mock_get_client, client, seeded_question):
    mock_client= MagicMock()
    mock_client.audio.transcriptions.create.return_value="I'd use hybrid search with reranking."
    mock_get_client.return_value = mock_client

    session_resp = client.post("/sessions/", json={"role":"AI Engineer"})
    session_id = session_resp.json()["id"]

    fake_audio = b"fake audio bytes for testing"
    result = client.post(
        "/responses/audio",
        data={"session_id": session_id, "question_id": seeded_question.id},
        files={"audio": ("test.wav", fake_audio, "audio/wav")},
    )
    assert result.status_code == 200
    assert result.json()["answer_text"] == "I'd use hybrid search with reranking."


@patch("app.routers.responses.get_groq_client")
def test_submit_audio_response_transcription_failure(mock_get_client, client, seeded_question):
    mock_client = MagicMock()
    mock_client.audio.transcriptions.create.side_effect = Exception("Groq API timeout")
    mock_get_client.return_value = mock_client

    session_resp = client.post("/sessions/", json={"role": "AI Engineer"})
    session_id = session_resp.json()["id"]

    result = client.post(
        "/responses/audio",
        data={"session_id": session_id, "question_id": seeded_question.id},
        files={"audio": ("test.wav", b"fake bytes", "audio/wav")},
    )
    assert result.status_code == 502