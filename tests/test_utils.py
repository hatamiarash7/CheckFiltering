import pytest
from validators.utils import ValidationError

from check_filter import utils


@pytest.mark.xfail(raises=ValidationError)
def test_validate_domain():
    assert utils.validate_domain("domain.com") is True
    utils.validate_domain("domain") is False
    utils.validate_domain("") is False


@pytest.mark.asyncio
async def test_print_result(capsys):
    res = await utils.print_result(["example.com"])
    assert res is None
    captured = capsys.readouterr()
    assert captured.out.__contains__("example.com │ Free")
