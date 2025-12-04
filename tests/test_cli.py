"""Tests for the CLI module."""

from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from check_filter import (
    CheckResult,
    FilterStatus,
    __app_name__,
    __version__,
    cli,
)

runner = CliRunner()


class TestVersionCallback:
    """Tests for version callback functionality."""

    def test_version_short_flag(self):
        """Test -v flag shows version."""
        result = runner.invoke(cli.app, ["-v"])

        assert result.exit_code == 0
        assert __app_name__ in result.stdout
        assert __version__ in result.stdout

    def test_version_long_flag(self):
        """Test --version flag shows version."""
        result = runner.invoke(cli.app, ["--version"])

        assert result.exit_code == 0
        assert __app_name__ in result.stdout
        assert __version__ in result.stdout


class TestHelpOutput:
    """Tests for help output."""

    def test_main_help(self):
        """Test main help output."""
        result = runner.invoke(cli.app, ["--help"])

        assert result.exit_code == 0
        assert "domain" in result.stdout.lower()
        assert "domains" in result.stdout.lower()
        assert "file" in result.stdout.lower()

    def test_domain_command_help(self):
        """Test domain command help."""
        result = runner.invoke(cli.app, ["domain", "--help"])

        assert result.exit_code == 0
        assert "single" in result.stdout.lower()

    def test_domains_command_help(self):
        """Test domains command help."""
        result = runner.invoke(cli.app, ["domains", "--help"])

        assert result.exit_code == 0
        assert "multiple" in result.stdout.lower()
        assert "comma" in result.stdout.lower()

    def test_file_command_help(self):
        """Test file command help."""
        result = runner.invoke(cli.app, ["file", "--help"])

        assert result.exit_code == 0
        assert "file" in result.stdout.lower()


class TestDomainCommand:
    """Tests for single domain command."""

    def test_valid_domain(self):
        """Test checking a valid domain."""
        with patch(
            "check_filter.cli.utils.print_result", new_callable=AsyncMock
        ) as mock_print:
            mock_print.return_value = [
                CheckResult(domain="example.com", status=FilterStatus.FREE)
            ]

            result = runner.invoke(cli.app, ["domain", "example.com"])

            assert result.exit_code == 0
            assert "Checking" in result.stdout
            mock_print.assert_called_once()

    def test_invalid_domain(self):
        """Test checking an invalid domain."""
        result = runner.invoke(cli.app, ["domain", "invalid"])

        assert result.exit_code == 1
        assert "not a valid domain" in result.stdout

    def test_empty_domain(self):
        """Test checking with empty domain argument."""
        # Typer should handle missing argument
        result = runner.invoke(cli.app, ["domain"])

        assert result.exit_code != 0


class TestDomainsCommand:
    """Tests for multiple domains command."""

    def test_valid_domains(self):
        """Test checking multiple valid domains."""
        with patch("check_filter.cli.utils.validate_domains") as mock_validate:
            mock_validate.return_value = (["example.com", "google.com"], [])

            with patch(
                "check_filter.cli.utils.print_result", new_callable=AsyncMock
            ) as mock_print:
                mock_print.return_value = []

                result = runner.invoke(cli.app, ["domains", "example.com,google.com"])

                assert result.exit_code == 0
                assert "Checking" in result.stdout

    def test_mixed_valid_invalid(self):
        """Test checking mixed valid and invalid domains."""
        with patch("check_filter.cli.utils.validate_domains") as mock_validate:
            mock_validate.return_value = (["example.com"], ["invalid"])

            result = runner.invoke(cli.app, ["domains", "example.com,invalid"])

            assert result.exit_code == 1
            assert "invalid" in result.stdout.lower()

    def test_empty_domain_list(self):
        """Test with empty domain list after splitting."""
        result = runner.invoke(cli.app, ["domains", ",,,"])

        assert result.exit_code == 1
        assert "No valid domains" in result.stdout

    def test_whitespace_handling(self):
        """Test that whitespace is handled in domain list."""
        with patch("check_filter.cli.utils.validate_domains") as mock_validate:
            mock_validate.return_value = (["example.com", "google.com"], [])

            with patch(
                "check_filter.cli.utils.print_result", new_callable=AsyncMock
            ) as mock_print:
                mock_print.return_value = []

                result = runner.invoke(cli.app, ["domains", "example.com , google.com"])

                assert result.exit_code == 0


