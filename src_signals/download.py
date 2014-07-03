#! /usr/bin/python

try:
	with open("data/storage") as fd:
		data = fd.read()
except IOError:
	link.put(":No file uploaded.")
else:
	link.put("password:server-store:Password: ")
	password = link.get()
	data = cs_proto.decrypt(data, password)
	link.put(":Sending %i bytes of payload." % len(data))
	link.put("download:Path: ")
	link.put(data)
link.put("done")

