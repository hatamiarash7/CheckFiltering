import dns.resolver
from click import style
from columnar import columnar

blocked_ips = {'10.10.34.34', '10.10.34.35', '10.10.34.36'}
resolver = dns.resolver.Resolver()
resolver.nameservers = ['8.8.8.8']
headers = ['Address', 'Status']
result = []

with open('list') as file:
    sites = [site.strip() for site in file]

for site in sites:
    try:
        answer = resolver.resolve(site)
        ip_list = [data.address for data in answer]
    except dns.resolver.NXDOMAIN:
        ip_list = []

    status = 'Blocked' if any(ip in blocked_ips for ip in ip_list) else 'Free'
    result.append([site, status])


patterns = [
    ('Blocked', lambda text: style(text, fg='red')),
    ('Free', lambda text: style(text, fg='green')),
]

table = columnar(
    result,
    headers,
    no_borders=False,
    patterns=patterns,
    justify=['l', 'c'],
    min_column_width=15
)

print(table)
