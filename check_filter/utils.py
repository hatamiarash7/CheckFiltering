import validators


def validate_domain(domain: str) -> bool:
    return validators.domain(domain)


def print_result(domain: str, result: bool) -> str:
    if result:
        return f"\nThe `[italic]{domain}[/italic]` is [green]free[/green] in Iran :smiley:"
    return f"\nThe `[italic]{domain}[/italic]` is [red]blocked[/red] in Iran :x:"
