from utils import getHashValue, verifyMerkleTree
from collections import OrderedDict
from typing import List

class MerkleTreeNode:
    def __init__(self,value = ""):
        self.hashValue: str = ""
        self.leftNode: MerkleTreeNode = None
        self.rightNode: MerkleTreeNode = None

    def calculate(self, leftNode, rightNode):
        self.leftNode = leftNode
        self.rightNode = rightNode
        if self.rightNode is not None:
            self.hashValue = getHashValue(self.leftNode.hashValue, self.rightNode.hashValue)
        else:
            self.hashValue = getHashValue(self.leftNode.hashValue, "" )


class MerkleTree:
    def __init__(self):
        self.mrkl_root = None

    def getTxnNodes(self, txnList):
        txnNodes = []
        for i in txnList:
            txnNodes.append(MerkleTreeNode(i))

        return txnNodes

    def get_new_level(self, txnNodes):
        index: int = 0
        newLevel = []
        while index<len(txnNodes):
            leftNode = txnNodes[index]
            index+=1
            rightNode = None
            if index!=txnNodes:
                rightNode = txnNodes[index]

            newTempNode = MerkleTreeNode()
            newTempNode.calculate(leftNode,rightNode)
            newLevel.append(newTempNode)
            index+=1

        return newLevel

    def createMerkleTree(self, txnList: List[str]):
        txnNodes = self.getTxnNodes(txnList)
        newLevel = self.get_new_level(txnNodes)
        while len(newLevel)>1:
            newLevel = self.get_new_level(newLevel)
            
        self.mrkl_root = newLevel[0]






newMerkleTree = MerkleTree()
newMerkleTree.createMerkleTree(["a","b","c","d"])
print(verifyMerkleTree(newMerkleTree.mrkl_root))
