#! /usr/bin/python

import socket, getpass, readline, hashlib, sys
import cs_proto

if len(sys.argv) != 2:
	print "Usage: cs_client host"
	exit(2)

def get_hashed_pass(prompt, distinguish):
	password = getpass.getpass(prompt)
	password = cs_proto.hash_password(distinguish+password)
	return password

s = socket.create_connection((sys.argv[1], 50666))
link = cs_proto.CryptoLink(s.makefile())
password = get_hashed_pass("Password: ", "main-login")

if not link.handshake(password):
	print "Authentication error."
	exit(1)

while True:
	command = raw_input("> ")
	if command == "passwd":
		password = get_hashed_pass("New password: ", "main-login")
		link.put("passwd"+password)
	elif command == "signal":
		password = get_hashed_pass("Signal code: ", "signal-client")
		link.put("signal"+password)
	else:
		link.put(command)
	value = link.get()
	if value is None:
		print "Terminated."
		break
	print value

