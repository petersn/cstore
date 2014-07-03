#! /usr/bin/python

link.put("password:server-store:Password: ")
password = link.get()
link.put("file:Upload file: ")
data = link.get()
link.put(":Got %i bytes of payload." % len(data))
data = cs_proto.encrypt(data, password)
with open("data/storage", "w") as fd:
	fd.write(data)
link.put(":Done.")
link.put("done")

