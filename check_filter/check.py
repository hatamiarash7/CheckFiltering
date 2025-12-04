"""Checker module for DNS-based filtering status detection.

This module provides functionality to detect if a domain is blocked
by checking its DNS A record against known blocking IPs used by
Iranian ISPs for censorship.
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from dns import asyncresolver, exception, resolver

if TYPE_CHECKING:
    from collections.abc import Set

logger = logging.getLogger(__name__)


class FilterStatus(Enum):
    """Enumeration of possible filtering statuses."""

    FREE = "free"
    BLOCKED = "blocked"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class CheckResult:
    """Result of a domain filtering check.

    Attributes:
        domain: The domain that was checked.
        status: The filtering status of the domain.
        ips: Set of resolved IP addresses (empty if resolution failed).
        error: Error message if the check failed, None otherwise.
    """

    domain: str
    status: FilterStatus
    ips: frozenset[str] = field(default_factory=frozenset)
    error: str | None = None

    @property
    def is_blocked(self) -> bool:
        """Check if the domain is blocked."""
        return self.status == FilterStatus.BLOCKED

    @property
    def is_free(self) -> bool:
        """Check if the domain is free (not blocked)."""
        return self.status == FilterStatus.FREE

    def __iter__(self) -> Any:
        """Allow tuple unpacking for backward compatibility."""
        yield self.domain
        yield self.is_free


# Default IPs used by Iranian ISPs for blocked domains
DEFAULT_BLOCKED_IPS: frozenset[str] = frozenset(
    {
        "10.10.34.34",
        "10.10.34.35",
        "10.10.34.36",
    }
)

# Default DNS nameservers
DEFAULT_NAMESERVER = "8.8.8.8"
CI_NAMESERVER = "178.22.122.100"


class DomainChecker:
    """Checks if domains are blocked by analyzing DNS responses.

    This class resolves domain A records and compares the results
    against known blocking IPs used by Iranian ISPs.

    Attributes:
        blocked_ips: Set of IP addresses that indicate a blocked domain.
        resolver: The DNS resolver instance.

    Example:
        >>> checker = DomainChecker()
        >>> result = await checker.acheck("google.com")
        >>> print(f"{result.domain}: {result.status.value}")
        google.com: free
    """

    headers = ["Address", "Status"]

    def __init__(
        self,
        blocked_ips: Set[str] | None = None,
        nameservers: list[str] | None = None,
        timeout: float = 5.0,
    ) -> None:
        """Initialize the domain checker.

        Args:
            blocked_ips: Custom set of IPs indicating blocked domains.
                Defaults to Iranian ISP blocking IPs.
            nameservers: List of DNS nameservers to use.
                Defaults to Google DNS (8.8.8.8) or Iranian DNS in CI.
            timeout: DNS query timeout in seconds. Defaults to 5.0.
        """
        self.blocked_ips: frozenset[str] = (
            frozenset(blocked_ips) if blocked_ips else DEFAULT_BLOCKED_IPS
        )

        self.resolver = asyncresolver.Resolver(configure=False)

        if nameservers:
            self.resolver.nameservers = nameservers
        else:
            self.resolver.nameservers = [
                CI_NAMESERVER if "CI" in os.environ else DEFAULT_NAMESERVER
            ]

        self.resolver.lifetime = timeout
        logger.debug(
            "DomainChecker initialized with nameservers: %s",
            self.resolver.nameservers,
        )

    async def acheck(self, domain: str) -> CheckResult:
        """Check if a domain is blocked asynchronously.

        Args:
            domain: The domain name to check.

        Returns:
            CheckResult containing the domain, status, resolved IPs,
            and any error message.

        Raises:
            dns.resolver.NoAnswer: If the domain exists but has no A record.
        """
        if not domain or not domain.strip():
            raise resolver.NoAnswer("Domain can't be empty or whitespace only")

        domain = domain.strip().lower()
        logger.debug("Checking domain: %s", domain)

        try:
            answer = await self.resolver.resolve(domain, "A")
            ip_list = frozenset(data.address for data in answer)
            logger.debug("Resolved IPs for %s: %s", domain, ip_list)

            is_blocked = bool(ip_list & self.blocked_ips)
            status = FilterStatus.BLOCKED if is_blocked else FilterStatus.FREE

            return CheckResult(
                domain=domain,
                status=status,
                ips=ip_list,
            )

        except resolver.NXDOMAIN:
            logger.debug("Domain %s does not exist (NXDOMAIN)", domain)
            return CheckResult(
                domain=domain,
                status=FilterStatus.UNKNOWN,
                error="Domain does not exist",
            )

        except resolver.NoNameservers as e:
            logger.error("No nameservers available for %s: %s", domain, e)
            return CheckResult(
                domain=domain,
                status=FilterStatus.ERROR,
                error=f"No nameservers available: {e}",
            )

        except exception.Timeout as e:
            logger.warning("DNS timeout for %s: %s", domain, e)
            return CheckResult(
                domain=domain,
                status=FilterStatus.ERROR,
                error=f"DNS query timeout: {e}",
            )

    async def acheck_many(self, domains: list[str]) -> list[CheckResult]:
        """Check multiple domains concurrently.

        Args:
            domains: List of domain names to check.

        Returns:
            List of CheckResult objects for each domain.
        """
        tasks = [self.acheck(domain) for domain in domains]
        return await asyncio.gather(*tasks, return_exceptions=False)
