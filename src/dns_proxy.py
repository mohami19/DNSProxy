import socket
import time
import json
import redis
import Datetime


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
    extra = packet[i+4:]
    return header, qname[:-1], qtype, qclass ,extra

with open('setting.json') as file:
    setting = json.load(file)
expiration_time = setting['cache_expiration_time']
HOST = "127.0.0.3"
PORT = 5006

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(('8.8.8.8', 53))

start = time.time()
cache = {}

while True:
    data,addr = s.recvfrom(512)
    
    if data in cache:
        
        print("in dns cache")
    else:
        sock.sendto(data, ('8.8.8.8', 53))
        respose_date, respose_addr = sock.recvfrom(1024)
        result = (socket.getaddrinfo(parse_dns_packet(response_data)[1],80))
        res = {result[0][4][0]}
        for i in result:
            res.add(i[4][0])
        
    clear_cache = time.time()
    if clear_cache - start >= float(expiration_time):
        cache.clear()
        start = time.time()
    
    for i in res:
        s.sendto(i.encode(),addr)