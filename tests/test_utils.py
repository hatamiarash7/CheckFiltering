"""Tests for the utils module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from check_filter import CheckResult, DomainChecker, FilterStatus, utils


class TestValidateDomain:
    """Tests for validate_domain function."""

    def test_valid_domain(self):
        """Test validation of a valid domain."""
        assert utils.validate_domain("example.com") is True
        assert utils.validate_domain("sub.example.com") is True
        assert utils.validate_domain("sub.sub.example.co.uk") is True

    def test_invalid_domain(self, capsys):
        """Test validation of invalid domains."""
        assert utils.validate_domain("invalid") is False
        captured = capsys.readouterr()
        assert "not a valid domain name" in captured.out

    def test_empty_domain(self, capsys):
        """Test validation of empty domain."""
        assert utils.validate_domain("") is False
        captured = capsys.readouterr()
        assert "empty" in captured.out.lower()

    def test_none_domain(self, capsys):
        """Test validation with None value."""
        assert utils.validate_domain(None) is False
        captured = capsys.readouterr()
        assert "empty" in captured.out.lower()

    def test_whitespace_domain(self, capsys):
        """Test validation of whitespace-only domain."""
        assert utils.validate_domain("   ") is False
        captured = capsys.readouterr()
        assert "empty" in captured.out.lower() or "whitespace" in captured.out.lower()

    def test_verbose_false(self, capsys):
        """Test validation with verbose=False doesn't print."""
        utils.validate_domain("invalid", verbose=False)
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_domain_with_spaces_stripped(self):
        """Test that domains with leading/trailing spaces are handled."""
        # The domain should be stripped before validation
        assert utils.validate_domain("  example.com  ") is True


class TestValidateDomains:
    """Tests for validate_domains function."""

    def test_all_valid(self):
        """Test validation when all domains are valid."""
        valid, invalid = utils.validate_domains(
            ["example.com", "google.com", "github.com"],
            verbose=False,
        )
        assert valid == ["example.com", "google.com", "github.com"]
        assert invalid == []

    def test_all_invalid(self):
        """Test validation when all domains are invalid."""
        valid, invalid = utils.validate_domains(
            ["invalid", "also-invalid", "nope"],
            verbose=False,
        )
        assert valid == []
        assert len(invalid) == 3

    def test_mixed(self):
        """Test validation with mixed valid and invalid domains."""
        valid, invalid = utils.validate_domains(
            ["example.com", "invalid", "google.com"],
            verbose=False,
        )
        assert valid == ["example.com", "google.com"]
        assert invalid == ["invalid"]

    def test_empty_list(self):
        """Test validation of empty list."""
        valid, invalid = utils.validate_domains([], verbose=False)
        assert valid == []
        assert invalid == []


class TestFormatStatus:
    """Tests for format_status function."""

    def test_format_free(self):
        """Test formatting for free status."""
        result = CheckResult(domain="example.com", status=FilterStatus.FREE)
        domain_text, status_text = utils.format_status(result)

        assert domain_text == "example.com"
        assert "Free" in status_text
        assert "green" in status_text

    def test_format_blocked(self):
        """Test formatting for blocked status."""
        result = CheckResult(domain="blocked.com", status=FilterStatus.BLOCKED)
        domain_text, status_text = utils.format_status(result)

        assert "blocked.com" in domain_text
        assert "red" in domain_text
        assert "Blocked" in status_text

    def test_format_error(self):
        """Test formatting for error status."""
        result = CheckResult(
            domain="error.com",
            status=FilterStatus.ERROR,
            error="Timeout",
        )
        domain_text, status_text = utils.format_status(result)

        assert "error.com" in domain_text
        assert "Error" in status_text
        assert "yellow" in status_text

    def test_format_unknown(self):
        """Test formatting for unknown status."""
        result = CheckResult(domain="unknown.com", status=FilterStatus.UNKNOWN)
        domain_text, status_text = utils.format_status(result)

        assert "unknown.com" in domain_text
        assert "Unknown" in status_text


class TestCreateResultsTable:
    """Tests for create_results_table function."""

    def test_default_title(self):
        """Test table creation with default title."""
        table = utils.create_results_table()
        assert table.title == "Check Result"

    def test_custom_title(self):
        """Test table creation with custom title."""
        table = utils.create_results_table(title="My Custom Title")
        assert table.title == "My Custom Title"

    def test_table_columns(self):
        """Test that table has correct columns."""
        table = utils.create_results_table()
        column_names = [col.header for col in table.columns]
        assert "Domain" in column_names
        assert "Status" in column_names


