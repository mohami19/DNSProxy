import socket

PORT = 5005
HOST = '127.0.0.2'

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
input = input("Enter the domain name : ")

s.connect((HOST, PORT))
s.sendto(input.encode(),(HOST,PORT))

data,addr = s.recvfrom(512)
imported_ip = data.decode().split(',')

print('Non-authoritative answer:')
print(f'Name : \t {input} \nAddress : ',imported_ip[0].encode())
print(f'Name : \t {input} \nAddress : ',imported_ip[1].encode())