# saved as greeting-client.py
import Pyro5.api
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from datetime import datetime

private_key = Ed25519PrivateKey.generate()
signature = private_key.sign(b"name")
public_key = private_key.public_key()

# name = input("What is your name? ").strip()

server = Pyro5.api.Proxy("PYRONAME:server.uri")    # use name server object lookup uri shortcut

bytes = public_key.public_bytes_raw()
print(bytes)
server.add_manager('name', bytes, 'uri')

productId = server.add_product('name', 'description', 9.99, 3, 1, signature)

print('Current Stock Report')
server.get_report(1)
print('Stock History Report')
server.get_report(2)
print('Low Interest Report')
server.get_report(3, datetime(2023, 9, 21).strftime('%Y-%m-%dT%H:%M:%S.%fZ'))

server.edit_product(productId, -2, signature)

print('After Stock Report')
server.get_report(1)
print('After Stock History Report')
server.get_report(2)
print('After Low Interest Report')
server.get_report(3, datetime(2023, 9, 21).strftime('%Y-%m-%dT%H:%M:%S.%fZ'))

