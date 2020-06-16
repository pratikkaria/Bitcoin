from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from typing import Tuple


class Cryptographic:
    def __init__(self, numberOfKeyBits: int):
        (self.publicKey, self.privateKey) = self.generateKeys(numberOfKeyBits)

    def generateKeys(self, bits: int) -> Tuple[str, str]:
        new_key = RSA.generate(bits, e=65537)
        public_key = SHA256.new()
        private_key = SHA256.new()
        public_key.update(new_key.publickey().exportKey("PEM"))
        private_key.update(new_key.exportKey("PEM"))
        return (public_key.hexdigest(), private_key.hexdigest())
