from fastapi.testclient import TestClient

from src.app.main import app

client = TestClient(app)


def test_get_question_returns_a_question():
    response = client.get("/questions", params={"difficulty": "easy"})
    assert response.status_code == 200
    body = response.json()
    assert "id" in body
    assert body["difficulty"] == "easy"


def test_submit_correct_answer():
    question = client.get("/questions", params={"difficulty": "easy"}).json()
    response = client.post(
        "/answers",
        json={"question_id": question["id"], "candidate_sql": question["expected_sql"]},
    )
    assert response.status_code == 200
    assert response.json()["correct"] is True


def test_submit_answer_unknown_question_id():
    response = client.post(
        "/answers", json={"question_id": 999999, "candidate_sql": "SELECT 1"}
    )
    assert response.status_code == 404
