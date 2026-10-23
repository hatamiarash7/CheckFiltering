"""Checker module for DNS-based filtering status detection.

This module provides functionality to detect if a domain is blocked
by checking its DNS A record against known blocking IPs used by
Iranian ISPs for censorship.
"""

from __future__ import annotations

import asyncio
import logging
import math
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from dns import asyncresolver, exception, resolver

if TYPE_CHECKING:
    from collections.abc import Iterator, Set

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

    def __iter__(self) -> Iterator[str | bool]:
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

    headers: list[str] = ["Address", "Status"]

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
            timeout: Positive, finite DNS query lifetime in seconds. Defaults to 5.0.

        Raises:
            ValueError: If timeout is not finite and greater than zero.
        """
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("timeout must be finite and greater than zero")

        self.blocked_ips: frozenset[str] = (
            frozenset(blocked_ips) if blocked_ips is not None else DEFAULT_BLOCKED_IPS
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
            dns.resolver.NoAnswer: If the input is empty or whitespace only.
        """
        if not domain or not domain.strip():
            raise resolver.NoAnswer("Domain can't be empty or whitespace only")

        domain = domain.strip().lower()
        logger.debug("Checking domain: %s", domain)

        try:
            answer = await self.resolver.resolve(domain, "A")
            ip_list = frozenset(data.address for data in answer)
            logger.debug("Resolved IPs for %s: %s", domain, ip_list)

            if not ip_list:
                raise resolver.NoAnswer()

            is_blocked = not ip_list.isdisjoint(self.blocked_ips)
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

        except resolver.NoAnswer:
            logger.debug("Domain %s has no A record", domain)
            return CheckResult(
                domain=domain,
                status=FilterStatus.UNKNOWN,
                error="Domain has no A record",
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

        except exception.DNSException as e:
            logger.warning("DNS query failed for %s: %s", domain, e)
            return CheckResult(
                domain=domain,
                status=FilterStatus.ERROR,
                error=f"DNS query failed: {e}",
            )

    async def acheck_many(self, domains: list[str]) -> list[CheckResult]:
        """Check multiple domains concurrently.

        Args:
            domains: List of domain names to check.

        Returns:
            List of CheckResult objects in input order, including duplicates.
            Unfinished checks are cancelled and awaited if the batch fails
            or is cancelled.
        """
        tasks = [asyncio.create_task(self.acheck(domain)) for domain in domains]
        try:
            return await asyncio.gather(*tasks)
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
