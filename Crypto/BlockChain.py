from Block import Block
from typing import Dict, List, Optional, Tuple
from Transaction import Transaction, TransactionOutput
import copy
from constants import BlockStatus, hashSize
import ScriptEngine, utils, os
from ScriptEngine import comparePubKeyAndScript

class BlockChain:
    def __init__(self) -> None:
        self.mempool: Dict[str, Transaction] = {} # unconfirmed transactions
        self.unspntTxOut: Dict[str, Dict[int, TransactionOutput]] = {} # confirmed but unspent transactions outputs
        self.headMap: Dict[str, BlockNode] = {} # map from a head block hash to the blocknode
        self.longest: str = "" # longest chain-head hash
        self.blockMap: Dict[str, BlockNode] = {} # map from all block hashes to the blocknode
        # blockstates is a Dict[blockHash, (mempool, unspntTxOut)]
        self.blockStates: Dict[str, Tuple[Dict[str, Transaction], Dict[str, Dict[int, TransactionOutput]]]] = {}
        self.blockBalance: Dict[str, int] = {} # map from all block hashes to the corresponding wallet balance
        self.currentBalance: int = 0
        # per block previous transaction hashes as an aid for generating new transactions
        self.blockPrevTxnHashes: Dict[str, Dict[str, List[int]]] = {}
        # currentPrevTxnHashes is a Dict[txnHash, List[indices]]
        self.currentPrevTxnHashes: Dict[str, List[int]] = {}
        self.seenMerkelTreeHashes: List[str] = []

    def isCoinBaseTxn(self, txn: Transaction) -> bool:
        if len(txn.txnInputs) == 1 and txn.txnInputs[0].prevIndex == int("ffffffff", 16):
            # coinbase transaction
            return True
        return False

    # insert a new block into blockchain, return True (if all ok) return False (if block rejected)
    def insert(self, block: Block, pubKey: str) -> Tuple[bool, BlockStatus]:
        pid = os.getpid()
        # if this is Genesis Block
        if block.blockHeader.prevBlock == "":
            print(pid, ": Inserting genesis block..")
            newBlkNode = BlockNode(block)
            self.blockMap[block.hash] = newBlkNode
            self.headMap[block.hash] = newBlkNode
            self.longest = block.hash
            self.seenMerkelTreeHashes.append(block.blockHeader.mrkl_root.hashValue)
            unspntTxOut = {}
            balance: int = 0
            self.blockPrevTxnHashes[block.hash] = {}
            for txn in block.txnList:
                #print("txn in genesisblock")
                nums = list(range(len(txn.txnOutputs)))
                dictTxnOuts = dict(zip(nums, txn.txnOutputs))
                unspntTxOut[txn.getHash()] = dictTxnOuts
                for index, txnOut in enumerate(txn.txnOutputs):
                    if comparePubKeyAndScript(pubKey, txnOut.scriptPubKey):
                        balance += txnOut.amount
                        #print("pubKey found")
                        if txn.getHash() in self.blockPrevTxnHashes[block.hash]:
                            if index not in self.blockPrevTxnHashes[block.hash][txn.getHash()]:
                                self.blockPrevTxnHashes[block.hash][txn.getHash()].append(index)
                        else:
                            self.blockPrevTxnHashes[block.hash][txn.getHash()] = []
                            self.blockPrevTxnHashes[block.hash][txn.getHash()].append(index)
            self.currentPrevTxnHashes = self.blockPrevTxnHashes[block.hash]
            self.blockBalance[block.hash] = balance
            self.currentBalance = self.blockBalance[block.hash]
            self.blockStates[block.hash] = ({}, unspntTxOut)
            self.mempool = self.blockStates[self.longest][0]
            #print(pid, ": mempool = ", self.mempool)
            self.unspntTxOut = self.blockStates[self.longest][1]
            #print(pid, ": unspntTxOut= ", self.unspntTxOut)
        # for any block other than genesis block
        else:
            # prevblock exists in the blockchain
            print(pid, ": Trying to insert a new block..")
            if block.blockHeader.prevBlock in self.blockMap:
                if block.blockHeader.mrkl_root.hashValue in self.seenMerkelTreeHashes:
                    print(pid, ": same merkeltree hash!")
                    return (False, BlockStatus.IDENTICAL_MERKELTREE_HASH)
                else:
                    print(pid, ": new merkeltree hash")
                    self.seenMerkelTreeHashes.append(block.blockHeader.mrkl_root.hashValue)
                # temporary buffer of txOutputs in the current block
                bufferTxOuts: Dict[str, Dict[int, TransactionOutput]] = {}
                for txn in block.txnList:
                    nums = list(range(len(txn.txnOutputs)))
                    dictTxnOuts = dict(zip(nums, txn.txnOutputs))
                    bufferTxOuts[txn.getHash()] = dictTxnOuts
                # to detect cycles in block
                atLeastOnePresent = False
                # check if any transaction in this new block is unknown to us
                # verify other important semantics
                for txn in block.txnList:
                    #print(pid, ": mempool = ", self.mempool)
                    #print(pid, ": txnHash = ", txn.getHash())
                    #print(pid, ": blockStates.mempool = ", self.blockStates[block.blockHeader.prevBlock][0])
                    #assert self.mempool is self.blockStates[block.blockHeader.prevBlock][0]
                    if self.isCoinBaseTxn(txn):
                        continue
                    if txn.getHash() not in self.blockStates[block.blockHeader.prevBlock][0]:
                        # invalid transaction; reject the block
                        return (False, BlockStatus.MISSING_TXN)
                    for txnIn in txn.txnInputs:
                        if txnIn.prevTxn not in self.blockStates[block.blockHeader.prevBlock][1]:
                            # prev transaction not present in unspntTxOut
                            if txnIn.prevTxn not in bufferTxOuts:
                                # prev transaction not present in current block too
                                return (False, BlockStatus.MISSING_PREV_TXN)
                        # TODO? check if the txnOutputs list/dict is not empty?
                        atLeastOnePresent = True
                if atLeastOnePresent == False:
                    return (False, BlockStatus.CYCLE_DETECTED)

                # update the mempool and unspntTxOut structures for the new block
                #self.blockStates[block.hash] = (copy.deepcopy(self.blockStates[block.blockHeader.prevBlock][0]), copy.deepcopy(self.blockStates[block.blockHeader.prevBlock][1]))
                self.blockStates[block.hash] = copy.deepcopy(self.blockStates[block.blockHeader.prevBlock])
                self.blockPrevTxnHashes[block.hash] = copy.deepcopy(self.blockPrevTxnHashes[block.blockHeader.prevBlock])
                self.blockBalance[block.hash] = copy.deepcopy(self.blockBalance[block.blockHeader.prevBlock])
                print(pid, ": blockbalance[block.hash] = ", self.blockBalance[block.hash])
                for txn in block.txnList:
                    if self.isCoinBaseTxn(txn):
                        # skip correct?
                        continue
                    if txn.getHash() in self.blockStates[block.hash][0]:
                        nums = list(range(len(txn.txnOutputs)))
                        dictTxnOuts = dict(zip(nums, txn.txnOutputs))
                        # can't do the following commented operation now
                        #self.blockStates[block.hash][1][txn.getHash()] = dictTxnOuts
                        self.blockStates[block.hash][0].pop(txn.getHash())
                        # also remove the relevant txnOutputs from unspntTxOut
                        for txnIn in txn.txnInputs:
                            # we can use block.hash instead of prevBlock's hash, as we have done deepcopy above
                            # .pop() would work, as we have used a Dict instead of a List - so the indices for other elements won't change
                            if txnIn.prevTxn in self.blockStates[block.hash][1]:
                                if txnIn.prevIndex in self.blockStates[block.hash][1][txnIn.prevTxn]:
                                    tmpTxnOut: TransactionOutput = self.blockStates[block.hash][1][txnIn.prevTxn][txnIn.prevIndex]
                                    if comparePubKeyAndScript(pubKey, tmpTxnOut.scriptPubKey):
                                        self.blockBalance[block.hash] -= tmpTxnOut.amount
                                        self.currentBalance = self.blockBalance[block.hash]
                                    self.blockStates[block.hash][1][txnIn.prevTxn].pop(txnIn.prevIndex)
                            elif txnIn.prevTxn in bufferTxOuts:
                                if txnIn.prevIndex in bufferTxOuts[txnIn.prevTxn]:
                                    tmpTxnOut: TransactionOutput = bufferTxOuts[txnIn.prevTxn][txnIn.prevIndex]
                                    if comparePubKeyAndScript(pubKey, tmpTxnOut.scriptPubKey):
                                        self.blockBalance[block.hash] -= tmpTxnOut.amount
                                        self.currentBalance = self.blockBalance[block.hash]
                                    bufferTxOuts[txnIn.prevTxn].pop(txnIn.prevIndex)
                            else:
                                # Invalid path; impossible to come here
                                print(pid, ": TxnInput => ", txnIn.prevTxn, " not present in unspntTxOut and bufferTxOuts!")
                                return (False, BlockStatus.REJECTED)
                            if txnIn.prevTxn in self.blockPrevTxnHashes[block.hash] and txnIn.prevIndex in self.blockPrevTxnHashes[block.hash][txnIn.prevTxn]:
                                self.blockPrevTxnHashes[block.hash][txnIn.prevTxn].remove(txnIn.prevIndex)

                        # on becoming an empty list of txnOutputs, remove the transaction hash from unspntTxOut
                        if txnIn.prevTxn in self.blockStates[block.hash][1] and len(self.blockStates[block.hash][1][txnIn.prevTxn].keys()) == 0:
                            self.blockStates[block.hash][1].pop(txnIn.prevTxn)

                    else:
                        # invalid path; impossible to come here
                        print(pid, ": Txn => ", txn.getHash(), " not present in mempool!")
                        return (False, BlockStatus.REJECTED)

                print(pid, ": blockBalance[block.hash] (in between)= ", self.blockBalance[block.hash])
                # Now, add the buffered (temporary) txnOuts into unspntTxOut
                for txn in block.txnList:
                    if self.isCoinBaseTxn(txn):
                        nums = list(range(len(txn.txnOutputs)))
                        dictTxnOuts = dict(zip(nums, txn.txnOutputs))
                        self.blockStates[block.hash][1][txn.getHash()] = dictTxnOuts
                        continue
                    if len(bufferTxOuts[txn.getHash()].keys()) != 0:
                        self.blockStates[block.hash][1][txn.getHash()] = bufferTxOuts[txn.getHash()]

                # add the new block to blockMap and headMap
                newBlkNode = BlockNode(block, self.blockMap[block.blockHeader.prevBlock])
                self.blockMap[block.hash] = newBlkNode
                self.headMap[block.hash] = newBlkNode
                # update the longest pointer and corresponding mempool and unspntTxout cache if necessary
                if block.blockHeader.prevBlock in self.headMap:
                    print(pid, ": newblocknode.len = ", newBlkNode.len)
                    print(pid, ": currentlongest len = ", self.headMap[self.longest].len)
                    if newBlkNode.len > self.headMap[self.longest].len:
                        print(pid, ": chang longest chain to => (newly added blockhash)", block.hash)
                        self.longest = block.hash
                        self.mempool = self.blockStates[self.longest][0]
                        self.unspntTxOut = self.blockStates[self.longest][1]
                    self.headMap.pop(block.blockHeader.prevBlock)
                for txn in block.txnList:
                    for index, txnOut in enumerate(txn.txnOutputs):
                        if comparePubKeyAndScript(pubKey, txnOut.scriptPubKey):
                            self.blockBalance[block.hash] += txnOut.amount
                            if txn.getHash() in self.blockPrevTxnHashes[block.hash]:
                                if index not in self.blockPrevTxnHashes[block.hash][txn.getHash()]:
                                    self.blockPrevTxnHashes[block.hash][txn.getHash()].append(index)
                            else:
                                self.blockPrevTxnHashes[block.hash][txn.getHash()] = []
                                self.blockPrevTxnHashes[block.hash][txn.getHash()].append(index)
                print(pid, ": blockBalance[block.hash] (at last)= ", self.blockBalance[block.hash])
                # currentBalance will always correspond to the current longest chain block head
                self.currentBalance = self.blockBalance[self.longest]
                # currentPrevTxnHashes will always correspond to the longest chain
                self.currentPrevTxnHashes = self.blockPrevTxnHashes[self.longest]
            # prevblock absent in the blockchain
            else:
                # invalid block; reject it
                return (False, BlockStatus.MISSING_PREV_BLOCK)
        print(pid, ": new block inserted successfully!")
        return (True, BlockStatus.VALID)

# unit of node used inside blockchain implemented as linked list
class BlockNode:
    def __init__(self, block: Block, prevBlk = None) -> None:
        self.block = block
        if (prevBlk == None):
            self.prevBlk = None
            self.len: int = 1
        else:
            self.prevBlk = prevBlk
            self.len = self.prevBlk.len + 1
