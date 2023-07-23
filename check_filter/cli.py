"""This module provides the CheckFilter CLI."""

from typing import Optional
import typer
from rich import print

from check_filter import (
    __app_name__,
    __version__,
    __description__,
    __epilog__,
    check,
    utils
)

app = typer.Typer(
    help=__description__,
    rich_markup_mode="rich"
)


def _version_callback(value: bool) -> None:
    if value:
        print(
            f"{__app_name__} [bold cyan]v{__version__}[/bold cyan] :boom:"
        )
        raise typer.Exit()


@app.command(epilog=__epilog__)
def domain(domain: str) -> None:
    """Check filtering status for a [green]single[/green] domain

    Args:
        domain (str): Domain's name
    """
    if utils.validate_domain(domain):
        print(f"[yellow]Checking [italic]{domain}[/italic] ...[/yellow]")
        result = check.check(domain=domain)
        print(utils.print_result(domain=domain, result=result))
        return

    print(f"[red]The `{domain}` is not a valid domain name![/red]")


@app.command(epilog=__epilog__)
def domains(domains: str):
    """Check filtering status for [green]multiple domains[/green].
    Give a comma separated list of domains.

    Args:
        domains (str): A comma separated list of domains
    """
    result = []
    print("[yellow]Checking domains ...[/yellow]")

    for domain in domains.split(","):
        if utils.validate_domain(domain):
            status = check.check(domain=domain)
            result.append([domain, status])
        else:
            print(f"[red]The `{domain}` is not a valid domain name![/red]")
    utils.print_table(result)
    return


@app.command(epilog=__epilog__)
def file(path: str):
    """Check filtering status from a [green]domain file[/green].
    Give a file path contains multi-line list of domains.

    Args:
        path (str): File path of domains
    """
    print("[yellow]Checking domains ...[/yellow]")
    with open('list') as file:
        sites = [site.strip() for site in file]
        result = []

        for domain in sites:
            if utils.validate_domain(domain):
                status = check.check(domain=domain)
                result.append([domain, status])
            else:
                print(f"[red]The `{domain}` is not a valid domain name![/red]")
        utils.print_table(result)
        return


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return
