import socket
import time
import json
import redis
import datetime
import struct
import threading

def parse_dns_packet_new(data):
    # Parse the DNS packet header
    header = struct.unpack('!6H', data[:12])
    query_id = header[0]
    flags = header[1]
    question_count = header[2]
    answer_count = header[3]
    
    # Parse the DNS queries
    offset = 12
    queries = []
    for i in range(question_count):
        domain_name, offset = parse_domain_name(data, offset)
        query_type, query_class = struct.unpack('!2H', data[offset:offset+4])
        offset += 4
        queries.append((domain_name, query_type, query_class))

    # Parse the DNS resource records in the answer section
    answer_offset = offset
    answers = []
    for i in range(answer_count):
        domain_name, answer_type, answer_class, ttl, ip_address = parse_resource_record(data, answer_offset)
        answers.append((domain_name, answer_type, answer_class, ttl, ip_address))

    return (query_id, flags, queries, answers)

def parse_domain_name(data, offset):
    domain_name = ''
    while True:
        label_length = data[offset]
        offset += 1
        if label_length == 0:
            break
        elif label_length & 0xC0 == 0xC0:
            # This is a pointer to a domain name elsewhere in the packet
            pointer_offset = struct.unpack('!H', data[offset-1:offset+1])[0] & 0x3FFF
            domain_name += parse_domain_name(data, pointer_offset)[0]
            offset += 1
            break
        else:
            domain_name += data[offset:offset+label_length].decode('utf-8') + '.'
            offset += label_length
    return (domain_name, offset)

def parse_resource_record(data, offset):
    domain_name, offset = parse_domain_name(data, offset)
    resource_type, resource_class, ttl, data_length = struct.unpack('!HHLH', data[offset:offset+10])
    offset += 10
    if data_length > 0:
        if resource_type == 1:  # A record
            # Parse the IPv4 address
            ip_address = socket.inet_ntoa(data[offset:offset+4])
            return (domain_name, resource_type, resource_class, ttl, ip_address)
        elif resource_type == 28:  # AAAA record
            # Parse the IPv6 address
            ip_address = socket.inet_ntop(socket.AF_INET6, data[offset:offset+16])
            return (domain_name, resource_type, resource_class, ttl, ip_address)
        else:
            # Parse other types of resource records as byte strings
            return (domain_name, resource_type, resource_class, ttl, data[offset:offset+data_length])
    else:
        return (domain_name, resource_type, resource_class, ttl, None)
    

def parse_dns_packet(packet):
    header = packet[:12]
    qname = ''
    i = 12
    while True:
        length = packet[i]
        if length == 0:
            break
        qname += packet[i+1:i+1+length].decode() + '.'
        i += length + 1
    qtype, qclass = struct.unpack('!HH', packet[i:i+4])
    extra = ''
    return header, qname[:-1], qtype, qclass ,extra

def db_select():
    r = redis.Redis(host='localhost', port=6379, db=0)
    cache = {}
    keys = r.keys('*')
    for key in keys:
        item = r.lpop(key)
        while(item != None):
            if key in cache:
                cache[key].append(item)
            else:
                cache[key] = [item]
            item = r.lpop(key)
    return cache

def db_insert(key, result):
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.lpush(key, int((datetime.datetime.today()-datetime.datetime(2023,1,1,0,0,0,0)).total_seconds()))
    for res in result:
        r.lpush(key, res)

with open('setting.json') as file:
    setting = json.load(file)
expiration_time = setting['cache_expiration_time']
dns_proxy = setting['list_of_ips']

HOST = "127.0.0.3"
PORT = 5006
cache_redis = db_select()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(('8.8.8.8', 53))

def dns(data,dns_proxy,s,cache):
    if data in cache:
        print("in dns cache")
    else:
        sock.sendto(data, (dns_proxy, 53))
        response_data, response_addr = sock.recvfrom(1024)
        print(response_data)
        result = (socket.getaddrinfo(parse_dns_packet(response_data)[1],80))
        IPs = {result[0][4][0]}
        for i in result:
            IPs.add(i[4][0])
        cache.update({data : IPs})
        db_insert(parse_dns_packet(response_data)[1], IPs)

    clear_cache = time.time()
    if clear_cache - start >= float(expiration_time):
        cache.clear()
        cache_redis.clear()
        start = time.time()

    for i in IPs:
        s.sendto(i.encode(),addr)

cache = {}
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))
start = time.time()
while True:
    data,addr = s.recvfrom(512)
    threading.Thread(target=dns, args=(data,dns_proxy,s,cache)).start()
    