import pytest
import dns
from check_filter import check


def test_check():
    assert check.check("google.com") is True
    assert check.check("instagram.com") is False

    with pytest.raises(dns.resolver.NoAnswer):
        check.check("")
