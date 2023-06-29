import socket
import time
import json
import redis
import Datetime


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
        
    clear_cache = time.time()
    if clear_cache - start >= float(expiration_time):
        cache.clear()
        start = time.time()