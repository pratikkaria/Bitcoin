from typing import Dict
from enum import IntEnum, auto

opcodeList: Dict[str, int] = {"OP_DUP":1,"OP_HASH160":1,"OP_EQUALVERIFY":1,"OP_CHECKSIG":1,"OP_CHECKMULTISIG":1}
coinbase = 25
hashSize = 256 #256,224,384,512,160
arity = 2 #Arity of merkle tree
Y = 10  #Limit on number of coins
X = 5 #Number of coins to deduct
lockTime = 15
votingFee = 1
genesisTxnAmount = 1000
candidates = ["Apple", "Mango", "Banana", "Orange"]
contractFees = 1
txnLimit = 10
perTxnLimit = 3
nNodes = 10
# noncesize 8 bytes = 32 bits (in hex)
nonceSize = 8

class BlockStatus(IntEnum):
    VALID = auto()
    REJECTED = auto()
    MISSING_TXN = auto()
    INVALID = auto()
    MISSING_PREV_TXN = auto()
    MISSING_PREV_BLOCK = auto()
    CYCLE_DETECTED = auto()
    IDENTICAL_MERKELTREE_HASH = auto()

class Threshold(IntEnum):
    TXN_THRESHOLD = 50
    BLK_THRESHOLD = 500
