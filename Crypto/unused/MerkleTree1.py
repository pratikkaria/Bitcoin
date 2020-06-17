from Crypto.Hash import SHA256
from collections import OrderedDict
from typing import List

class MerkleTree:

    def __init__(self, txnList: List[str]) -> List[str]:
        self.listOfTxns: List[str] = txnList
        self.mrkl_root: str = ""

    def getHashValue(self,left: str, right: str) -> str:
        newHash = SHA256.new()
        newData: str = left+right
        newHash.update(newData.encode('utf-8'))

        return newHash.hexdigest()


    def get_new_list(self, tempList: List[str]) -> List[str]:
        newList: List[str] = []
        index: int = 0
        while(index<len(tempList)):
            left:str = tempList[index]
            index+=1
            right:str = ""
            if index!=len(tempList):
                right = tempList[index]

            newList.append(self.getHashValue(left,right))
            index+=1

        return newList

    def merkle_tree(self):
        tempList: List[str] = self.listOfTxns
        newList: List[str] = self.get_new_list(tempList)
        while(len(newList)!=1):
            newList = self.get_new_list(newList)

        self.mrkl_root = newList[0]

    def getRoot(self) -> str:
        return self.mrkl_root

temp = MerkleTree(['a','e','c','d'])
temp.merkle_tree()
print(temp.mrkl_root)
