from Block import Block
from typing import Dict, List, Optional, Tuple
from Transaction import Transaction, TransactionOutput
import copy

class BlockChain:
    def __init__(self) -> None:
        self.mempool: Dict[str, Transaction] = {} # unconfirmed transactions
        self.unspntTxOut: Dict[str, List[TransactionOutput]] = {} # confirmed but unspent transactions outputs
        self.headMap: Dict[str, BlockNode] = {} # map from a head block hash to the blocknode
        self.longest: str = "" # longest chain-head hash
        self.blockMap: Dict[str, BlockNode] = {} # map from all block hashes to the blocknode
        # blockstates is a Dict[blockHash, (mempool, unspntTxOut)]
        self.blockStates: Dict[str, Tuple[Dict[str, Transaction], Dict[str, List[TransactionOutput]]]] = {}

    # insert a new block into blockchain, return True (if all ok) return False (if block rejected)
    def insert(self, block: Block) -> bool:
        # if this is Genesis Block
        if block.blockHeader.prevBlock is "":
            newBlkNode = BlockNode(block)
            self.blockMap[block.hash] = newBlkNode
            self.headMap[block.hash] = newBlkNode
            self.longest = block.hash
            unspntTxOut = {}
            for txn in block.txnList:
                unspntTxOut[txn.getHash()] = txn.txnOutputs
            self.blockStates[block.hash] = ({}, unspntTxOut)
            self.mempool = self.blockStates[self.longest][0]
            self.unspntTxOut = self.blockStates[self.longest][1]
        # for any block other than genesis block
        else:
            # prevblock exists in the blockchain
            if block.blockHeader.prevBlock in self.blockMap:
                # check if any transaction in this new block is unknown to us
                for txn in block.txnList:
                    if txn.getHash() not in self.blockStates[block.blockHeader.prevBlock][0]:
                        # invalid transaction; reject the block
                        return False
                # update the mempool and unspntTxOut structures for the new block
                self.blockStates[block.hash] = (copy.deepcopy(self.blockStates[block.blockHeader.prevBlock][0]), copy.deepcopy(self.blockStates[block.blockHeader.prevBlock][1]))
                for txn in block.txnList:
                    if txn.getHash() in self.blockStates[block.hash][0]:
                        self.blockStates[block.hash][1][txn.getHash()] = txn.txnOutputs
                        self.blockStates[block.hash][0].pop(txn.getHash())
                    else:
                        # invalid path; impossible to come here
                        return False
                # add the new block to blockMap and headMap
                newBlkNode = BlockNode(block, self.blockMap[block.blockHeader.prevBlock])
                self.blockMap[block.hash] = newBlkNode
                self.headMap[block.hash] = newBlkNode
                # update the longest pointer and corresponding mempool and unspntTxout cache if necessary
                if block.blockHeader.prevBlock in self.headMap:
                    if newBlkNode.len > self.headMap[self.longest].len:
                        self.longest = block.hash
                        self.mempool = self.blockStates[self.longest][0]
                        self.unspntTxOut = self.blockStates[self.longest][1]
                    self.headMap.pop(block.blockHeader.prevBlock)
            # prevblock absent in the blockchain
            else:
                # invalid block; reject it
                return False
        return True

# unit of node used inside blockchain implemented as linked list
class BlockNode:
    def __init__(self, block: Block, prevBlk: Optional[BlockNode] = None) -> None:
        self.block = block
        self.prevBlk = prevBlk
        if (self.prevBlk == None):
            self.len: int = 1
        else:
            self.len = self.prevBlk.len + 1
