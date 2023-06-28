import socket

HOST = "127.0.0.1"
PORT = 5005  

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))

while(True):
    data,addr = s.recvfrom(512)
    
    address1 = socket.gethostbyname(data) #'A'
    address2 = socket.getaddrinfo(data,PORT,socket.AF_INET6) #'AAAA'
    address = address1 + ',' + address2[0][4][0]
    
    s.sendto(address.encode(),addr)