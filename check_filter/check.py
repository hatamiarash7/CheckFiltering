"""It's the checker module for filtering status"""
import dns.resolver

blocked_ips = {'10.10.34.34', '10.10.34.35', '10.10.34.36'}
resolver = dns.resolver.Resolver()
resolver.nameservers = ['8.8.8.8']
headers = ['Address', 'Status']


def check(domain: str) -> bool:
    """Check if domain is blocked

    Args:
        domain (str): The domain's name

    Returns:
        bool: Blocking status
    """
    try:
        answer = resolver.resolve(domain)
        ip_list = [data.address for data in answer]
    except dns.resolver.NXDOMAIN:
        ip_list = []

    return not any(ip in blocked_ips for ip in ip_list)
