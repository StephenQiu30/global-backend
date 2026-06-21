"""Tests for installation request DTO validation."""

import pytest
from pydantic import ValidationError

from app.dto.installation import (
    ListInstallationRepositoriesRequest,
    VerifyInstallationRequest,
)


class TestVerifyInstallationRequest:
    def test_valid_data(self):
        request = VerifyInstallationRequest(installation_id=12345)
        assert request.installation_id == 12345

    def test_missing_installation_id(self):
        with pytest.raises(ValidationError):
            VerifyInstallationRequest()


class TestListInstallationRepositoriesRequest:
    def test_valid_data(self):
        request = ListInstallationRepositoriesRequest(installation_id=67890)
        assert request.installation_id == 67890

    def test_missing_installation_id(self):
        with pytest.raises(ValidationError):
            ListInstallationRepositoriesRequest()
