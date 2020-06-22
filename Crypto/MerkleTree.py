'''
Usage:
1) To Create
merkle_tree = MerkleTree(arity)
merkle_tree.createMerkleTree(<List of Transactions(str now)>)
2) To Verify
verifyMerkleTree(merkle_tree.mrkl_root)


EG)newMerkleTree = MerkleTree(2)
newMerkleTree.createMerkleTree(["a","b","c","d","e","f"])
print(verifyMerkleTree(newMerkleTree.mrkl_root))
'''

from utils import getHashValue, verifyMerkleTree
from typing import List
from constants import hashSize
from Transaction import Transaction,TransactionInput,TransactionOutput
class MerkleTreeNode:
    def __init__(self,value = "") -> None:
        self.hashValue: str = value
        self.nodeList = []

    def calculate(self, nodeList):
        self.nodeList = nodeList
        for i in nodeList:
            self.hashValue += i.hashValue
        self.hashValue = getHashValue(self.hashValue, hashSize)

    def __eq__(self, other) -> bool :
        if other is None:
            return False
        return self.hashValue == other.hashValue

class MerkleTree:
    def __init__(self, arity: int = 2) -> None:
        self.mrkl_root: MerkleTreeNode = MerkleTreeNode()
        self.fullTree: List[MerkleTreeNode] = []
        self.arity = arity

    def __eq__(self, other) -> bool:
        if other is None:
            return False
        return other.mrkl_root==self.mrkl_root

    def getTxnNodes(self, txnList: List[Transaction]) -> List[MerkleTreeNode] :
        txnNodes = []
        for i in txnList:
            txnNodes.append(MerkleTreeNode(i.hash))

        return txnNodes

    def get_new_level(self, txnNodes: List[MerkleTreeNode]) -> List[MerkleTreeNode]:
        index: int = 0
        newLevel: List[MerkleTreeNode] = []
        while index<len(txnNodes):
            nodeList = []
            for i in range(self.arity):
                if index>=len(txnNodes):
                    break
                nodeList.append(txnNodes[index])
                index+=1
            newTempNode: MerkleTreeNode = MerkleTreeNode()
            newTempNode.calculate(nodeList)
            newLevel.append(newTempNode)

        return newLevel

    def createMerkleTree(self, txnList: List[Transaction]):
        txnNodes: List[MerkleTreeNode] = self.getTxnNodes(txnList)
        self.fullTree.extend(txnNodes)
        newLevel: List[MerkleTreeNode] = self.get_new_level(txnNodes)
        self.fullTree.extend(newLevel)
        while len(newLevel)>1:
            newLevel = self.get_new_level(newLevel)
            self.fullTree.extend(newLevel)

        self.mrkl_root = newLevel[0]


merkle_tree = MerkleTree(5)
# merkle_tree.createMerkleTree(["a","b","c","d","e","f","g"])
print(verifyMerkleTree(merkle_tree.mrkl_root))
