from BlockChain import BlockChain
from typing import Dict, List
from Transaction import Transaction, TransactionInput, TransactionOutput
from multiprocessing import Queue
import time, random
from Block import Block, BlockHeader
import ScriptEngine as ScrEng
from MerkleTree import MerkleTree
import binascii
from constants import BlockStatus, coinbase, Threshold
import utils

class BitCoinNode:
    id: int = 0
    def __init__(self, blockchain: BlockChain = BlockChain(), txQueue: Queue = Queue(), blkQueue: Queue = Queue()) -> None:
        self.blockchain: BlockChain = blockchain
        self.txQueue: Queue = txQueue
        self.blkQueue: Queue = blkQueue
        self.blkThreshold: Threshold = Threshold.BLK_THRESHOLD
        self.txnThreshold: Threshold = Threshold.TXN_THRESHOLD
        self.generatedTxns: List[Transaction] = []
        self.nodesList: List[BitCoinNode] = []
        BitCoinNode.id += 1
        self.id: int = BitCoinNode.id
        self.target: str = "0000000000000000007e9e4c586439b0cdbe13b1370bdd9435d76a644d047523"
        self.pubKeys: List[str] = []
        self.privateKeys: List[str] = []
        self.addGenesisBlock()

    def processBlk(self, blkCnt: int, emptyExcptn: bool) -> None:
        try:
            newBlk: Block = self.blkQueue.get_nowait()
            # before inserting, block verification is done inside the BlockChain.insert() method
            (result, status) = self.blockchain.insert(newBlk, self.pubKeys[0])
            if not result and status is BlockStatus.MISSING_TXN:
                # Not reliable to get the size of queue
                currentQueueSize = self.txQueue.qsize()
                self.processTxns(currentQueueSize)
                # Last try - if still we get MISSING_TXN, we have to reject this block
                (result, status) = self.blockchain.insert(newBlk, self.pubKeys[0])
                if result:
                    blkCnt += 1
        except:
            # empty blkQueue - ignore
            emptyExcptn = True

    def processBlks(self) -> int:
        blkCnt: int = 0
        emptyExcptn = False
        while (emptyExcptn == False and blkCnt < self.blkThreshold):
            self.processBlk(blkCnt, emptyExcptn)
        return blkCnt

    def processTxns(self, threshold = Threshold.TXN_THRESHOLD) -> None:
        txnCnt: int = 0
        emptyExcptn = False
        while (emptyExcptn == False and txnCnt < threshold):
            try:
                newTx: Transaction = self.txQueue.get_nowait()
                newTxHash = newTx.getHash()
                # Verify this transaction
                verified = True
                for newTxIn in newTx.txnInputs:
                    if not ((newTxIn.prevTxn in self.blockchain.mempool) or (newTxIn.prevTxn in self.blockchain.unspntTxOut)):
                        verified = False
                        break
                    if not ScrEng.verifyScriptSig(newTxIn.scriptSig, newTxIn.dataToSign, newTx.txnOutputs):
                        verified = False
                        break
                if verified:
                    #self.unspntTxOut[newTxHash] = newTx
                    self.mempool[newTxHash] = newTx
                    txnCnt += 1
            except:
                # empty txQueue - ignore
                emptyExcptn = True
                pass
        # give an opportunity to broadcast generated transactions
        self.broadcastTxns()

    def broadcastTxns(self) -> None:
        txn: Transaction
        skip: bool = False
        for txn in self.generatedTxns:
            # Check if the current transaction's inputs have the corresponding outputs available
            skip = False
            for txIn in txn.txnInputs:
                if not (txIn.prevTxn in self.unspntTxOut or txIn.prevTxn in self.mempool):
                    skip = True
                    break;
            if skip is False:
                # now broadcast this transaction to all the other BitCoinNodes
                node: BitCoinNode
                for node in self.nodesList:
                    if node.id != self.id:
                        node.txQueue.put(txn)
            pass
        pass

    def createCoinBaseTxn(self) -> Transaction:
        txnInput = TransactionInput(binascii.hexlify(bytearray(32)), "ffffffff")
        txnOutput = TransactionOutput(coinbase)
        txnOutput.createScriptPubKey(self.pubKey)
        txn = Transaction([txnInput], [txnOutput], 15)
        return txn

    def createBlock(self) -> Block:
        # Check - whether it should be copied, moved or destroyed
        txnList = self.blockchain.mempool
        #self.blockchain.mempool.clear()
        coinBaseTxn = self.createCoinBaseTxn()
        txnList.insert(0, coinBaseTxn)
        newMerkleTree = MerkleTree()
        newMerkleTree.createMerkleTree(txnList)
        nonce = random.randint(0, 2147483647)
        blkHeader = BlockHeader(self.blockchain.longest, nonce, newMerkleTree.mrkl_root, len(txnList))
        newBlk: Block = Block(txnList, blkHeader, newMerkleTree.fullTree)
        return newBlk

    def addGenesisBlock(self, block: Block) -> None:
        (result, status) = self.blockchain.insert(block, self.pubKeys[0])
        assert result == True

    def proofOfWork(self) -> Block:
        restart = True
        newBlk: Block
        while restart is True:
            restart = False
            newBlk = self.createBlock()
            while (newBlk.hash >= self.target):
                nonce = random.randint(0, 2147483647)
                newBlk.blockHeader.nonce = nonce
                newBlk.reCalculateHash()
                # Keep processing the newly arrived blocks
                count = self.processBlks()
                if count > 0:
                    restart = True
                    break
        return newBlk

    def broadcastBlock(self, newBlk: Block) -> None:
        node: BitCoinNode
        for node in self.nodesList:
            if node.id != self.id:
                node.blkQueue.put(newBlk)
        # once we are sure about the newly mined block, add it into our own blockchain, as we broadcast it to other nodes
        (result, status) = self.blockchain.insert(newBlk, self.pubKeys[0])
        assert result == True

    def startRunning(self) -> None:
        while(True):
            # wait for some time
            # time.sleep(random.randint(1, 3))
            # broadcast transaction(s)
            self.broadcastTxns()
            # process received transactions from queue
            self.processTxns()
            # process received blocks from queue
            self.processBlks()
            # start mining for a block
            newBlk = self.proofOfWork()
            # broadbast block to all other nodes
            self.broadcastBlock(newBlk)
