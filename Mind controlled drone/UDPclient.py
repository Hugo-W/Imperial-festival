#!/usr/bin/python
import socket	#for sockets
import sys		#for exit
import msvcrt

# Global vars
host = '127.0.0.1'
port = 10000  #int(raw_input("Enter Listening Port:"))

# Create a UDP socket
try:
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	print 'Socket created'
except socket.error, msg:
	print 'Failed to create socket. Error Code: ' + str(msg[0]) + ' Message: ' + msg[1]
	sys.exit()
	
def sendData():
	# Keep alive unless socket error
	print >>sys.stderr, 'sending data stream.'
	while True:
		try:
			if msvcrt.kbhit() and msvcrt.getch()==chr(27):
				break
		
			#send data
			msg = raw_input('Message to Send: ')
			sock.sendto(msg, (host, port))
			sock.sendto(msg, (host, port + 1))
		
		except socket.error, msg:
			print 'Error Code: ' + str(msg[0]) + ' Message: ' + msg[1]
			break

	print >>sys.stderr, 'Closing socket'
	sock.close()	
	sys.exit()
	
def main(argv):
	print 'UDP Socket: IP: %s Port: %s' % (host, port)
	sendData()
	
# root code
if __name__ == "__main__":
	main(sys.argv)
