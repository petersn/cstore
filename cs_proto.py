#! /usr/bin/python

import os, struct, hashlib

# Minimal authenticated randomized stream cipher.
sha256 = lambda s: hashlib.sha256(s).digest()
stream_enc = lambda m, k: "".join(chr(ord(sha256(str(i) + ":" + k)[0]) ^ ord(b)) for i, b in enumerate(m))

def encrypt(m, key):
	nonce = os.urandom(16)
	key = nonce + sha256(key)
	return nonce + sha256(m + key) + stream_enc(m, key)

def decrypt(m, key):
	nonce, mac, m = m[:16], m[16:48], m[48:]
	key = nonce + sha256(key)
	m = stream_enc(m, key)
	if sha256(m + key) == mac:
		return m

# Diffie-Hellman parameters.
dh_modulus = 2**2048 + 10029811
dh_gen = 3
dh_bits = 2048

def urandom_bits(x):
	assert x % 8 == 0
	return int(os.urandom(x / 8).encode("hex"), 16)

def modular_inverse(a, m):
	"""modular_inverse(a, m) -> b such that (a * b) % m == 1"""
	a, c = a % m, 1
	while a > 1:
		q, a = m / a, m % a
		c = (-c * q) % m
	if a == 1:
		return c

def hash_password(password, distinguish=""):
	for i in xrange(1024):
		password = hashlib.sha256("cstore:1:" + distinguish + password).hexdigest()
	return password

class CryptoLink:
	def __init__(self, wfile, rfile=None, role=0):
		self.wfile, self.rfile = wfile, rfile or wfile
		self.role = role

	def _send_num(self, x):
		self.wfile.write("%x\n" % x)
		self.wfile.flush()

	def _recv_num(self):
		return int(self.rfile.readline().strip(), 16) % dh_modulus

	def diffie_hellman(self, exponent, base=dh_gen):
		gx = pow(base, exponent, dh_modulus)
		self._send_num(gx)
		gy = self._recv_num()
		assert gy != 1
		gxy = pow(gy, exponent, dh_modulus)
		return gxy

	def handshake(self, password):
		password = sha256(password)
		password_num = int(password.encode("hex"), 16)
		# Run the Socialist Millionaire protocol
		x = urandom_bits(dh_bits)
		y = urandom_bits(dh_bits)
		z = urandom_bits(dh_bits)
		shared1 = self.diffie_hellman(x)
		shared2 = self.diffie_hellman(y)
		pub1 = pow(shared2, z, dh_modulus)
		self._send_num(pub1)
		other_pub1 = self._recv_num()
		assert pub1 != other_pub1
		if self.role:
			pub1, other_pub1 = other_pub1, pub1
		t = (pub1 * modular_inverse(other_pub1, dh_modulus)) % dh_modulus
		pub2 = (pow(dh_gen, z, dh_modulus) * pow(shared1, password_num, dh_modulus)) % dh_modulus
		self._send_num(pub2)
		other_pub2 = self._recv_num()
		assert pub2 != other_pub2
		if self.role:
			pub2, other_pub2 = other_pub2, pub2
		u = (pub2 * modular_inverse(other_pub2, dh_modulus)) % dh_modulus
		c = self.diffie_hellman(y, base=u)
		if c == t:
			self.shared_secret = sha256("%s:%s:%s" % (password, shared1, shared2))
			return True
		# Otherwise, secrets don't match.
		return False

	def put(self, s):
		ciphertext = encrypt(s, self.shared_secret)
		self.wfile.write(struct.pack("<Q", len(ciphertext)))
		self.wfile.write(ciphertext)
		self.wfile.flush()

	def get(self):
		length = self.rfile.read(8)
		if len(length) != 8:
			return None
		length, = struct.unpack("<Q", length)
		ciphertext = self.rfile.read(length)
		return decrypt(ciphertext, self.shared_secret)

if __name__ == "__main__":
	import getpass, sys
	if len(sys.argv) == 1:
		password = getpass.getpass("Password: ")
		print "Main login:", hash_password(password, distinguish="main-login")
	elif len(sys.argv) == 2:
		import json
		with open("cstore_config.json") as fd:
			config = json.load(fd)
		data = open(sys.argv[1]).read()
		password = getpass.getpass("Signal: ")
		recv = hash_password(password, distinguish="signal-client")
		signal_hash = hash_password(recv, distinguish="signal-address" + config["salt"])
		encryption_key = hash_password(recv, distinguish="signal-key" + config["salt"])
		with open("signals/" + signal_hash, "w") as fd:
			fd.write(encrypt(data, encryption_key))
	else:
		print "Usage: cs_proto.py [file.py]"
		print "With a python script passed, installs a signal."
		print "Otherwise, hashes for login password."

