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
import os


class BitCoinNode:
    id: int = 0
    #def __init__(self, pubKey: str, privateKey: str, nNodes: int, blockchain: BlockChain = BlockChain(), txQueue: Queue = Queue(), blkQueue: Queue = Queue()) -> None:
    def __init__(self, pubKey: str, privateKey: str, nNodes: int) -> None:
        blockchain = BlockChain()
        txQueue = Queue()
        blkQueue = Queue()
        self.blockchain: BlockChain = blockchain
        print("blockchain: ", self.blockchain)
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
        if pubKey:
            self.pubKeys.append(pubKey)
        self.privateKeys: List[str] = []
        if privateKey:
            self.privateKeys.append(privateKey)
        #self.createGenesisBlock(nNodes)

    def setGeneratedTxns(self, txns: List[Transaction]) -> None:
        self.generatedTxns = txns

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
        return emptyExcptn

    def processBlks(self) -> int:
        blkCnt: int = 0
        emptyExcptn = False
        while (emptyExcptn == False and blkCnt < self.blkThreshold):
            emptyExcptn = self.processBlk(blkCnt, emptyExcptn)
        return blkCnt

    def processTxns(self, threshold = Threshold.TXN_THRESHOLD) -> None:
        pid = os.getpid()
        txnCnt: int = 0
        emptyExcptn = False
        while (emptyExcptn == False and txnCnt < threshold):
            try:
                newTx: Transaction = self.txQueue.get_nowait()
                newTxHash = newTx.getHash()
                print(pid, ": transaction processing..")
                # Verify this transaction
                verified = True
                for newTxIn in newTx.txnInputs:
                    if not ((newTxIn.prevTxn in self.blockchain.mempool) or (newTxIn.prevTxn in self.blockchain.unspntTxOut)):
                        verified = False
                        break
                    print("partially verified")
                    if not ScrEng.verifyScriptSig(newTxIn.scriptSig, newTxIn.dataToSign, newTx.txnOutputs):
                        verified = False
                        break
                if verified:
                    #self.unspntTxOut[newTxHash] = newTx
                    print(pid, ": transaction verified")
                    self.mempool[newTxHash] = newTx
                    txnCnt += 1
            except:
                # empty txQueue - ignore
                emptyExcptn = True
                pass
        # give an opportunity to broadcast generated transactions
        self.broadcastTxns()

    def broadcastTxns(self) -> None:
        pid = os.getpid()
        txn: Transaction
        skip: bool = False
        for txn in self.generatedTxns:
            # Check if the current transaction's inputs have the corresponding outputs available
            skip = False
            for txIn in txn.txnInputs:
                if not (txIn.prevTxn in self.blockchain.unspntTxOut or txIn.prevTxn in self.blockchain.mempool):
                    skip = True
                    break;
            if skip is False:
                # now broadcast this transaction to all the other BitCoinNodes
                print(pid, ": broadcasting transaction..")
                node: BitCoinNode
                for node in self.nodesList:
                    if node.id != self.id:
                        node.txQueue.put(txn)
            self.generatedTxns.remove(txn   )
            pass
        pass

    def createCoinBaseTxn(self, amount: int = coinbase) -> Transaction:
        txnOutput = TransactionOutput(amount)
        txnOutput.createScriptPubKey(self.pubKeys[0])
        txnInput = TransactionInput(str(binascii.hexlify(bytearray(32))), "ffffffff")
        txn = Transaction([txnInput], [txnOutput], 15)
        return txn

    def createBlock(self) -> Block:
        # TODO: Transaction Fees
        # Check - whether it should be copied, moved or destroyed
        txnList = self.blockchain.mempool.values()
        #self.blockchain.mempool.clear()
        coinBaseTxn = self.createCoinBaseTxn()
        txnList.insert(0, coinBaseTxn)
        newMerkleTree = MerkleTree()
        newMerkleTree.createMerkleTree(txnList)
        nonce = random.randint(0, 2147483647)
        blkHeader = BlockHeader(self.blockchain.longest, nonce, newMerkleTree.mrkl_root, len(txnList))
        newBlk: Block = Block(txnList, blkHeader, newMerkleTree.fullTree)
        return newBlk

    def addGenesisBlock(self, txnList: List[Transaction]) -> None:
        pid = os.getpid()
        newMerkleTree = MerkleTree()
        newMerkleTree.createMerkleTree(txnList)
        nonce = random.randint(0, 2147483647)
        print("nonce: ", nonce)
        print("longest: ", self.blockchain.longest)
        blkHeader = BlockHeader(self.blockchain.longest, str(nonce), newMerkleTree.mrkl_root, len(txnList))
        block: Block = Block(txnList, blkHeader, newMerkleTree.fullTree)
        (result, status) = self.blockchain.insert(block, self.pubKeys[0])
        print("assert")
        assert result == True

    def createGenesisBlock(self, nNodes: int) -> None:
        pid = os.getpid()
        txnList: List[Transaction] = []
        for i in range(0, nNodes):
            txn: Transaction = self.createCoinBaseTxn(1000)
            txnList.append(txn)
        newMerkleTree = MerkleTree()
        newMerkleTree.createMerkleTree(txnList)
        nonce = random.randint(0, 2147483647)
        blkHeader = BlockHeader(self.blockchain.longest, str(nonce), newMerkleTree.mrkl_root, len(txnList))
        block: Block = Block(txnList, blkHeader, newMerkleTree.fullTree)
        (result, status) = self.blockchain.insert(block, self.pubKeys[0])
        print("assert")
        assert result == True

    def proofOfWork(self) -> Block:
        pid = os.getpid()
        restart = True
        newBlk: Block
        while restart is True:
            restart = False
            print(pid, ": proof of work..")
            newBlk = self.createBlock()
            while (newBlk.hash >= self.target):
                print(pid, ": finding nonce..")
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
        pid = os.getpid()
        node: BitCoinNode
        for node in self.nodesList:
            if node.id != self.id:
                node.blkQueue.put(newBlk)
        # once we are sure about the newly mined block, add it into our own blockchain, as we broadcast it to other nodes
        (result, status) = self.blockchain.insert(newBlk, self.pubKeys[0])
        print("assert")
        assert result == True

    def startRunning(self) -> None:
        pid = os.getpid()
        while(True):
            # wait for some time
            # time.sleep(random.randint(1, 3))
            # broadcast transaction(s)
            #print(pid, ": broadbast begin")
            self.broadcastTxns()
            #print(pid, ": broadbast end")
            # process received transactions from queue
            #print(pid, ": processTxns begin")
            self.processTxns()
            #print(pid, ": processTxns end")
            # process received blocks from queue
            #print(pid, ": processBlks begin")
            self.processBlks()
            #print(pid, ": processBlks end")
            if self.blockchain.mempool:
                print("mempool")
                # start mining for a block
                newBlk = self.proofOfWork()
                # broadbast block to all other nodes
                self.broadcastBlock(newBlk)
