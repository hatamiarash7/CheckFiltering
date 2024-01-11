import pytest
import dns
from check_filter import DomainChecker


@pytest.mark.asyncio
async def test_check():
    domain_checker = DomainChecker()

    google_results = await domain_checker.acheck("google.com")
    instagram_results = await domain_checker.acheck("instagram.com")

    assert google_results[0] == "google.com"
    assert google_results[1] is True

    assert instagram_results[0] == "instagram.com"
    assert instagram_results[1] is False

    with pytest.raises(dns.resolver.NoAnswer):
        await domain_checker.acheck("")
