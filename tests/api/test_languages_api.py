"""Tests for GET /api/languages endpoint."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


class TestGetLanguages:
    """Tests for GET /api/languages endpoint."""

    def test_returns_200(self, client):
        response = client.get("/api/languages")
        assert response.status_code == 200

    def test_returns_envelope_with_list(self, client):
        response = client.get("/api/languages")
        data = response.json()
        assert data["code"] == "SUCCESS"
        assert data["message"] == "OK"
        assert "trace_id" in data
        assert isinstance(data["data"], list)

    def test_returns_eight_languages(self, client):
        response = client.get("/api/languages")
        data = response.json()
        assert len(data["data"]) == 8

    def test_each_language_has_code_and_label(self, client):
        response = client.get("/api/languages")
        data = response.json()
        for lang in data["data"]:
            assert "code" in lang
            assert "label" in lang
            assert isinstance(lang["code"], str)
            assert isinstance(lang["label"], str)

    def test_contains_zh_cn(self, client):
        response = client.get("/api/languages")
        data = response.json()
        codes = [lang["code"] for lang in data["data"]]
        assert "zh-CN" in codes

    def test_contains_en(self, client):
        response = client.get("/api/languages")
        data = response.json()
        codes = [lang["code"] for lang in data["data"]]
        assert "en" in codes

    def test_zh_cn_label(self, client):
        response = client.get("/api/languages")
        data = response.json()
        zh_cn = next(lang for lang in data["data"] if lang["code"] == "zh-CN")
        assert zh_cn["label"] == "简体中文"
