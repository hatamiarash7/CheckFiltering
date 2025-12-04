"""Command-line interface for CheckFilter.

This module provides the CLI commands for checking domain filtering status
in Iran using DNS analysis.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich import print as rich_print
from rich.console import Console

from check_filter import (
    __app_name__,
    __description__,
    __epilog__,
    __version__,
    utils,
)

# Initialize console for error output
console = Console(stderr=True)

# Create the Typer app
app = typer.Typer(
    help=__description__,
    rich_markup_mode="rich",
    add_completion=True,
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:
    """Display version information and exit."""
    if value:
        rich_print(f"{__app_name__} [bold cyan]v{__version__}[/bold cyan] :boom:")
        raise typer.Exit()


def _handle_validation_errors(invalid_domains: list[str]) -> None:
    """Handle validation errors for invalid domains."""
    if invalid_domains:
        console.print(
            f"[red]Found {len(invalid_domains)} invalid domain(s). "
            "Please fix them and try again.[/red]"
        )
        raise typer.Exit(code=1)


@app.command(epilog=__epilog__)
def domain(
    domain_name: Annotated[
        str,
        typer.Argument(
            help="The domain name to check (e.g., example.com)",
            show_default=False,
        ),
    ],
) -> None:
    """Check filtering status for a [green]single[/green] domain.

    Examples:
        check-filter domain google.com
        check-filter domain twitter.com
    """
    if not utils.validate_domain(domain_name):
        raise typer.Exit(code=1)

    rich_print(f"[yellow]Checking [italic]{domain_name}[/italic] ...[/yellow]")
    asyncio.run(utils.print_result([domain_name]))


@app.command(epilog=__epilog__)
def domains(
    domain_list: Annotated[
        str,
        typer.Argument(
            help="Comma-separated list of domains (e.g., google.com,twitter.com)",  # noqa: E501
            show_default=False,
        ),
    ],
) -> None:
    """Check filtering status for [green]multiple domains[/green].

    Provide a comma-separated list of domain names.

    Examples:
        check-filter domains google.com,twitter.com
        check-filter domains github.com,gitlab.com,bitbucket.org
    """
    rich_print("[yellow]Checking domains ...[/yellow]")

    # Parse and clean domain list
    domain_names = [d.strip() for d in domain_list.split(",") if d.strip()]

    if not domain_names:
        console.print("[red]No valid domains provided![/red]")
        raise typer.Exit(code=1)

    valid, invalid = utils.validate_domains(domain_names)
    _handle_validation_errors(invalid)

    asyncio.run(utils.print_result(valid))


@app.command(epilog=__epilog__)
def file(
    path: Annotated[
        Path,
        typer.Argument(
            help="Path to a file containing domain names (one per line)",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            show_default=False,
        ),
    ],
) -> None:
    """Check filtering status from a [green]domain file[/green].

    The file should contain one domain name per line.
    Lines starting with # are treated as comments and ignored.
    Empty lines are also ignored.

    Examples:
        check-filter file domains.txt
        check-filter file /path/to/my_domains.txt
    """
    rich_print(f"[yellow]Reading domains from [italic]{path}[/italic] ...[/yellow]")

    try:
        domain_names = utils.read_domains_from_file(str(path))
    except FileNotFoundError:
        console.print(f"[red]File not found: {path}[/red]")
        raise typer.Exit(code=1) from None
    except PermissionError:
        console.print(f"[red]Permission denied: {path}[/red]")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"[red]Error reading file: {e}[/red]")
        raise typer.Exit(code=1) from None

    if not domain_names:
        console.print("[red]No domains found in the file![/red]")
        raise typer.Exit(code=1)

    rich_print(f"[yellow]Checking {len(domain_names)} domain(s) ...[/yellow]")

    valid, invalid = utils.validate_domains(domain_names)
    _handle_validation_errors(invalid)

    asyncio.run(utils.print_result(valid))


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    _: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-v",
            help="Show the application's version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """CheckFilter - Check if domains are filtered in Iran.

    This tool analyzes DNS responses to detect if domains are blocked
    by Iranian ISPs. It works by comparing DNS A record responses
    against known blocking IP addresses.

    Note: This tool can only detect DNS-based blocking and does not
    have the power to detect other types of filtering or disorders.
    """
    # Show help if no command is provided
    if ctx.invoked_subcommand is None:
        rich_print(ctx.get_help())


def run() -> None:
    """Entry point for the CLI application."""
    try:
        app()
    except KeyboardInterrupt:
        rich_print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(130)


if __name__ == "__main__":
    run()
