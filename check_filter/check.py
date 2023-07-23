import dns.resolver

blocked_ips = {'10.10.34.34', '10.10.34.35', '10.10.34.36'}
resolver = dns.resolver.Resolver()
resolver.nameservers = ['8.8.8.8']
headers = ['Address', 'Status']


def check(domain):
    try:
        answer = resolver.resolve(domain)
        ip_list = [data.address for data in answer]
    except dns.resolver.NXDOMAIN:
        ip_list = []

    status = 'Blocked' if any(ip in blocked_ips for ip in ip_list) else 'Free'
    return status == "Free"
