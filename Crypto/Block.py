from CryptoGen import Cryptographic
from Crypto.Hash import SHA256
from typing import Tuple, List

class Block:
    coinBaseValue = 25

    def __init__(self, prevHash: str, publicKey: str):
        self.previousBlockHash: str = prevHash
        self.coinBase: Transaction = Transaction(coinBaseValue, publicKey)
        self.transactions: List[int] = []
        self.blockHash: str = ""

    def returnCoinBase(self) -> Transaction:
        return self.coinBase

    def returnHash(self) -> str:
        return self.blockHash

    def returnPrevBlockHash(self) -> str:
        return self.previousBlockHash

    def returnTxns(self) -> List[int] :
        return self.transactions

    def returnParticularTxn(self, index: int) -> Transaction:
        return self.transactions[index]

    def addTransactionToBlock(self, txn: Transaction):
        self.transactions.append(txn)
