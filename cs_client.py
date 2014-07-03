#! /usr/bin/python

import socket, getpass, readline, hashlib, sys
import cs_proto

if len(sys.argv) != 2:
	print "Usage: cs_client host"
	exit(2)

def get_hashed_pass(prompt, distinguish):
	password = getpass.getpass(prompt)
	password = cs_proto.hash_password(password, distinguish)
	return password

s = socket.create_connection((sys.argv[1], 50666))
link = cs_proto.CryptoLink(s.makefile())
password = get_hashed_pass("Password: ", "main-login")

if not link.handshake(password):
	print "Authentication error."
	exit(1)

while True:
	command = raw_input("> ")
	if command.endswith(":"):
		command += getpass.getpass("Secret entropy: ")
	command = cs_proto.hash_password(command, distinguish="signal-client")
	link.put(":" + command)
	while True:
		schema = link.get()
		if schema is None:
			print "Terminated."
			exit()
		elif schema.startswith(":"):
			print schema[1:]
		elif schema.startswith("prompt:"):
			link.put(raw_input("*string* " + schema[7:]))
		elif schema.startswith("password:"):
			distinguish, prompt = schema[9:].split(":", 1)
			link.put(get_hashed_pass("[%s] " % distinguish + prompt, distinguish=distinguish))
		elif schema.startswith("file:"):
			prompt = schema[5:]
			while True:
				path = raw_input("*load file* " + prompt)
				try:
					with open(path) as fd:
						data = fd.read()
				except IOError, e:
					print "Error:", e
					continue
				break
			link.put(data)
		elif schema.startswith("download:"):
			print "Downloading content from server."
			data = link.get()
			print "Downloaded."
			prompt = schema[9:]
			while True:
				path = raw_input("*save file* " + prompt)
				try:
					with open(path, "w") as fd:
						fd.write(data)
				except IOError, e:
					print "Error:", e
					continue
				break
		elif schema == "done":
			break

