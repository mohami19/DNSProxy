import socket
import time
import json

with open('setting.json') as file:
    setting = json.load(file)
expiration_time = setting['cache_expiration_time']
HOST = "127.0.0.1"
PORT = 5005

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))

start = time.time()
cache = {}

while True:
    data,addr = s.recvfrom(512)
    
    if data in cache:
        address = cache.get(data)
        s.sendto(address.encode(),addr)
    else:
        try :
            address1 = socket.gethostbyname(data) #'A'
        except :
            address1 = 'Unsupported Query Type'
        
        try :
            address2 = socket.getaddrinfo(data,PORT,socket.AF_INET6)[0][4][0] #'AAAA'
        except :
            address2 = 'Unsupported Query Type'
        
        address = address1 + ',' + address2
        cache[data] = address
        cache.update({data : address})
        s.sendto(address.encode(),addr)
    
    clear_cache = time.time()
    if clear_cache - start >= float(expiration_time):
        cache.clear()
        start = time.time()
