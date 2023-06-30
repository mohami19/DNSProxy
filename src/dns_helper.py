'''
1- install dnspython using pip.
2- run the program providing following arguments.
    domain server-ip server-port rdtype(A or AAAA)
for example:
    python3 dns_helper.py mail.google.com 4.2.2.4 53 A
'''

import sys
import dns.resolver


def query(name: str, server: str, port: int, rdtype: str):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [server]
    resolver.port = int(port)
    dns_answer = resolver.resolve(name, rdtype=rdtype)
    ips = [ip.address for ip in dns_answer]
    return ips


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print('*ERROR* : Provide all arguments (domain, server-ip, server-port, rdtype(A or AAAA))')
        exit(1)

    print(query(*sys.argv[1:]))
