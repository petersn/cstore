= cstore

Simple reconfigurable cryptographic server, written in only 255 lines of code.
A client connects to the server, the parties authenticate each other with the socialist millionaire protocol, and switch to a symmetrically encrypted link.
This provides forward security, mutual authentication, a.
The client provides a command line interface for sending "signals" (which act like user commands) to the server.
When the server receives a signal, it derives (via hashing) an address, and an encryption key.
It then reads from `signals/address`, and decrypts the contents under the derived key, and runs it.
The read out code communicates with the client, and can make requests for arbitrary strings and file contents.

The easiest way to think about this is that the server consists of a skeleton that decrypts additional features as they are needed.
Further more, because the key material for decrypting these features are provided by the client, a complete compromise of the server isn't sufficient to reveal how the server is configured.
An example application of this is shown with the upload/download/bad\_download scripts.
The upload and download signals allow the user to store an encrypted payload on the server, while the bad\_download signal shreds the data stored on the server, and sends an emergency "I am being coerced" email to a trusted friend.
Two signals may be installed with the same name, provided they have different passwords.
Thus, you could install download and bad\_download both as "download", but have one password be the emergency coerced password.

The applications are limited only by the total entropy of the universe.
All implemented in just 255 lines of code in pure Python with no non-standard libraries.
