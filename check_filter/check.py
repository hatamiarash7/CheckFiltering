"""It's the checker module for filtering status"""

import os

import dns.asyncresolver


class DomainChecker:
    """
    Checks if the domain is blocked or not
    """

    headers = ["Address", "Status"]

    def __init__(self, blocked_ips=None):
        self.blocked_ips = blocked_ips or {
            "10.10.34.34",
            "10.10.34.35",
            "10.10.34.36",
        }

        self.resolver = dns.asyncresolver.Resolver(configure=False)
        self.resolver.nameservers = [
            "178.22.122.100" if "CI" in os.environ else "8.8.8.8"
        ]

    async def acheck(self, domain: str) -> tuple[str, bool]:
        """Check if domain is blocked

        Args:
            domain (str): The domain's name

        Returns:
            tuple: (Domain's name, Blocking status)
        """
        try:
            answer = await self.resolver.resolve(domain)
            ip_list = [data.address for data in answer]
        except dns.resolver.NXDOMAIN:
            ip_list = []

        return domain, not any(ip in self.blocked_ips for ip in ip_list)
