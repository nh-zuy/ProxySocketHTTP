'''
# Proxy Server

# 19120477 Le Van Dinh
# 19120484 Tram Huu Duc
# 19120495 Nguyen Nhat Duy
'''
import sys
import _thread
import socket
import ssl
import datetime

# GLOBAL VARIABLES
LISTEN_PORT = 8888             # Serving port
BUFFER_SIZE = 4096             # Buffer
MAX_CONNECT = 69               # Max accepted connection

# Banned domain in "backlist.conf"
with open("blacklist.conf", "r") as blacklist:
	blacklinks = blacklist.readlines()
	BLACKLINKS = [link[:-1] for link in blacklinks]

''' Proxy connect to webServer at port '''
def connectServer(webServer, port, connect, address, request):
	print(f"{webServer} at port {port} {connect} {address}")
	print("\n")

	try:
		# Set up new socket to connect the webServer
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.connect((webServer, port))
		
		# Continue sending the request of the sock
		sock.sendall(request)

		while True:
			response = sock.recv(BUFFER_SIZE)

			if (len(response) > 1) :
				# Return all the resonse to client
				connect.send(response)
				print(f"<I> Response: {webServer} -> {address[0]}")
			else:
				break

		sock.close()
		connect.close()
		
	except Exception as error:
		print(error)
		sock.close()
		connect.close()
		sys.exit(1)

''' Handling the request of the client '''
def handleRequest(connect, address, request):
	try:
		print(address)
		print("\n")
		print(request)
		print("\n")

		# Ex: GET http://abc.com.vn/ HTTP/1.1
		requestLine = request.decode("utf-8").split("\n")[0]

		print(requestLine)
		print("\n")

		# Split the method, web server, HTTP in the request line
		requestLineFields = requestLine.split(" ")      # GET abc.com.vn /HTTP1.1

		method = requestLineFields[0]             		# GET / POST
		path = requestLineFields[1]               		# http://abc.com.vn/index.html

		httpPos = path.find("://")                		

		temp =  path if (httpPos == -1) else path[(httpPos+3):]

		portPos = temp.find(":")
		webServerPos = temp.find("/")

		if (webServerPos == -1) :
			webServerPos = len(temp)

		webServer = ""
		port = 80

		if (portPos == -1) or (webServerPos < portPos):
			port = 80
			webServer = temp[:webServerPos]
		else:
			port = int(temp[(portPos + 1):][:webServerPos - portPos -1])
			webServer = temp[:portPos]

		# Check if the webServer in the blaclist.conf
		if (webServer not in BLACKLINKS):
			connectServer(webServer, port, connect, address, request)

			# Store the access history
			timeAccess = datetime.datetime.now()
			accessLog(webServer, port, timeAccess, "200 OK")
		else:
			# Store the access history
			timeAccess = datetime.datetime.now()
			accessLog(webServer, port, timeAccess, "403 Forbidden")

			# Resonse 403 Not Forbidden for the client if the webServer is banned
			header = 'HTTP/1.1 403 Forbidden\nContent-Type: text/html\n\n'.encode("utf-8")
			with open("403.html", mode="rb") as file:
				errorPage = file.read()

			connect.send(header + errorPage)

			connect.close()

	except Exception as error:
		print(error)

''' Storing the accessing history '''
def accessLog(webServer, port, time, code):
	with open("access.log", mode='a', encoding="utf-8") as file:
		file.write(f"::1 - - [{time}] {webServer}:{port} {code}\n")

''' Main function '''
def ProxyServer():
	''' Proxy Server '''
	try:
		# Set up the proxy server
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server.bind(("", LISTEN_PORT))
		server.listen(MAX_CONNECT)

		print(f"<> Proxy Socket started successfully at port {LISTEN_PORT}")

	except Exception as error:
		# Error occurred
		print(error)
		sys.exit(2)

	while True:
		try:
			# Accept new connection 
			(connect, address) = server.accept()
			request = connect.recv(BUFFER_SIZE)

			# Each connection will be served in a thread
			_thread.start_new_thread(handleRequest, (connect, address, request))
			
		# Type Ctrl + C in CMD to end the proxy
		except KeyboardInterrupt:
			server.close()
			print("\n\n<!> Server shut down. Successfully !")
			sys.exit(1)

	server.close()

if __name__ == "__main__":
	ProxyServer()