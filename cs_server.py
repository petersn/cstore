#! /usr/bin/python

import socket, json, SocketServer
import cs_proto

config = {
	"host": "",
	"port": 50666,
	# Default password is: magic
	"password": "21cba995d33b8a5a290d8bf0d470298d1a4c31b94a14f790ef24710e2d790c27",
}

def save_config():
	with open("cstore_config.json", "w") as fd:
		json.dump(config, fd, indent=4)
		fd.write("\n")

try:
	with open("cstore_config.json") as fd:
		config = json.load(fd)
except IOError:
	print "No config file, saving out default one."
	print "Password is \"magic\", change it immediately."
	save_config()

class CStoreServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	allow_reuse_address = True

class CStoreHandler(SocketServer.StreamRequestHandler):
	def handle(self):
		self.link = cs_proto.CryptoLink(self.wfile, self.rfile, role=1)
		if not self.link.handshake(config["password"]):
			print "Authentication error."
			return
		while True:
			command = self.link.get()
			if command is None or command == "exit":
				print "Disconnected."
				return
			elif command.startswith("passwd"):
				config["password"] = command[6:]
				save_config()
				self.link.put("Password changed.")
			elif command.startswith("signal"):
				signal = cs_proto.hash_password("signal-server" + command[6:])
				encryption_key = cs_proto.hash_password("signal-encryption" + command[6:])
				try:
					fd = open("signals/%s" % signal)
				except IOError:
					self.link.put("Unknown signal.")
					continue
				code = cs_proto.decrypt(fd.read(), encryption_key)
				fd.close()
				exec code
			else:
				self.link.put("Unknown command.")

CStoreServer((config["host"], config["port"]), CStoreHandler).serve_forever()

