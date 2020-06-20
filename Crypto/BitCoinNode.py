from BlockChain import BlockChain
from typing import Dict
from Transaction import Transaction
from multiprocessing import Queue

class BitCoinNode:
    def __init__(self, blockchain = BlockChain(), unspntTxOut = {}, txQueue = Queue(), blkQueue = Queue()):
        self.blockchain: BlockChain = blockchain
        self.unspntTxOut: Dict[str, Transaction] = unspntTxOut
        self.txQueue = txQueue
        self.blkQueue = blkQueue

    def startRunning(self):
        while(True):
            try:
                newTx = self.txQueue.get_nowait()
                newTxHash = newTx.getHash()
                if newTx.validate():
                    self.unspntTxOut[newTxHash] = newTx
            except:
                # empty txQueue - ignore
                nop
            try:
                newBlk = self.blkQueue.get_nowait()
                newBlkHash = newBlk.getHash()
                if newBlk.validate():
                    self.blockchain.addNewBlock(newBlk)
            except:
                # empty blkQueue - ignore
                nop
            self.generateTxs()
            self.broadcastTxs()
            # After generating and broadcasting transactions, go for creating a block
            self.proofOfWork()
            self.createBlock()
            self.broadcastBlock()

    def createBlock(self):
        nop
        
    def broadcastBlock(self):
        nop

    def broadcastTxs(self):
        # broadcast already generated transactions
        nop

    def generateTxs(self):
        # generate transactions
        nop

    def proofOfWork(self):
        # carry out proof of work
        nop
