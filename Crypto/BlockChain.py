from Block import Block
from typing import List

class BlockChain:
    def __init__(self) -> BlockChain:
        self.blkList: List[Block] = []
        self.latestHash: str = ""

    def addNewBlock(self, blk: Block) -> None:
        self.blkList.append(blk)
        self.latestHash = "" # calculate hash of block 'blk'
