from uuid import uuid4


def _create_and_start(client):
    created = client.post(
        "/sessions/",
        json={
            "role": "AI Engineer",
            "candidate_name": "Ada",
            "seniority": "senior",
            "job_description": "Build reliable retrieval and evaluation systems.",
        },
    )
    assert created.status_code == 200
    public_id = created.json()["public_id"]
    started = client.post(f"/sessions/{public_id}/start")
    assert started.status_code == 200
    return public_id, started.json()


def _answer(client, public_id, question_id, text="A concise answer that needs a deeper explanation.", request_id=None):
    return client.post(
        f"/sessions/{public_id}/answers",
        json={
            "question_id": question_id,
            "answer_text": text,
            "client_request_id": request_id or str(uuid4()),
        },
    )


def test_plans_five_competencies_and_resumes_state(client):
    public_id, state = _create_and_start(client)

    assert state["status"] == "in_progress"
    assert len(state["plan_categories"]) == 5
    assert len(set(state["plan_categories"])) == 5
    assert state["current_question"]["kind"] == "primary"

    resumed = client.get(f"/sessions/{public_id}/state")
    assert resumed.status_code == 200
    assert resumed.json()["current_question"]["id"] == state["current_question"]["id"]


def test_short_answer_gets_one_answerable_probe_then_advances(client):
    public_id, state = _create_and_start(client)
    primary = state["current_question"]

    probed = _answer(client, public_id, primary["id"])
    assert probed.status_code == 200
    assert probed.json()["action"] == "probe"
    follow_up = probed.json()["current_question"]
    assert follow_up["kind"] == "follow_up"
    assert follow_up["parent_question_id"] == primary["id"]

    advanced = _answer(client, public_id, follow_up["id"], "The trade-off is latency versus retrieval quality, measured with recall and groundedness.")
    assert advanced.status_code == 200
    assert advanced.json()["action"] == "advance"
    assert advanced.json()["current_question"]["kind"] == "primary"
    assert advanced.json()["current_question"]["sequence_index"] == 1


def test_idempotent_answer_does_not_create_another_turn(client):
    public_id, state = _create_and_start(client)
    request_id = str(uuid4())
    first = _answer(client, public_id, state["current_question"]["id"], request_id=request_id)
    duplicate = _answer(client, public_id, state["current_question"]["id"], request_id=request_id)

    assert first.status_code == 200
    assert duplicate.status_code == 200
    assert duplicate.json()["action"] == "duplicate"
    resumed = client.get(f"/sessions/{public_id}/state").json()
    assert resumed["progress"]["answered_turns"] == 1


def test_full_interview_completes_with_report_and_bounded_probes(client):
    public_id, state = _create_and_start(client)
    actions = []
    while state["status"] == "in_progress":
        result = _answer(client, public_id, state["current_question"]["id"])
        assert result.status_code == 200
        actions.append(result.json()["action"])
        state = client.get(f"/sessions/{public_id}/state").json()
        assert len(actions) <= 10

    assert actions.count("probe") == 5
    assert actions[-1] == "complete"
    assert state["progress"]["completed_primary"] == 5
    assert state["progress"]["answered_turns"] == 10
    assert state["report_token"]

    report = client.get(f"/sessions/{public_id}/report")
    assert report.status_code == 200
    data = report.json()
    assert data["coverage_summary"]["primary_answered"] == 5
    assert data["coverage_summary"]["follow_ups_answered"] == 5
    assert len(data["evidence"]) == 10

    shared = client.get(f"/sessions/reports/shared/{data['share_token']}")
    assert shared.status_code == 200
    assert shared.json()["session_public_id"] == public_id


def test_early_completion_requires_an_answer_and_builds_partial_report(client):
    public_id, state = _create_and_start(client)
    empty_finish = client.post(f"/sessions/{public_id}/complete")
    assert empty_finish.status_code == 409

    _answer(client, public_id, state["current_question"]["id"])
    finished = client.post(f"/sessions/{public_id}/complete")
    assert finished.status_code == 200
    assert finished.json()["coverage_summary"]["primary_answered"] == 1


def test_demo_scores_are_disclosed_in_report(client):
    public_id, state = _create_and_start(client)
    answered = _answer(client, public_id, state["current_question"]["id"])
    assert "Demo heuristic" in answered.json()["decision_summary"]
    report = client.post(f"/sessions/{public_id}/complete").json()
    assert report["coverage_summary"]["demo_heuristic_scores"] == 1
    assert "do not assess technical correctness" in report["summary"]


def test_stateful_audio_without_provider_does_not_advance(client):
    public_id, state = _create_and_start(client)
    response = client.post(
        f"/sessions/{public_id}/answers/audio",
        data={"question_id": state["current_question"]["id"], "client_request_id": str(uuid4())},
        files={"audio": ("answer.webm", b"fixture-audio", "audio/webm")},
    )
    assert response.status_code == 503
    resumed = client.get(f"/sessions/{public_id}/state").json()
    assert resumed["progress"]["answered_turns"] == 0
