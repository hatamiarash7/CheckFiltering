"""Tests for the check module."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import dns.exception
import dns.resolver
import pytest

from check_filter import CheckResult, DomainChecker, FilterStatus
from check_filter.check import (
    CI_NAMESERVER,
    DEFAULT_BLOCKED_IPS,
    DEFAULT_NAMESERVER,
)


class TestFilterStatus:
    """Tests for FilterStatus enum."""

    def test_enum_values(self):
        """Test that all expected enum values exist."""
        assert FilterStatus.FREE.value == "free"
        assert FilterStatus.BLOCKED.value == "blocked"
        assert FilterStatus.ERROR.value == "error"
        assert FilterStatus.UNKNOWN.value == "unknown"


class TestCheckResult:
    """Tests for CheckResult dataclass."""

    def test_basic_creation(self):
        """Test basic CheckResult creation."""
        result = CheckResult(
            domain="example.com",
            status=FilterStatus.FREE,
        )
        assert result.domain == "example.com"
        assert result.status == FilterStatus.FREE
        assert result.ips == frozenset()
        assert result.error is None

    def test_with_ips(self):
        """Test CheckResult with resolved IPs."""
        ips = frozenset({"1.2.3.4", "5.6.7.8"})
        result = CheckResult(
            domain="example.com",
            status=FilterStatus.FREE,
            ips=ips,
        )
        assert result.ips == ips

    def test_with_error(self):
        """Test CheckResult with error message."""
        result = CheckResult(
            domain="example.com",
            status=FilterStatus.ERROR,
            error="Connection timeout",
        )
        assert result.error == "Connection timeout"

    def test_is_blocked_property(self):
        """Test is_blocked property."""
        blocked = CheckResult(domain="x.com", status=FilterStatus.BLOCKED)
        free = CheckResult(domain="example.com", status=FilterStatus.FREE)

        assert blocked.is_blocked is True
        assert free.is_blocked is False

    def test_is_free_property(self):
        """Test is_free property."""
        blocked = CheckResult(domain="x.com", status=FilterStatus.BLOCKED)
        free = CheckResult(domain="example.com", status=FilterStatus.FREE)

        assert blocked.is_free is False
        assert free.is_free is True

    def test_tuple_unpacking(self):
        """Test backward-compatible tuple unpacking."""
        result = CheckResult(domain="example.com", status=FilterStatus.FREE)
        domain, is_free = result

        assert domain == "example.com"
        assert is_free is True

    def test_tuple_unpacking_blocked(self):
        """Test tuple unpacking for blocked domain."""
        result = CheckResult(domain="blocked.com", status=FilterStatus.BLOCKED)
        domain, is_free = result

        assert domain == "blocked.com"
        assert is_free is False

    def test_immutability(self):
        """Test that CheckResult is immutable (frozen)."""
        result = CheckResult(domain="example.com", status=FilterStatus.FREE)

        with pytest.raises(AttributeError):
            result.domain = "other.com"


class TestDomainChecker:
    """Tests for DomainChecker class."""

    def test_default_initialization(self):
        """Test default DomainChecker initialization."""
        checker = DomainChecker()

        assert checker.blocked_ips == DEFAULT_BLOCKED_IPS
        assert (
            DEFAULT_NAMESERVER in checker.resolver.nameservers
            or CI_NAMESERVER in checker.resolver.nameservers
        )

    def test_custom_blocked_ips(self):
        """Test initialization with custom blocked IPs."""
        custom_ips = {"1.1.1.1", "2.2.2.2"}
        checker = DomainChecker(blocked_ips=custom_ips)

        assert checker.blocked_ips == frozenset(custom_ips)

    def test_empty_blocked_ips(self):
        """An explicit empty set disables blocking-IP matches."""
        assert DomainChecker(blocked_ips=set()).blocked_ips == frozenset()

    @pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf")])
    def test_invalid_timeout(self, timeout):
        """Reject timeouts that cannot impose a finite positive deadline."""
        with pytest.raises(ValueError, match="timeout"):
            DomainChecker(timeout=timeout)

    @pytest.mark.parametrize("ci_value", ["true", "false", ""])
    def test_ci_nameserver(self, monkeypatch, ci_value):
        """Preserve the CI-variable-presence convention."""
        monkeypatch.setenv("CI", ci_value)
        assert DomainChecker().resolver.nameservers == [CI_NAMESERVER]

    def test_default_nameserver_without_ci(self, monkeypatch):
        """Use the documented default outside CI."""
        monkeypatch.delenv("CI", raising=False)
        assert DomainChecker().resolver.nameservers == [DEFAULT_NAMESERVER]

    def test_custom_nameservers(self):
        """Test initialization with custom nameservers."""
        custom_ns = ["1.1.1.1", "8.8.4.4"]
        checker = DomainChecker(nameservers=custom_ns)

        assert checker.resolver.nameservers == custom_ns

    def test_custom_timeout(self):
        """Test initialization with custom timeout."""
        checker = DomainChecker(timeout=10.0)

        assert checker.resolver.lifetime == 10.0

    @pytest.mark.asyncio
    async def test_acheck_free_domain(self):
        """Test checking a free domain."""
        checker = DomainChecker()

        with patch.object(
            checker.resolver, "resolve", new_callable=AsyncMock
        ) as mock_resolve:
            mock_answer = MagicMock()
            mock_answer.__iter__ = lambda self: iter(
                [MagicMock(address="142.250.80.46")]
            )
            mock_resolve.return_value = mock_answer

            result = await checker.acheck("google.com")

            assert result.domain == "google.com"
            assert result.status == FilterStatus.FREE
            assert result.is_free is True
            assert "142.250.80.46" in result.ips

    @pytest.mark.asyncio
    async def test_acheck_blocked_domain(self):
        """Test checking a blocked domain."""
        checker = DomainChecker()

        with patch.object(
            checker.resolver, "resolve", new_callable=AsyncMock
        ) as mock_resolve:
            mock_answer = MagicMock()
            mock_answer.__iter__ = lambda self: iter([MagicMock(address="10.10.34.34")])
            mock_resolve.return_value = mock_answer

            result = await checker.acheck("blocked.com")

            assert result.domain == "blocked.com"
            assert result.status == FilterStatus.BLOCKED
            assert result.is_blocked is True

    @pytest.mark.asyncio
    async def test_acheck_empty_domain(self):
        """Test checking an empty domain raises error."""
        checker = DomainChecker()

        with pytest.raises(dns.resolver.NoAnswer):
            await checker.acheck("")

    @pytest.mark.asyncio
    async def test_acheck_whitespace_domain(self):
        """Test checking a whitespace-only domain raises error."""
        checker = DomainChecker()

        with pytest.raises(dns.resolver.NoAnswer):
            await checker.acheck("   ")

    @pytest.mark.asyncio
    async def test_acheck_nxdomain(self):
        """Test handling NXDOMAIN response."""
        checker = DomainChecker()

        with patch.object(
            checker.resolver, "resolve", new_callable=AsyncMock
        ) as mock_resolve:
            mock_resolve.side_effect = dns.resolver.NXDOMAIN()

            result = await checker.acheck("nonexistent.invalid")

            assert result.status == FilterStatus.UNKNOWN
            assert result.error == "Domain does not exist"

    @pytest.mark.asyncio
    async def test_acheck_timeout(self):
        """Test handling DNS timeout."""
        checker = DomainChecker()

        with patch.object(
            checker.resolver, "resolve", new_callable=AsyncMock
        ) as mock_resolve:
            mock_resolve.side_effect = dns.exception.Timeout()

            result = await checker.acheck("slow.example.com")

            assert result.status == FilterStatus.ERROR
            assert "timeout" in result.error.lower()

    @pytest.mark.asyncio
    async def test_acheck_no_nameservers(self):
        """Test handling no nameservers available."""
        checker = DomainChecker()

        with patch.object(
            checker.resolver, "resolve", new_callable=AsyncMock
        ) as mock_resolve:
            mock_resolve.side_effect = dns.resolver.NoNameservers()

            result = await checker.acheck("example.com")

            assert result.status == FilterStatus.ERROR
            assert "nameservers" in result.error.lower()

    @pytest.mark.asyncio
    async def test_acheck_normalizes_domain(self):
        """Test that domain is normalized (lowercase, stripped)."""
        checker = DomainChecker()

        with patch.object(
            checker.resolver, "resolve", new_callable=AsyncMock
        ) as mock_resolve:
            mock_answer = MagicMock()
            mock_answer.__iter__ = lambda self: iter([MagicMock(address="1.2.3.4")])
            mock_resolve.return_value = mock_answer

            result = await checker.acheck("  EXAMPLE.COM  ")

            assert result.domain == "example.com"
            mock_resolve.assert_called_with("example.com", "A")

    @pytest.mark.asyncio
    async def test_acheck_many(self):
        """Test checking multiple domains concurrently."""
        checker = DomainChecker()

        with patch.object(
            checker.resolver, "resolve", new_callable=AsyncMock
        ) as mock_resolve:
            mock_answer = MagicMock()
            mock_answer.__iter__ = lambda self: iter([MagicMock(address="1.2.3.4")])
            mock_resolve.return_value = mock_answer

            results = await checker.acheck_many(["a.com", "b.com", "c.com"])

            assert len(results) == 3
            assert all(isinstance(r, CheckResult) for r in results)

    @pytest.mark.parametrize("answer", [[], None])
    async def test_missing_a_record_is_unknown(self, answer):
        """A missing A record is inconclusive, not free or a batch failure."""
        checker = DomainChecker()
        with patch.object(
            checker.resolver, "resolve", new_callable=AsyncMock
        ) as resolve:
            if answer is None:
                resolve.side_effect = dns.resolver.NoAnswer()
            else:
                resolve.return_value = answer
            result = await checker.acheck("ipv6-only.example.com")

        assert result.status is FilterStatus.UNKNOWN
        assert result.ips == frozenset()
        assert "A record" in result.error

    async def test_mixed_answer_is_blocked(self):
        """One known blocking IP suffices, even alongside ordinary answers."""
        checker = DomainChecker()
        answer = [MagicMock(address=ip) for ip in ["1.2.3.4", "10.10.34.34", "1.2.3.4"]]
        with patch.object(checker.resolver, "resolve", AsyncMock(return_value=answer)):
            result = await checker.acheck("example.com")
        assert result.is_blocked
        assert result.ips == frozenset({"1.2.3.4", "10.10.34.34"})

    async def test_dns_exception_is_error(self):
        """Other DNS failures do not abort the whole batch."""
        checker = DomainChecker()
        with patch.object(
            checker.resolver,
            "resolve",
            AsyncMock(side_effect=dns.exception.FormError()),
        ):
            result = await checker.acheck("example.com")
        assert result.status is FilterStatus.ERROR
        assert result.error

    async def test_acheck_many_preserves_order(self):
        """Return input order even when later checks finish first."""
        checker = DomainChecker()
        second_finished = asyncio.Event()

        async def check(domain):
            if domain == "first.com":
                await second_finished.wait()
            else:
                second_finished.set()
            return CheckResult(domain, FilterStatus.FREE)

        with patch.object(checker, "acheck", side_effect=check):
            results = await checker.acheck_many(
                ["first.com", "second.com", "second.com"]
            )
        assert [result.domain for result in results] == [
            "first.com",
            "second.com",
            "second.com",
        ]

    async def test_acheck_many_empty(self):
        """An empty batch makes no DNS queries."""
        checker = DomainChecker()
        with patch.object(checker.resolver, "resolve", AsyncMock()) as resolve:
            assert await checker.acheck_many([]) == []
        resolve.assert_not_awaited()

    async def test_acheck_many_missing_record_does_not_abort(self):
        """A no-answer response is an individual result in a mixed batch."""
        checker = DomainChecker()
        with patch.object(
            checker.resolver,
            "resolve",
            AsyncMock(
                side_effect=[dns.resolver.NoAnswer(), [MagicMock(address="1.2.3.4")]]
            ),
        ):
            results = await checker.acheck_many(["no-a.com", "has-a.com"])
        assert [result.status for result in results] == [
            FilterStatus.UNKNOWN,
            FilterStatus.FREE,
        ]

    async def test_acheck_many_cancellation(self):
        """Cancellation reaches and awaits every child check."""
        checker = DomainChecker()
        started = asyncio.Event()
        children = []

        async def check(domain):
            children.append(asyncio.current_task())
            if len(children) == 2:
                started.set()
            await asyncio.Event().wait()

        with patch.object(checker, "acheck", side_effect=check):
            parent = asyncio.create_task(checker.acheck_many(["a.com", "b.com"]))
            await started.wait()
            parent.cancel()
            with pytest.raises(asyncio.CancelledError):
                await parent
        assert len(children) == 2
        assert all(task.cancelled() for task in children)

    async def test_acheck_many_cleans_up_after_failure(self):
        """Do not leave sibling checks running when one raises."""
        checker = DomainChecker()
        started = asyncio.Event()
        pending = []

        async def check(domain):
            if domain == "fail.com":
                await started.wait()
                raise RuntimeError("failed check")
            pending.append(asyncio.current_task())
            started.set()
            await asyncio.Event().wait()

        with patch.object(checker, "acheck", side_effect=check):
            try:
                with pytest.raises(RuntimeError, match="failed check"):
                    await checker.acheck_many(["fail.com", "pending.com"])
                assert all(task.done() for task in pending)
            finally:
                for task in pending:
                    task.cancel()
                await asyncio.gather(*pending, return_exceptions=True)


class TestDefaultConstants:
    """Tests for module constants."""

    def test_default_blocked_ips(self):
        """Test default blocked IPs are correct."""
        assert "10.10.34.34" in DEFAULT_BLOCKED_IPS
        assert "10.10.34.35" in DEFAULT_BLOCKED_IPS
        assert "10.10.34.36" in DEFAULT_BLOCKED_IPS

    def test_default_nameservers(self):
        """Test default nameserver constants."""
        assert DEFAULT_NAMESERVER == "8.8.8.8"
        assert CI_NAMESERVER == "178.22.122.100"


@pytest.mark.integration
class TestIntegration:
    """Integration tests that make actual DNS queries."""

    @pytest.mark.asyncio
    async def test_real_free_domain(self):
        """Test checking a real free domain (google.com)."""
        checker = DomainChecker()
        result = await checker.acheck("google.com")

        assert result.domain == "google.com"
        assert result.is_free is True

    @pytest.mark.asyncio
    async def test_real_blocked_domain(self):
        """Test checking a known blocked domain (instagram.com in Iran)."""
        checker = DomainChecker()
        result = await checker.acheck("instagram.com")

        assert result.domain == "instagram.com"
        # Note: Result depends on network environment
        assert result.status in [FilterStatus.FREE, FilterStatus.BLOCKED]
