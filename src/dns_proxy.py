import socket
import time
import json
import redis
import datetime
import struct
import threading

 
    

def parse_dns_packet(packet):
    header = bytearray(packet[:12])
    qname = ''
    i = 12
    while True:
        length = packet[i]
        if length == 0:
            break
        qname += packet[i+1:i+1+length].decode() + '.'
        i += length + 1
    i += 1
    qtype, qclass = struct.unpack('!HH', packet[i:i+4])
    extra = ''
    #if qtype != 1:
    #    header[3] = (header[3] & 0xF0) | 0x04
    return header, qname[:-1], qtype, qclass ,extra

def change_id(packet1, packet2):
    
    header_length = 12
    qname_end = packet1.find(b'\x00', header_length) + 5
    question_section = packet1[header_length:qname_end]
    qname_start = header_length
    qname_end = packet2.find(b'\x00', qname_start) + 5
    modified_packet2 = packet1[0:2] + packet2[2:qname_start] + question_section + packet2[qname_end:]
    
    
    return bytes(modified_packet2)

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
    r.lpush(key, result)



def dns(data,dns_proxy,s,cache):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(('8.8.8.8', 53))
    
    domain = parse_dns_packet(data)[1]
    print(domain)
    if domain in cache:
        x = change_id(data, cache[domain][1])
        print(data)
        print(x)
        s.sendto(x,addr)
    else:
        print("here")
        sock.send(data)
        response_data, response_addr = sock.recvfrom(1024)
        print(data)
        print(response_data)
        
        time = int((datetime.datetime.today()-datetime.datetime(2023,1,1,0,0,0,0)).total_seconds())
        cache[domain] = [time, response_data]

        db_insert(data, response_data)

        s.sendto(response_data,addr)

with open('setting.json') as file:

    setting = json.load(file)
expiration_time = setting['cache_expiration_time']
dns_proxy = setting['list_of_ips']

HOST = "127.0.0.3"
PORT = 5006
cache_redis = db_select()



cache = {}
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))
start = time.time()
while True:
    data,addr = s.recvfrom(512)
    dns(data,dns_proxy, s, cache)
    #threading.Thread(target=dns, args=(data,dns_proxy,s,cache)).start()
    