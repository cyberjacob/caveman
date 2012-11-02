#!/usr/bin/python2

import threading
import socket
import select

PORT=1337

class Connection:
	def __init__(self, manager, socket):
		self.manager = manager
		self.socket = socket
		self.thread = threading.Thread(target=self.run)
		self.thread.start()

	def run(self):
		connected = True
		while(connected):
			x, y, z = select.select((self.socket,), (), (), 0)
			if x:
				buf = self.socket.recv(1024)
				if len(buf) == 0:
					connected = False

				else:
					self.manager.send(buf)	

		self.socket.close()

	def send(self, message):
		self.socket.send(message)

class Dispatcher:
	def __init__(self):
		self.connections = []
		self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.listener.bind(("localhost", PORT))
		self.listener.listen(5)
		self.listen()

	def listen(self):
		while(True):
			print " [*] Listening for connection..."
			(clientsocket, address) = self.listener.accept()
			print " [x] Received connection, spawning new thread."
			client = Connection(self, clientsocket)
			self.connections.append(client)

	def send(self, message):
		for x in self.connections:
			x.send(message)

Dispatcher()
