"""Utils module"""

import validators
from rich.console import Console
from rich.table import Table

console = Console()


def validate_domain(domain: str) -> bool:
    """Validate domain's name

    Args:
        domain (str): Domain's name

    Returns:
        bool: Result of validation
    """
    return validators.domain(domain)


def print_result(domain: str, result: bool) -> str:
    """Print a pretty result for CLI

    Args:
        domain (str): Domain's name
        result (bool): Blocking result

    Returns:
        str: Printable result
    """
    if result:
        return f"\nThe `[italic]{domain}[/italic]` is [green]free[/green] in Iran :smiley:"

    return f"\nThe `[italic]{domain}[/italic]` is [red]blocked[/red] in Iran :x:"


def print_table(domains: list) -> None:
    """Print a pretty table for CLI

    Args:
        domains (list): List of [domain, status] of blocking result
    """
    table = Table(title="Check result")
    table.add_column("Domain", justify="left", no_wrap=True)
    table.add_column("Status", justify="left", no_wrap=True)

    for domain in domains:
        table.add_row(
            f"[red]{domain[0]}[/red]" if not domain[1] else domain[0],
            "[green]Free[/green]" if domain[1] else "[red]Blocked[/red] :x:")

    console.print("\n", table)
