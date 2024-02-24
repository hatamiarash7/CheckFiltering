"""Utils module"""

import asyncio

import validators
from rich import print as p
from rich.live import Live
from rich.table import Table

from check_filter import DomainChecker


def validate_domain(domain: str) -> bool:
    """Validate domain's name

    Args:
        domain (str): Domain's name

    Returns: is domain valid
    """
    is_valid = validators.domain(domain)
    if not is_valid:
        p(f"[red]The `{domain}` is not a valid domain name![/red]")

    return is_valid


async def print_result(domains: list) -> None:
    """Print a pretty result for CLI

    Args:
        domains (list): List of [domain, status] of blocking result
    """
    table = Table(title="Check result")
    table.add_column("Domain", justify="left", no_wrap=True)
    table.add_column("Status", justify="left", no_wrap=True)

    domain_checker = DomainChecker()

    tasks = set()

    with Live(table, auto_refresh=False) as live_table:
        for d in domains:
            tasks.add(
                asyncio.create_task(
                    domain_checker.acheck(d),
                    name=f"domain-check-{d}",
                )
            )

        for future in asyncio.as_completed(tasks):
            domain, status = await future
            table.add_row(
                f"[red]{domain}[/red]" if not status else domain,
                "[green]Free[/green]" if status else "[red]Blocked[/red] :x:",
            )
            live_table.refresh()
