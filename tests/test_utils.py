import pytest
from validators.utils import ValidationFailure
from check_filter import utils


@pytest.mark.xfail(raises=ValidationFailure)
def test_validate_domain():
    assert utils.validate_domain("domain.com") is True
    utils.validate_domain("domain") is False
    utils.validate_domain("") is False


def test_print_result():
    assert utils.print_result(
        "domain.com", True) == "\nThe `[italic]domain.com[/italic]` is [green]free[/green] in Iran :smiley:"
    assert utils.print_result(
        "domain.com", False) == "\nThe `[italic]domain.com[/italic]` is [red]blocked[/red] in Iran :x:"


def test_print_table(capsys):
    assert utils.print_table([["example.com", True]]) is None
    captured = capsys.readouterr()
    assert captured.out.__contains__("example.com │ Free")
