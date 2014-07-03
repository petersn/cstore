#! /usr/bin/python

import socket, json, SocketServer, os
import cs_proto

config = {
	"host": "",
	"port": 50666,
	# Default password is: magic
	"password": "b2a5e2760cbb83ae464d0318cd781b279b9ec74d83e04e8bbdcb0edb6e3a24d0",
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
	config["salt"] = os.urandom(16).encode("hex")
	save_config()

class CStoreServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	allow_reuse_address = True

class CStoreHandler(SocketServer.StreamRequestHandler):
	def handle(self):
		link = cs_proto.CryptoLink(self.wfile, self.rfile, role=1)
		if not link.handshake(config["password"]):
			print "Authentication error."
			return
		keep_going = True
		while keep_going:
			command = link.get()
			if command is None:
				print "Connection dropped."
				break
			if command.startswith(":"):
				# Look up the signal.
				signal = cs_proto.hash_password(command[1:], distinguish="signal-address" + config["salt"])
				encryption_key = cs_proto.hash_password(command[1:], distinguish="signal-key" + config["salt"])
				try:
					fd = open("signals/%s" % signal)
				except IOError:
					# Send a message, then an empty schema.
					link.put(":Unknown signal.")
					link.put("done")
					continue
				code = cs_proto.decrypt(fd.read(), encryption_key)
				fd.close()
				exec code

CStoreServer((config["host"], config["port"]), CStoreHandler).serve_forever()