class TestReadDomainsFromFile:
    """Tests for read_domains_from_file function."""

    def test_read_simple_file(self, tmp_path):
        """Test reading domains from a simple file."""
        file_path = tmp_path / "domains.txt"
        file_path.write_text("example.com\ngoogle.com\ngithub.com\n")

        domains = utils.read_domains_from_file(str(file_path))

        assert domains == ["example.com", "google.com", "github.com"]

    def test_read_file_with_comments(self, tmp_path):
        """Test reading file with comment lines."""
        file_path = tmp_path / "domains.txt"
        file_path.write_text(
            "# This is a comment\nexample.com\n# Another comment\ngoogle.com\n"
        )

        domains = utils.read_domains_from_file(str(file_path))

        assert domains == ["example.com", "google.com"]

    def test_read_file_with_empty_lines(self, tmp_path):
        """Test reading file with empty lines."""
        file_path = tmp_path / "domains.txt"
        file_path.write_text("example.com\n\n\ngoogle.com\n\n")

        domains = utils.read_domains_from_file(str(file_path))

        assert domains == ["example.com", "google.com"]

    def test_read_file_with_whitespace(self, tmp_path):
        """Test reading file with whitespace around domains."""
        file_path = tmp_path / "domains.txt"
        file_path.write_text("  example.com  \n\tgoogle.com\t\n")

        domains = utils.read_domains_from_file(str(file_path))

        assert domains == ["example.com", "google.com"]

    def test_file_not_found(self):
        """Test handling of non-existent file."""
        with pytest.raises(FileNotFoundError):
            utils.read_domains_from_file("/nonexistent/path/file.txt")

    def test_empty_file(self, tmp_path):
        """Test reading empty file."""
        file_path = tmp_path / "empty.txt"
        file_path.write_text("")

        domains = utils.read_domains_from_file(str(file_path))

        assert domains == []


class TestPrintResult:
    """Tests for print_result function."""

    @pytest.mark.asyncio
    async def test_print_result_returns_results(self):
        """Test that print_result returns CheckResult objects."""
        with patch.object(
            DomainChecker, "acheck", new_callable=AsyncMock
        ) as mock_acheck:
            mock_acheck.return_value = CheckResult(
                domain="example.com",
                status=FilterStatus.FREE,
                ips=frozenset({"1.2.3.4"}),
            )

            results = await utils.print_result(
                ["example.com"],
                show_progress=False,
            )

            assert len(results) == 1
            assert results[0].domain == "example.com"
            assert results[0].is_free is True

    @pytest.mark.asyncio
    async def test_print_result_multiple_domains(self):
        """Test print_result with multiple domains."""
        with patch.object(
            DomainChecker, "acheck", new_callable=AsyncMock
        ) as mock_acheck:

            async def side_effect(domain):
                return CheckResult(
                    domain=domain,
                    status=FilterStatus.FREE,
                    ips=frozenset({"1.2.3.4"}),
                )

            mock_acheck.side_effect = side_effect

            results = await utils.print_result(
                ["a.com", "b.com", "c.com"],
                show_progress=False,
            )

            assert len(results) == 3

    @pytest.mark.asyncio
    async def test_print_result_with_custom_checker(self):
        """Test print_result with custom DomainChecker."""
        mock_checker = MagicMock(spec=DomainChecker)
        mock_checker.acheck = AsyncMock(
            return_value=CheckResult(
                domain="example.com",
                status=FilterStatus.BLOCKED,
            )
        )

        results = await utils.print_result(
            ["example.com"],
            checker=mock_checker,
            show_progress=False,
        )

        assert len(results) == 1
        assert results[0].is_blocked is True
        mock_checker.acheck.assert_called_once_with("example.com")


class TestDomainPattern:
    """Tests for DOMAIN_PATTERN constant."""

    def test_pattern_exists(self):
        """Test that DOMAIN_PATTERN is defined."""
        assert utils.DOMAIN_PATTERN is not None

    def test_pattern_matches_valid_domains(self):
        """Test pattern matches valid domain names."""
        valid_domains = [
            "example.com",
            "sub.example.com",
            "deep.sub.example.co.uk",
            "a.io",
        ]
        for domain in valid_domains:
            assert utils.DOMAIN_PATTERN.match(domain), f"Should match: {domain}"

    def test_pattern_rejects_invalid_domains(self):
        """Test pattern rejects invalid domain names."""
        invalid_domains = [
            "invalid",
            "-invalid.com",
            "invalid-.com",
            ".com",
        ]
        for domain in invalid_domains:
            assert not utils.DOMAIN_PATTERN.match(domain), f"Should not match: {domain}"
