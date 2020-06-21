from CryptoGen import Cryptographic
from Crypto.Hash import SHA256
from typing import Tuple, List
from constants import coinbase
from MerkelTree import MerkleTreeNode
from Transaction import Transaction
import utils

class BlockHeader:
    def __init__(self, prevBlockHash: str, nonce: str, mrkl_root: MerkleTreeNode,numberOfTransactions: int):
        self.prevBlock: str = prevBlockHash
        self.nonce: str = nonce
        self.mrkl_root: MerkleTreeNode = mrkl_root
        self.numberOfTransactions: int = numberOfTransactions

    def getRawDataToHash(self) -> str:
        dataToHash:str  = ""
        dataToHash += self.prevBlock
        dataToHash += self.nonce
        dataToHash += self.mrkl_root
        dataToHash += str(self.numberOfTransactions)
        return dataToHash


class Block:
    def __init__(self, txnList: List[Transaction], blockHeader: BlockHeader, fullMerkleTree: List[MerkleTreeNode]):
        self.txnList: List[Transaction] = txnList
        self.blockHeader: BlockHeader = blockHeader
        self.merkleTree: List[MerkleTreeNode] = fullMerkleTree
        self.hash: str = utils.getHashValue(blockHeader.getRawDataToHash(),"")
