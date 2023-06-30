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
    
    return header, qname[:-1], qtype, qclass


def change_rcode(packet):
    
    temp = bytearray(packet)[2] | 0x80
    temp2 = bytearray(packet)[3] | 0x04
    qname_end = packet.find(b'\x00', 12) + 5
    
    packet = bytes(packet[0:2]) + temp.to_bytes(1, 'big') + temp2.to_bytes(1, 'big') + bytes(packet[4:qname_end])
    
    return packet

def change_id(packet1, packet2):
    
    header_length = 12
    qname_end = packet1.find(b'\x00', header_length) + 5
    question_section = packet1[header_length:qname_end]
    qname_start = header_length
    qname_end = packet2.find(b'\x00', qname_start) + 5
    packet = packet1[0:2] + packet2[2:qname_start] + question_section + packet2[qname_end:]
    
    
    return bytes(packet)

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



def dns(data,dns_proxy,s,cache, expiration_time):
    
    for i in dns_proxy:
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((i, 53))
        parsed_data = parse_dns_packet(data)
        domain = parsed_data[1]
        time = int((datetime.datetime.today()-datetime.datetime(2023,1,1,0,0,0,0)).total_seconds())
        if parsed_data[2] == (1 or 28): 
            if domain in cache and not time - cache[domain][0] > expiration_time:
                response_data = change_id(data, cache[domain][1])
            else:
                sock.send(data)
                response_data, response_addr = sock.recvfrom(1024)
                parsed_response_data = parse_dns_packet(response_data)
                
                if (parsed_response_data[0][3] & 0x0F) == 0x00:
                    time = int((datetime.datetime.today()-datetime.datetime(2023,1,1,0,0,0,0)).total_seconds())
                    cache.update({domain: [time, response_data]})
                    db_insert(data, response_data)
                    break
        else:
            response_data = (change_rcode(data))
    
    s.sendto(response_data, addr)


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
    dns(data,dns_proxy, s, cache, expiration_time)
    #threading.Thread(target=dns, args=(data,dns_proxy,s,cache)).start()
    