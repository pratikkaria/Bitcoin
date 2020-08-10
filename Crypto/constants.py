from typing import Dict
from enum import IntEnum, auto

opcodeList: Dict[str, int] = {"OP_DUP":1,"OP_HASH160":1,"OP_EQUALVERIFY":1,"OP_CHECKSIG":1,"OP_CHECKMULTISIG":1}
coinbase = 25
hashSize = 256 #256,224,384,512,160
arity = 2 #Arity of merkle tree
Y = 10  #Limit on number of coins
X = 5 #Number of coins to deduct
lockTime = 15
class BlockStatus(IntEnum):
    VALID = auto()
    REJECTED = auto()
    MISSING_TXN = auto()
    INVALID = auto()
    MISSING_PREV_BLOCK = auto()
class Threshold(IntEnum):
    TXN_THRESHOLD = 50
    BLK_THRESHOLD = 500
