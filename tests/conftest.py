"""Pytest configuration and fixtures."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from check_filter import CheckResult, DomainChecker, FilterStatus


@pytest.fixture
def domain_checker() -> DomainChecker:
    """Create a DomainChecker instance for testing."""
    return DomainChecker()


@pytest.fixture
def mock_domain_checker() -> MagicMock:
    """Create a mock DomainChecker for unit testing."""
    mock = MagicMock(spec=DomainChecker)
    mock.acheck = AsyncMock()
    mock.acheck_many = AsyncMock()
    return mock


@pytest.fixture
def free_check_result() -> CheckResult:
    """Create a CheckResult for a free domain."""
    return CheckResult(
        domain="example.com",
        status=FilterStatus.FREE,
        ips=frozenset({"93.184.216.34"}),
    )


@pytest.fixture
def blocked_check_result() -> CheckResult:
    """Create a CheckResult for a blocked domain."""
    return CheckResult(
        domain="blocked.example.com",
        status=FilterStatus.BLOCKED,
        ips=frozenset({"10.10.34.34"}),
    )


@pytest.fixture
def error_check_result() -> CheckResult:
    """Create a CheckResult for an error case."""
    return CheckResult(
        domain="error.example.com",
        status=FilterStatus.ERROR,
        error="DNS query timeout",
    )


@pytest.fixture
def temp_domain_file(tmp_path: Path) -> Path:
    """Create a temporary file with test domains."""
    file_path = tmp_path / "test_domains.txt"
    file_path.write_text(
        "# Test domains file\nexample.com\ngoogle.com\n\n# Comment line\ngithub.com\n"
    )
    return file_path


@pytest.fixture
def empty_domain_file(tmp_path: Path) -> Path:
    """Create an empty temporary domain file."""
    file_path = tmp_path / "empty_domains.txt"
    file_path.write_text("")
    return file_path


@pytest.fixture
def invalid_domain_file(tmp_path: Path) -> Path:
    """Create a temporary file with invalid domains."""
    file_path = tmp_path / "invalid_domains.txt"
    file_path.write_text("valid.com\ninvalid\nalso-valid.org\nnot_valid\n")
    return file_path


@pytest.fixture(scope="session")
def sample_domains() -> list[str]:
    """Provide a list of sample domains for testing."""
    return [
        "example.com",
        "google.com",
        "github.com",
        "stackoverflow.com",
    ]


@pytest.fixture(scope="session")
def sample_blocked_domains() -> list[str]:
    """Provide a list of typically blocked domains in Iran."""
    return [
        "instagram.com",
        "twitter.com",
        "facebook.com",
    ]


@pytest.fixture(scope="session")
def invalid_domains() -> list[str]:
    """Provide a list of invalid domain names."""
    return [
        "",
        "invalid",
        "-invalid.com",
        "invalid-.com",
        ".com",
        "   ",
    ]
