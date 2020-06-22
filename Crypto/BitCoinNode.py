from BlockChain import BlockChain
from typing import Dict, List
from Transaction import Transaction, TransactionInput, TransactionOutput
from multiprocessing import Queue
import time, random
from Block import Block, BlockHeader
import ScriptEngine as ScrEng
from MerkleTree import MerkleTree
import binascii
import utils, constants

class BitCoinNode:
    id: int = 0
    def __init__(self, blockchain: BlockChain = BlockChain(), unspntTxOut: Dict[str, Transaction] = {}, txQueue: Queue = Queue(), blkQueue: Queue = Queue()) -> None:
        self.blockchain: BlockChain = blockchain
        self.unspntTxOut: Dict[str, Transaction] = unspntTxOut
        self.txQueue: Queue = txQueue
        self.blkQueue: Queue = blkQueue
        self.blkThreshold: int = 5
        self.txnThreshold: int = 5
        self.generatedTxns: List[Transaction] = []
        self.nodesList: List[BitCoinNode] = []
        BitCoinNode.id += 1
        self.id: int = BitCoinNode.id
        self.target: str = "0000000000000000007e9e4c586439b0cdbe13b1370bdd9435d76a644d047523"
        self.pubKey: str = ""
        self.privateKey: str = ""

    def processBlks(self) -> None:
        blkCnt = 0
        emptyExcptn = False
        while (emptyExcptn == False and blkCnt < self.blkThreshold):
            try:
                newBlk: Block = self.blkQueue.get_nowait()
                # TODO: check and remove those transactions from UTXO which are present in this block
                # TODO: verify this block
                self.blockchain.insert(newBlk)
                blkCnt += 1
            except:
                # empty blkQueue - ignore
                emptyExcptn = True
                pass

    def processTxns(self) -> None:
        txnCnt = 0
        emptyExcptn = False
        while (emptyExcptn == False and txnCnt < self.txnThreshold):
            try:
                newTx: Transaction = self.txQueue.get_nowait()
                newTxHash = newTx.getHash()
                # verify this transaction
                verified = True
                for newTxIn in newTx.txnInputs:
                    if not (newTxIn.prevTxn in self.unspntTxOut):
                        verified = False
                    if not ScrEng.verifyScriptSig(newTxIn.scriptSig, newTxIn.dataToSign, newTx.txnOutputs):
                        verified = False
                        break
                if verified:
                    self.unspntTxOut[newTxHash] = newTx
                txnCnt += 1
            except:
                # empty txQueue - ignore
                emptyExcptn = True
                pass

    def broadcastTxn(self) -> None:
        txn: Transaction = self.generatedTxns.pop()
        for node in self.nodesList:
            if node.id != self.id:
                node.txQueue.put(txn)
        pass

    def createCoinBaseTxn(self) -> Transaction:
        txnInput = TransactionInput(binascii.hexlify(bytearray(32)), "ffffffff")
        txnOutput = TransactionOutput(constants.coinbase)
        txnOutput.createScriptPubKey(self.pubKey)
        txn = Transaction([txnInput], [txnOutput], 15)
        return txn

    def createBlock(self) -> Block:
        txnList = list(self.unspntTxOut.values())
        self.unspntTxOut.clear()
        coinBaseTxn = self.createCoinBaseTxn()
        txnList.insert(0, coinBaseTxn)
        newMerkleTree = MerkleTree()
        newMerkleTree.createMerkleTree(txnList)
        nonce = random.randint(0, 2147483647)
        blkHeader = BlockHeader(self.blockchain.longest, nonce, newMerkleTree.mrkl_root, len(txnList))
        newBlk: Block = Block(txnList, blkHeader, newMerkleTree.fullTree)
        return newBlk

    def proofOfWork(self) -> Block:
        newBlk: Block = self.createBlock()
        while (newBlk.hash >= self.target):
            nonce = random.randint(0, 2147483647)
            newBlk.blockHeader.nonce = nonce
            newBlk.reCalculateHash()
        return newBlk

    def broadcastBlock(self, newBlk: Block) -> None:
        for node in self.nodesList:
            if node.id != self.id:
                node.blkQueue.put(newBlk)

    def startRunning(self) -> None:
        while(True):
            # wait for some time
            time.sleep(random.randint(1, 3))
            # process received blocks from queue
            self.processBlks()
            # process received transactions from queue
            self.processTxns()
            # broadcast a transaction at a time
            self.broadcastTxn()
            # start mining for a block
            newBlk = self.proofOfWork()
            # broadbast block to all other nodes
            self.broadcastBlock(newBlk)
