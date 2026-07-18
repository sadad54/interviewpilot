def test_create_session(client):
    response = client.post("/sessions/", json={"role": "AI Engineer", "candidate_name": "Adnan"})
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "AI Engineer"
    assert data["status"] == "in_progress"
    assert "id" in data


def test_get_session_not_found(client):
    response = client.get("/sessions/999")
    assert response.status_code == 404


def test_submit_response_invalid_session(client, seeded_question):
    response = client.post("/responses/", json={
        "session_id": 999,
        "question_id": seeded_question.id,
        "answer_text": "test answer",
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"