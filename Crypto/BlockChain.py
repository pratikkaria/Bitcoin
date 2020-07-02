from Block import Block
from typing import Dict, List, Optional, Tuple
from Transaction import Transaction, TransactionOutput

class BlockChain:
    def __init__(self) -> None:
        self.headMap: Dict[str, BlockNode] = {} # map from a head block hash to the blocknode
        self.headStates: Dict[str, Tuple[Dict[str, Transaction], Dict[str, TransactionOutput]]] = {}
        self.longest: str = "" # longest chain-head hash
        self.blockMap: Dict[str, BlockNode] = {} # map from all block hashes to the blocknode

    # insert a new block into blockchain, return True (if all ok) return False (if block rejected)
    def insert(self, block: Block, mempool: Dict[str, Transaction], unspntTxOut: Dict[str, TransactionOutput]) -> Tuple[bool, Dict, Dict]:
        ret0 = {}
        ret1 = {}
        if block.blockHeader.prevBlock is "":
            # Genesis Block
            newBlkNode = BlockNode(block)
            self.headMap[block.hash] = newBlkNode
            self.longest = block.hash
            self.headStates[block.hash] = (mempool, unspntTxOut)
        else:
            # if prevblock is already one of the heads
            if block.blockHeader.prevBlock in self.headMap:
                newBlkNode = BlockNode(block, self.headMap[block.blockHeader.prevBlock])
                self.blockMap[block.hash] = newBlkNode
                self.headMap[block.hash] = newBlkNode
                if self.longest == "" or self.headMap[self.longest].len < newBlkNode.len:
                    self.headStates[self.longest] = (mempool, unspntTxOut)
                    self.longest = block.hash
                    ret0 = self.headStates[block.blockHeader.prevBlock][0]
                    ret1 = self.headStates[block.blockHeader.prevBlock][1]
                self.headMap.pop(block.blockHeader.prevBlock)
                self.headStates.pop(block.blockHeader.prevBlock)
            # if prevblock is not a head
            elif block.blockHeader.prevBlock in self.blockMap:
                newBlkNode = BlockNode(block, self.blockMap[block.blockHeader.prevBlock])
                self.blockMap[block.hash] = newBlkNode
                self.headMap[block.hash] = newBlkNode
            # if prevblock doesn't exist in any map
            else:
                # reject / ignore this block
                return (False, ret0, ret1)
        return (True, ret0, ret1)

# unit of node used inside blockchain implemented as linked list
class BlockNode:
    def __init__(self, block: Block, prevBlk: Optional[BlockNode] = None) -> None:
        self.block = block
        self.prevBlk = prevBlk
        if (self.prevBlk == None):
            self.len: int = 1
        else:
            self.len = self.prevBlk.len + 1
