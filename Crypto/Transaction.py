from CryptoGen import Cryptographic
from Crypto.Hash import SHA256
from typing import Tuple, List

class Transaction:

    class Input:

        def __init__(self, prevHash: str, index: str):
            self.prevTxnHash: str = prevHash
            self.prevTxnIndex: int = index
            self.signature: str = ""

        def addSignature(self,signature: str):
            self.signature = signature

        def __eq__(self, other)-> bool:
            return (self.__class__ == other.__class__ and self.x == other.x)