class TestFileCommand:
    """Tests for file command."""

    def test_valid_file(self, tmp_path):
        """Test checking domains from a valid file."""
        file_path = tmp_path / "domains.txt"
        file_path.write_text("example.com\ngoogle.com")

        with patch("check_filter.cli.utils.validate_domains") as mock_validate:
            mock_validate.return_value = (["example.com", "google.com"], [])

            with patch(
                "check_filter.cli.utils.print_result", new_callable=AsyncMock
            ) as mock_print:
                mock_print.return_value = []

                result = runner.invoke(cli.app, ["file", str(file_path)])

                assert result.exit_code == 0
                assert "Reading" in result.stdout
                assert "Checking" in result.stdout

    def test_nonexistent_file(self):
        """Test with non-existent file."""
        result = runner.invoke(cli.app, ["file", "/nonexistent/file.txt"])

        assert result.exit_code != 0

    def test_empty_file(self, tmp_path):
        """Test with empty file."""
        file_path = tmp_path / "empty.txt"
        file_path.write_text("")

        result = runner.invoke(cli.app, ["file", str(file_path)])

        assert result.exit_code == 1
        assert "No domains" in result.stdout

    def test_file_with_comments(self, tmp_path):
        """Test file with comment lines."""
        file_path = tmp_path / "domains.txt"
        file_path.write_text("# Comment\nexample.com\n# Another comment\ngoogle.com")

        with patch("check_filter.cli.utils.validate_domains") as mock_validate:
            mock_validate.return_value = (["example.com", "google.com"], [])

            with patch(
                "check_filter.cli.utils.print_result", new_callable=AsyncMock
            ) as mock_print:
                mock_print.return_value = []

                result = runner.invoke(cli.app, ["file", str(file_path)])

                assert result.exit_code == 0

    def test_file_with_invalid_domains(self, tmp_path):
        """Test file containing invalid domains."""
        file_path = tmp_path / "domains.txt"
        file_path.write_text("example.com\ninvalid\ngoogle.com")

        with patch("check_filter.cli.utils.validate_domains") as mock_validate:
            mock_validate.return_value = (["example.com", "google.com"], ["invalid"])

            result = runner.invoke(cli.app, ["file", str(file_path)])

            assert result.exit_code == 1


class TestNoArgs:
    """Tests for CLI with no arguments."""

    def test_no_args_shows_help(self):
        """Test that running with no args shows help."""
        result = runner.invoke(cli.app, [])

        # Should show help, not error
        assert "domain" in result.stdout.lower()
        assert "domains" in result.stdout.lower()
        assert "file" in result.stdout.lower()


class TestRunFunction:
    """Tests for the run() entry point function."""

    def test_run_function_exists(self):
        """Test that run function exists."""
        assert hasattr(cli, "run")
        assert callable(cli.run)


@pytest.mark.integration
class TestIntegration:
    """Integration tests that make actual CLI calls."""

    def test_check_example_domain(self):
        """Test checking example.com (should always be free)."""
        result = runner.invoke(cli.app, ["domain", "example.com"])

        assert result.exit_code == 0
        assert "example.com" in result.stdout

    def test_check_multiple_domains_integration(self, tmp_path):
        """Test checking multiple domains from file."""
        file_path = tmp_path / "test_domains.txt"
        file_path.write_text("example.com\nexample.org")

        result = runner.invoke(cli.app, ["file", str(file_path)])

        assert result.exit_code == 0
        assert "example.com" in result.stdout or "example.org" in result.stdout
