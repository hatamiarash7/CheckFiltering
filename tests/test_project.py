"""Tests for package metadata and exports."""

import check_filter
from check_filter import (
    CheckResult,
    DomainChecker,
    FilterStatus,
    __all__,
    __app_name__,
    __author__,
    __description__,
    __epilog__,
    __version__,
)


class TestPackageMetadata:
    """Tests for package metadata."""

    def test_app_name(self):
        """Test application name."""
        assert __app_name__ == "check-filter"

    def test_version_format(self):
        """Test version follows semantic versioning."""
        parts = __version__.split(".")
        assert len(parts) >= 2  # At minimum major.minor
        assert all(part.isdigit() for part in parts[:2])

    def test_author(self):
        """Test author information is present."""
        assert __author__
        assert "Arash Hatami" in __author__

    def test_description(self):
        """Test description is present and meaningful."""
        assert __description__
        assert "Iran" in __description__ or "filter" in __description__.lower()

    def test_epilog(self):
        """Test epilog contains expected content."""
        assert __epilog__
        assert "Iran" in __epilog__


class TestPackageExports:
    """Tests for package exports."""

    def test_all_exports(self):
        """Test __all__ contains expected exports."""
        expected = {
            "DomainChecker",
            "CheckResult",
            "FilterStatus",
            "__app_name__",
            "__description__",
            "__version__",
            "__author__",
            "__epilog__",
        }
        assert expected <= set(__all__)

    def test_domain_checker_importable(self):
        """Test DomainChecker is importable from package root."""
        assert DomainChecker is not None
        assert callable(DomainChecker)

    def test_check_result_importable(self):
        """Test CheckResult is importable from package root."""
        assert CheckResult is not None

    def test_filter_status_importable(self):
        """Test FilterStatus is importable from package root."""
        assert FilterStatus is not None
        assert hasattr(FilterStatus, "FREE")
        assert hasattr(FilterStatus, "BLOCKED")

    def test_submodules_accessible(self):
        """Test that submodules are accessible."""
        from check_filter import check, cli, utils

        assert check is not None
        assert cli is not None
        assert utils is not None


class TestVersionConsistency:
    """Tests for version consistency."""

    def test_version_in_init(self):
        """Test version is defined in __init__."""
        assert hasattr(check_filter, "__version__")

    def test_version_matches_pyproject(self):
        """Test version matches pyproject.toml (informational)."""
        # This test documents expected version
        # Update this when releasing new versions
        assert __version__ == "2.5.0"


class TestClassAvailability:
    """Tests for class availability and basic functionality."""

    def test_domain_checker_instantiation(self):
        """Test DomainChecker can be instantiated."""
        checker = DomainChecker()
        assert checker is not None
        assert hasattr(checker, "acheck")
        assert hasattr(checker, "acheck_many")

    def test_check_result_instantiation(self):
        """Test CheckResult can be instantiated."""
        result = CheckResult(domain="test.com", status=FilterStatus.FREE)
        assert result.domain == "test.com"
        assert result.status == FilterStatus.FREE

    def test_filter_status_values(self):
        """Test FilterStatus has expected values."""
        assert FilterStatus.FREE.value == "free"
        assert FilterStatus.BLOCKED.value == "blocked"
        assert FilterStatus.ERROR.value == "error"
        assert FilterStatus.UNKNOWN.value == "unknown"
