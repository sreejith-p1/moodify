import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_analyze_happy():
    response = client.post("/analyze", json={"text": "I am feeling great!"})
    assert response.status_code == 200
    assert response.json()["emotion"] in ["happy", "very happy"]

def test_analyze_sad():
    response = client.post("/analyze", json={"text": "I am feeling terrible."})
    assert response.status_code == 200
    assert response.json()["emotion"] in ["sad", "very sad"]

def test_analyze_empty():
    response = client.post("/analyze", json={"text": "   "})
    assert response.status_code == 400
    assert "error" in response.json()
