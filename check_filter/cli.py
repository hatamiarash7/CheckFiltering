"""This module provides the CheckFilter CLI."""

import asyncio
from typing import Optional

import typer
from rich import print as p

from check_filter import (
    __app_name__,
    __description__,  # noqa E501
    __epilog__,
    __version__,
    utils,
)

app = typer.Typer(help=__description__, rich_markup_mode="rich")


def _version_callback(value: bool) -> None:
    if value:
        p(f"{__app_name__} [bold cyan]v{__version__}[/bold cyan] :boom:")
        raise typer.Exit()


@app.command(epilog=__epilog__)
def domain(domain: str) -> None:
    """Check filtering status for a [green]single[/green] domain

    Args:
        domain (str): Domain's name
    """
    if not utils.validate_domain(domain):
        p(f"[red]The `{domain}` is not a valid domain name![/red]")
        raise typer.Exit()

    p(f"[yellow]Checking [italic]{domain}[/italic] ...[/yellow]")
    asyncio.run(utils.print_result([domain]))


@app.command(epilog=__epilog__)
def domains(domains: str) -> None:
    """Check filtering status for [green]multiple domains[/green].
    Give a comma separated list of domains.

    Args:
        domains (str): A comma separated list of domains
    """
    p("[yellow]Checking domains ...[/yellow]")
    domains = domains.split(",")
    domain_validity_checks = [
        utils.validate_domain(domain) for domain in domains
    ]  # noqa: E501
    if not all(domain_validity_checks):
        raise typer.Exit()

    asyncio.run(utils.print_result(domains))


@app.command(epilog=__epilog__)
def file(path: str):
    """Check filtering status from a [green]domain file[/green].
    Give a file path contains multi-line list of domains.

    Args:
        path (str): File path of domains
    """
    p("[yellow]Checking domains ...[/yellow]")
    with open(file=path, encoding="utf-8", mode="r") as file:
        domains = [domain.strip() for domain in file]

    domain_validity_checks = [
        utils.validate_domain(domain) for domain in domains
    ]  # noqa: E501
    if not all(domain_validity_checks):
        raise typer.Exit()

    asyncio.run(utils.print_result(domains))


@app.callback()
def main(
    version: Optional[
        bool
    ] = typer.Option(  # pylint: disable=unused-argument # noqa: F841
        None,
        "--version",
        "-v",
        help="Show the application's version.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    """It's the version printer for CLI"""
    return


if __name__ == "__main__":
    app()
