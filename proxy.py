import socket
import _thread
import signal

t = 0

def isBlocked(server):
	f = open('blacklist.conf', 'r')
	allfile = f.read()
	li = allfile.splitlines()
	for i in li:
		p = server.find(i)
		if(p == -1):
			continue
		elif (p + len(i) == len(server)):
			print('block', server)
			return True
	return False

def threadProxyClient(conn,clientAddress):
		print('Tiep nhan client ', clientAddress, '\n')

		global t
		#f = open(str(t) + '.txt', 'a')
		t += 1

		request1 = ""
		request = conn.recv(1024).decode('ascii')
		request1 += request

		while (len(request) == 1024):
			request = conn.recv(1024).decode('ascii')
			request1 += request

		#f.write(request1)
		#f.write('\n')
		#f.close()

		if (len(request1) == 0): exit()

		webserverPos = request1.find('://')
		if(webserverPos > -1): webserverPos = webserverPos + 3
		else: webserverPos = 0
		web = request1[webserverPos:]
		endWeb = web.find('/')
		if(endWeb > -1):
			web = web[:endWeb]

		colonPos = web.find(':')
		port = -1
		if (colonPos == -1):
			port = 80
		else:
			port = int(web[colonPos+1:])
			web = web[:colonPos]

		if (isBlocked(web)):
			conn.send(b'HTTP/1.1 403 Forbidden')
		else:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.settimeout(1000)
			s.connect((web, port))
			s.sendall(request1.encode('ascii'))
		
			try:
				while 1:
					data = s.recv(1024)

					if (len(data) > 0):
						conn.send(data)
					else:
						break
			except Exception:
				print(clientAddress, 'timeout\n')

			s.close()
		conn.close()
		print("Done! Close connect ", clientAddress, '\n')


def exit_chi(a, b):
	print('Shutdown proxy')
	exit(0)

print('Start proxy')

signal.signal(signal.SIGINT, exit_chi)

#Tao mot TCP socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

serverSocket.bind(('', 8888))

serverSocket.listen(10)

try:
	while True:
		(connClient, clientAddr) = serverSocket.accept()
		_thread.start_new_thread(threadProxyClient, (connClient, clientAddr))
		
except Exception as a:
	print('\n')
