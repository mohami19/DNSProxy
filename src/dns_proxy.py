import socket
import time
import json
import redis
import datetime
import struct

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
HOST = "127.0.0.3"
PORT = 5006
cache_redis = db_select()
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
        response_data, response_addr = sock.recvfrom(1024)
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
