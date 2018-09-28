# This example runs on the raspberry pi
# It uses the vcgencmd tool to read the CPU temperature once per second
# and send the result over UDP 
# vcgendcmd: https://www.elinux.org/RPI_vcgencmd_usage
import socket
import time
import os
UDP_IP = "192.168.1.112"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

while True:
   message = os.popen('vcgencmd measure_temp').readline()
   message = message.replace("temp=","").replace("\n","") 
   bytes = sock.sendto(message,(UDP_IP,UDP_PORT))
   print message 
   time.sleep(1)

