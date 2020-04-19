import dns.resolver
from click import style
from columnar import columnar

file = open('list')
sites = file.readlines()
sites = [site.replace("\n", "") for site in sites]
file.close()

resolver = dns.resolver.Resolver()
resolver.nameservers = ['8.8.8.8']

headers = ['Address', 'Status']
result = []

for site in sites:
    answer = resolver.query(site)
    ip_list = []

    for data in answer:
        ip_list.append(data.address)

    if any(ip in '10.10.34.34 10.10.34.35 10.10.34.36' for ip in ip_list):
        result.append([site, 'Blocked'])
    else:
        result.append([site, 'Free'])

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
