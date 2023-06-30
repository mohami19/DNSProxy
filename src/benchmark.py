import matplotlib.pyplot as plt
import dns.resolver
import datetime

def query(name: str, server: str, port: int, rdtype: str):
    ips = []
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [server]
        resolver.port = int(port)
        dns_answer = resolver.resolve(name, rdtype=rdtype)
        ips = [ip.address for ip in dns_answer]
    except Exception as e:
        pass
    return ips


domains = []
with open(r'src\random-domains.txt') as f:
    for line in f:
        name = line.strip()
        domains.append(name)

proxy_time = []
proxy_time.append(0)   
for m in [20,40,60,100,140,200]:
    stime = datetime.datetime.today()
    for i in range(0, m):
        query(domains[i],  "127.0.0.3", 5006, "A")
    etime = datetime.datetime.today()
    proxy_time.append((etime-stime).total_seconds())
time = []
time.append(0)
for m in [20,40,60,100,140,200]:
    stime = datetime.datetime.today()
    for i in range(0, m):
        query(domains[i],  "8.8.8.8", 53, "A")
    etime = datetime.datetime.today()
    time.append((etime-stime).total_seconds())

xpoints = [0,20,40,60,100,140,200]


figure, axis = plt.subplots(1, 2)
axis[0].plot(xpoints, proxy_time)
axis[1].plot(xpoints, time)
axis[0].set_title('with proxy')
axis[1].set_title('without proxy')
plt.show()