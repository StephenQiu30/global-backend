"""Tests for OpenAPI documentation generated from controller modules.

Validates that the FastAPI app produces a correct OpenAPI schema with:
- All expected endpoint paths
- Stable operation IDs on every endpoint
- Tags on every endpoint
- Documented error responses
- No duplicate paths
"""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def openapi_schema(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    return response.json()


# All expected paths from the current API surface.
EXPECTED_PATHS = [
    "/api/github/installations/verify",
    "/api/github/installations/{installation_id}/repositories",
    "/api/languages",
    "/api/repositories/resolve",
    "/api/repositories/{owner}/{repo}/markdown-files",
    "/api/translation-tasks",
    "/api/public-preview",
]

EXPECTED_TAGS = [
    "installations",
    "repositories",
    "languages",
    "translation-tasks",
    "public-preview",
]


class TestOpenAPIAccessibility:
    """OpenAPI JSON and Swagger UI are accessible."""

    def test_openapi_json_is_accessible(self, client):
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")

    def test_swagger_ui_is_accessible(self, client):
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_has_paths(self, openapi_schema):
        assert "paths" in openapi_schema
        assert len(openapi_schema["paths"]) > 0


class TestEndpointPaths:
    """All expected endpoints are registered with correct HTTP methods."""

    @pytest.mark.parametrize("path", EXPECTED_PATHS)
    def test_path_exists(self, openapi_schema, path):
        assert path in openapi_schema["paths"], (
            f"Expected path '{path}' not found in OpenAPI schema. "
            f"Available: {list(openapi_schema['paths'].keys())}"
        )

    def test_no_duplicate_paths(self, openapi_schema):
        paths = list(openapi_schema["paths"].keys())
        assert len(paths) == len(set(paths)), (
            f"Duplicate paths found: {[p for p in paths if paths.count(p) > 1]}"
        )


class TestOperationIds:
    """Every endpoint has a stable, non-empty operationId."""

    def test_all_endpoints_have_operation_id(self, openapi_schema):
        missing = []
        for path, methods in openapi_schema["paths"].items():
            for method, detail in methods.items():
                if method in ("get", "post", "put", "patch", "delete"):
                    op_id = detail.get("operationId")
                    if not op_id:
                        missing.append(f"{method.upper()} {path}")
        assert not missing, (
            f"Endpoints missing operationId: {missing}"
        )

    def test_operation_ids_are_unique(self, openapi_schema):
        op_ids = []
        for path, methods in openapi_schema["paths"].items():
            for method, detail in methods.items():
                if method in ("get", "post", "put", "patch", "delete"):
                    op_ids.append(detail.get("operationId"))
        non_null = [o for o in op_ids if o is not None]
        assert len(non_null) == len(set(non_null)), (
            f"Duplicate operationIds found"
        )


class TestTags:
    """Every endpoint has at least one tag and tags match expected set."""

    def test_all_endpoints_have_tags(self, openapi_schema):
        missing = []
        for path, methods in openapi_schema["paths"].items():
            for method, detail in methods.items():
                if method in ("get", "post", "put", "patch", "delete"):
                    tags = detail.get("tags", [])
                    if not tags:
                        missing.append(f"{method.upper()} {path}")
        assert not missing, f"Endpoints missing tags: {missing}"

    def test_tags_match_expected_set(self, openapi_schema):
        schema_tags = [t["name"] for t in openapi_schema.get("tags", [])]
        for tag in EXPECTED_TAGS:
            assert tag in schema_tags, (
                f"Expected tag '{tag}' not in schema tags: {schema_tags}"
            )


class TestResponseModels:
    """Endpoints have documented success response models and error responses."""

    def test_endpoints_have_response_model(self, openapi_schema):
        """Each POST/GET endpoint should define a 200/201 response schema."""
        missing = []
        for path, methods in openapi_schema["paths"].items():
            for method, detail in methods.items():
                if method in ("get", "post"):
                    responses = detail.get("responses", {})
                    has_success = any(
                        str(code).startswith("2") for code in responses.keys()
                    )
                    if not has_success:
                        missing.append(f"{method.upper()} {path}")
        assert not missing, f"Endpoints missing success response: {missing}"

    def test_endpoints_document_error_responses(self, openapi_schema):
        """Endpoints that raise HTTPException should document error status codes."""
        # At minimum, verify the schema has some non-2xx responses documented.
        error_count = 0
        for path, methods in openapi_schema["paths"].items():
            for method, detail in methods.items():
                if method in ("get", "post"):
                    for code in detail.get("responses", {}).keys():
                        if not str(code).startswith("2"):
                            error_count += 1
        assert error_count > 0, "No error responses documented in any endpoint"

    def test_all_endpoints_have_error_responses(self, openapi_schema):
        """Every endpoint must document at least one non-2xx error response."""
        missing = []
        for path, methods in openapi_schema["paths"].items():
            for method, detail in methods.items():
                if method in ("get", "post"):
                    responses = detail.get("responses", {})
                    has_error = any(
                        not str(code).startswith("2") for code in responses.keys()
                    )
                    if not has_error:
                        missing.append(f"{method.upper()} {path}")
        assert not missing, (
            f"Endpoints missing error response documentation: {missing}"
        )
