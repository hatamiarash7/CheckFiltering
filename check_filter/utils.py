"""Utility functions for domain validation and result display.

This module provides helper functions for validating domain names
and displaying filtering check results in a formatted table.
"""

from __future__ import annotations

import asyncio
import logging
import re
from typing import TYPE_CHECKING

import validators
from rich import print as rich_print
from rich.live import Live
from rich.table import Table

from check_filter.check import CheckResult, DomainChecker, FilterStatus

if TYPE_CHECKING:
    from collections.abc import Iterable

logger = logging.getLogger(__name__)

# Regex pattern for basic domain validation
DOMAIN_PATTERN = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
)


def validate_domain(domain: str, verbose: bool = True) -> bool:
    """Validate a domain name.

    Args:
        domain: The domain name to validate.
        verbose: If True, print error message for invalid domains.

    Returns:
        True if the domain is valid, False otherwise.

    Example:
        >>> validate_domain("example.com")
        True
        >>> validate_domain("invalid")
        False
    """
    if not domain or not isinstance(domain, str):
        if verbose:
            rich_print("[red]Domain cannot be empty![/red]")
        return False

    domain = domain.strip()

    if not domain:
        if verbose:
            rich_print("[red]Domain cannot be empty or whitespace only![/red]")
        return False

    is_valid = validators.domain(domain)

    if not is_valid and verbose:
        rich_print(f"[red]The `{domain}` is not a valid domain name![/red]")

    return bool(is_valid)


def validate_domains(
    domains: Iterable[str], verbose: bool = True
) -> tuple[list[str], list[str]]:
    """Validate multiple domain names.

    Args:
        domains: Iterable of domain names to validate.
        verbose: If True, print error messages for invalid domains.

    Returns:
        Tuple of (valid_domains, invalid_domains) lists.
    """
    valid: list[str] = []
    invalid: list[str] = []

    for domain in domains:
        if validate_domain(domain, verbose=verbose):
            valid.append(domain.strip())
        else:
            invalid.append(domain.strip() if domain else "")

    return valid, invalid


def format_status(result: CheckResult) -> tuple[str, str]:
    """Format a check result for display.

    Args:
        result: The CheckResult to format.

    Returns:
        Tuple of (formatted_domain, formatted_status) strings.
    """
    status_formats = {
        FilterStatus.FREE: ("[green]Free[/green]", None),
        FilterStatus.BLOCKED: ("[red]Blocked[/red] :x:", "[red]"),
        FilterStatus.ERROR: ("[yellow]Error[/yellow] :warning:", "[yellow]"),
        FilterStatus.UNKNOWN: ("[dim]Unknown[/dim] :question:", "[dim]"),
    }

    status_text, domain_color = status_formats.get(
        result.status, ("[dim]Unknown[/dim]", None)
    )

    if domain_color:
        domain_text = f"{domain_color}{result.domain}[/{domain_color[1:-1]}]"
    else:
        domain_text = result.domain

    return domain_text, status_text


def create_results_table(title: str = "Check Result") -> Table:
    """Create a Rich table for displaying results.

    Args:
        title: The title for the table.

    Returns:
        A configured Rich Table instance.
    """
    table = Table(title=title)
    table.add_column("Domain", justify="left", no_wrap=True)
    table.add_column("Status", justify="left", no_wrap=True)
    return table


async def print_result(
    domains: list[str],
    checker: DomainChecker | None = None,
    show_progress: bool = True,
) -> list[CheckResult]:
    """Check domains and print results in a formatted table.

    Args:
        domains: List of domain names to check.
        checker: Optional DomainChecker instance. Creates one if not provided.
        show_progress: If True, show live updates as results come in.

    Returns:
        List of CheckResult objects for all checked domains.
    """
    table = create_results_table()
    domain_checker = checker or DomainChecker()
    results: list[CheckResult] = []

    tasks = {
        asyncio.create_task(
            domain_checker.acheck(d),
            name=f"check-{d}",
        )
        for d in domains
    }

    if show_progress:
        with Live(table, auto_refresh=False) as live_table:
            for future in asyncio.as_completed(tasks):
                result = await future
                results.append(result)

                domain_text, status_text = format_status(result)
                table.add_row(domain_text, status_text)
                live_table.refresh()
    else:
        for future in asyncio.as_completed(tasks):
            result = await future
            results.append(result)

            domain_text, status_text = format_status(result)
            table.add_row(domain_text, status_text)

        rich_print(table)

    return results


def read_domains_from_file(path: str) -> list[str]:
    """Read domain names from a file.

    Args:
        path: Path to the file containing domain names (one per line).

    Returns:
        List of domain names read from the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be read.
    """
    with open(path, encoding="utf-8") as f:
        domains = [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]
    return domains
