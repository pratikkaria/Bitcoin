from BlockChain import BlockChain
from typing import Dict, List, Tuple
from Transaction import Transaction, TransactionInput, TransactionOutput
from multiprocessing import Queue
import time, random
from Block import Block, BlockHeader
import ScriptEngine as ScrEng
from ScriptEngine import comparePubKeyAndScript
from MerkleTree import MerkleTree
import binascii
from constants import BlockStatus, coinbase, Threshold, lockTime
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
        #print("blockchain: ", self.blockchain)
        self.txQueue: Queue = txQueue
        self.blkQueue: Queue = blkQueue
        self.blkThreshold: Threshold = Threshold.BLK_THRESHOLD
        self.txnThreshold: Threshold = Threshold.TXN_THRESHOLD
        self.generatedTxns: List[Transaction] = []
        self.nodesList: List[BitCoinNode] = []
        self.nodesKeys: List[List[str]] = []
        BitCoinNode.id += 1
        self.id: int = BitCoinNode.id
        #self.target: str = "0000000000000000007e9e4c586439b0cdbe13b1370bdd9435d76a644d047523"
        self.target: str = "0987892757f34247427e9e4c586439b0cdbe13b1370bdd9435d76a644d047523"
        self.pubKeys: List[str] = []
        if pubKey:
            self.pubKeys.append(pubKey)
        self.privateKeys: List[str] = []
        if privateKey:
            self.privateKeys.append(privateKey)
        #self.createGenesisBlock(nNodes)

    def setNodesKeys(self, nodesKeys: List[List[str]]):
        self.nodesKeys = nodesKeys

    # annotation removed due to static typing error for self referencing BitCoinNode
    def setNodesList(self, nodesList) -> None:
        self.nodesList = nodesList

    def setGeneratedTxns(self, txns: List[Transaction]) -> None:
        self.generatedTxns = txns

    def processBlk(self, blkCnt: int, emptyExcptn: bool) -> None:
        pid = os.getpid()
        try:
            newBlk: Block = self.blkQueue.get_nowait()
            # before inserting, block verification is done inside the BlockChain.insert() method
            (result, status) = self.blockchain.insert(newBlk, self.pubKeys[0])
            print(pid, ": block arrived..")
            if result:
                blkCnt += 1
                print(pid, ": block processed successfully..")
            elif not result and status == BlockStatus.MISSING_TXN:
                # Not reliable to get the size of queue
                currentQueueSize = self.txQueue.qsize()
                self.processTxns(currentQueueSize)
                # Last try - if still we get MISSING_TXN, we have to reject this block
                (result, status) = self.blockchain.insert(newBlk, self.pubKeys[0])
                if result:
                    print(pid, ": block processed successfully..")
                    blkCnt += 1
        except:
            # empty blkQueue - ignore
            #print(pid, ": blockqueue empty")
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
                print(pid, ": transaction arrived..")
                # Verify this transaction
                verified = True
                for newTxIn in newTx.txnInputs:
                    if not ((newTxIn.prevTxn in self.blockchain.mempool) or (newTxIn.prevTxn in self.blockchain.unspntTxOut)):
                        verified = False
                        break
                    #print(pid, ": partially verified")
                    if not ScrEng.verifyScriptSig(newTxIn.scriptSig, newTxIn.dataToSign):
                        verified = False
                        break
                if verified:
                    #self.unspntTxOut[newTxHash] = newTx
                    print(pid, ": transaction verified")
                    self.mempool[newTxHash] = newTx
                    txnCnt += 1
                    for index, newTxOut in enumerate(newTx.txnOutputs):
                        if comparePubKeyAndScript(self.publicKeys[0], newTxOut.scriptPubKey):
                            if newTx.getHash() in self.blockchain.currentPrevTxnHashes:
                                self.blockchain.currentPrevTxnHashes[newTx.getHash()].append(index)
                            else:
                                self.blockchain.currentPrevTxnHashes[newTx.getHash()] = []
                                self.blockchain.currentPrevTxnHashes[newTx.getHash()].append(index)
            except:
                # empty txQueue - ignore
                emptyExcptn = True
                pass
        # give an opportunity to broadcast generated transactions
        self.broadcastTxns()

    def getSendList(self) -> Tuple[bool, str, int, str, int]:
        pid = os.getpid()
        pvTxnHash: str = ""
        pvIndex: int = -1
        pvPubKeyScript: str = ""
        pvAmount: int = 0
        repeatHash = True
        repeatHashCnt = 0
        while(repeatHash == True and repeatHashCnt < len(list(self.blockchain.currentPrevTxnHashes.keys()))):
            repeatHash = False
            repeatHashCnt += 1
            tmpList: List[str] = list(self.blockchain.currentPrevTxnHashes.keys())
            if len(tmpList) == 0:
                print(pid, ": tmpList len 0")
                return (False, pvTxnHash, pvIndex, pvPubKeyScript, pvAmount)
            i: int = random.randint(0, len(tmpList)-1)
            prevTxnHash = tmpList[i]
            pvTxnHash = prevTxnHash #identical
            #print("len: ",len(self.blockchain.currentPrevTxnHashes[prevTxnHash]))
            if len(self.blockchain.currentPrevTxnHashes[prevTxnHash]) == 0:
                print(pid, ": currentPrevTxnHashes len 0")
                return (False, pvTxnHash, pvIndex, pvPubKeyScript, pvAmount)
            repeatIndex = True
            repeatIndexCnt = 0
            if prevTxnHash not in self.blockchain.currentPrevTxnHashes:
                continue
            while(repeatIndex == True and prevTxnHash in self.blockchain.currentPrevTxnHashes and repeatIndexCnt < len(self.blockchain.currentPrevTxnHashes[prevTxnHash])):
                repeatIndex = False
                repeatIndexCnt += 1
                randomIndex: int = random.randint(0, len(self.blockchain.currentPrevTxnHashes[prevTxnHash])-1)
                prevIndex = self.blockchain.currentPrevTxnHashes[prevTxnHash][randomIndex]
                pvIndex = prevIndex
                # removal of prevIndex and possibly the prevTxnHash
                self.blockchain.currentPrevTxnHashes[prevTxnHash].remove(prevIndex)
                if len(self.blockchain.currentPrevTxnHashes[prevTxnHash]) == 0:
                    print(pid, ": removed")
                    self.blockchain.currentPrevTxnHashes.pop(prevTxnHash)

                if prevTxnHash in self.blockchain.mempool:
                    prevPubKeyScript = self.blockchain.mempool[prevTxnHash].txnOutputs[prevIndex].scriptPubKey
                    pvPubKeyScript = prevPubKeyScript
                    prevAmount = self.blockchain.mempool[prevTxnHash].txnOutputs[prevIndex].amount
                    pvAmount = prevAmount
                elif prevTxnHash in self.blockchain.unspntTxOut:
                    if prevIndex in self.blockchain.unspntTxOut[prevTxnHash]:
                        prevPubKeyScript = self.blockchain.unspntTxOut[prevTxnHash][prevIndex].scriptPubKey
                        pvPubKeyScript = prevPubKeyScript
                        prevAmount = self.blockchain.unspntTxOut[prevTxnHash][prevIndex].amount
                        pvAmount = prevAmount
                    else:
                        repeatIndex = True
                else:
                    print(pid, ": invalid")
                    # invalid; should not come here
                    return (False, pvTxnHash, pvIndex, pvPubKeyScript, pvAmount)
            if repeatIndex == True:
                repeatHash = True
        if repeatHash == True:
            # can't generate a new transaction - insufficient previous transaction outputs
            return (False, pvTxnHash, pvIndex, pvPubKeyScript, pvAmount)
        return (True, pvTxnHash, pvIndex, pvPubKeyScript, pvAmount)

    def generateTransaction(self) -> None:
        pid = os.getpid()

        sendList = []
        (status, prevTxnHash, prevIndex, prevPubKeyScript, prevAmount) = self.getSendList()
        if status == False:
            # can't generated new transaction at the moment
            return
        #print(pid, ": prevTxnHash: ", prevTxnHash, "prevIndex: ", prevIndex, "prevPubKeyScript: ", prevPubKeyScript, "prevAmount: ", prevAmount)
        sendList.append((prevTxnHash, prevIndex, prevPubKeyScript))
        # can be full amount also
        if prevAmount == 0:
            return
        recvAmount = random.randint(1, prevAmount)
        print(pid, ": recvAmount = ", recvAmount)
        # can send to self also
        recvPubKey = self.nodesKeys[random.randint(0, len(self.nodesKeys)-1)][0]
        recvList = []
        recvList.append((recvPubKey, recvAmount))

        txnOutputs: List[TransactionOutput] = []
        amountSpent = 0
        for (recvPubKey, recvAmount) in recvList:
            amountSpent += recvAmount
            txnOut = TransactionOutput(recvAmount)
            txnOut.createScriptPubKey(recvPubKey)
            txnOutputs.append(txnOut)
        if prevAmount - amountSpent > 0:
            txnOut = TransactionOutput(prevAmount - amountSpent)
            txnOut.createScriptPubKey(self.pubKeys[0])
            txnOutputs.append(txnOut)
        txnInputs: List[TransactionInput] = []
        for (prevTxnHash, prevIndex, prevPubKeyScript) in sendList:
            txnIn = TransactionInput(prevTxnHash, prevIndex)
            txnIn.createScriptSig(prevPubKeyScript, self.pubKeys[0], self.privateKeys[0], txnOutputs)
            txnInputs.append(txnIn)
        newTxn = Transaction(txnInputs, txnOutputs, lockTime)
        newTxn.calculateHash()
        # addition to currentPrevTxnHashes
        if prevAmount - amountSpent > 0:
            print(pid, ": added")
            self.blockchain.currentPrevTxnHashes[newTxn.getHash()] = [len(txnOutputs)-1]
        self.generatedTxns.append(newTxn)
        self.blockchain.mempool[newTxn.getHash()] = newTxn
        print(pid, ": generateTransaction success => ", newTxn.getHash())

    def broadcastTxns(self) -> None:
        pid = os.getpid()
        self.generateTransaction()
        txn: Transaction
        skip: bool = False
        for txn in self.generatedTxns:
            print(pid, ": trying to broadcast transaction..")
            # Check if the current transaction's inputs have the corresponding outputs available
            skip = False
            for txIn in txn.txnInputs:
                if not (txIn.prevTxn in self.blockchain.unspntTxOut or txIn.prevTxn in self.blockchain.mempool):
                    skip = True
                    break;
            if skip == False:
                # now broadcast this transaction to all the other BitCoinNodes
                print(pid, ": broadcasting transaction..")
                node: BitCoinNode
                for node in self.nodesList:
                    if node.id != self.id:
                        node.txQueue.put(txn)
            self.generatedTxns.remove(txn)
            pass
        pass

    def createCoinBaseTxn(self, amount: int = coinbase) -> Transaction:
        pid = os.getpid()
        txnOutput = TransactionOutput(amount)
        txnOutput.createScriptPubKey(self.pubKeys[0])
        txnInput = TransactionInput(str(binascii.hexlify(bytearray(32))), int("ffffffff", 16))
        print(pid, ": txnInput for coinBaseTxn = ", txnInput)
        txn = Transaction([txnInput], [txnOutput], 15)
        return txn

    def createBlock(self) -> Block:
        # TODO: Transaction Fees
        # Check - whether it should be copied, moved or destroyed
        txnList = list(self.blockchain.mempool.values())
        #self.blockchain.mempool.clear()
        coinBaseTxn = self.createCoinBaseTxn()
        txnList.insert(0, coinBaseTxn)
        newMerkleTree = MerkleTree()
        newMerkleTree.createMerkleTree(txnList)
        nonce = random.randint(0, 2147483647)
        blkHeader = BlockHeader(self.blockchain.longest, str(nonce), newMerkleTree.mrkl_root, len(txnList))
        newBlk: Block = Block(txnList, blkHeader, newMerkleTree.fullTree)
        return newBlk

    def addGenesisBlock(self, txnList: List[Transaction]) -> None:
        pid = os.getpid()
        for txn in txnList:
            print(pid, ": coinBaseTxn Hash = ", txn.getHash())
        newMerkleTree = MerkleTree()
        newMerkleTree.createMerkleTree(txnList)
        nonce = random.randint(0, 2147483647)
        #print("nonce: ", nonce)
        #print("longest: ", self.blockchain.longest)
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
        while restart == True:
            restart = False
            print(pid, ": proof of work..")
            newBlk = self.createBlock()
            while (newBlk.hash >= self.target):
                print(pid, ": finding nonce..")
                nonce = random.randint(0, 2147483647)
                newBlk.blockHeader.nonce = str(nonce)
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
        print(pid, ": block broadcast done")
        # once we are sure about the newly mined block, add it into our own blockchain, as we broadcast it to other nodes
        (result, status) = self.blockchain.insert(newBlk, self.pubKeys[0])
        print(pid, ": block insert status = ", status)
        assert result == True

    def startRunning(self) -> None:
        pid = os.getpid()
        while(True):
        #for i in range(0, 100):
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
                print("mempool nonempty?")
                # start mining for a block
                newBlk = self.proofOfWork()
                # broadbast block to all other nodes
                self.broadcastBlock(newBlk)
