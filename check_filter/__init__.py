"""CheckFilter - Check if domains are filtered in Iran.

This package provides tools to check if domains are blocked by Iranian ISPs
by analyzing DNS A record responses against known blocking IP addresses.

Example:
    >>> from check_filter import DomainChecker
    >>> checker = DomainChecker()
    >>> result = await checker.acheck("google.com")
    >>> print(f"{result.domain}: {result.status.value}")

Modules:
    check: Core domain checking functionality
    utils: Utility functions for validation and display
    cli: Command-line interface
"""

from __future__ import annotations

__app_name__ = "check-filter"
__description__ = "Detect DNS-based domain filtering in Iran."
__version__ = "2.6.0"
__author__ = "Arash Hatami <info@arash-hatami.ir>"
__epilog__ = "Made with :heart:  in [green]Iran[/green]"
__all__: list[str] = [
    "DomainChecker",
    "CheckResult",
    "FilterStatus",
    "__app_name__",
    "__description__",
    "__version__",
    "__author__",
    "__epilog__",
]

from check_filter.check import CheckResult, DomainChecker, FilterStatus
