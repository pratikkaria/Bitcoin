from multiprocessing import Process, Value, Array, Lock
from BitCoinNode import BitCoinNode
from Transaction import Transaction, TransactionOutput, TransactionInput
import utils, binascii, constants
from typing import List, Tuple, Dict

def generateTransaction(sendList: List[Tuple[str, int, str, str, str]], recvList: List[Tuple[str, int]]) -> Transaction:
    txnOutputs: List[TransactionOutput] = []
    for (recvPubKey, amount) in recvList:
        txnOut = TransactionOutput(amount)
        txnOut.createScriptPubKey(recvPubKey)
        txnOutputs.append(txnOut)
    txnInputs: List[TransactionInput] = []
    for (prevTxnHash, prevIndex, prevPubKeyScript, myPublicKey, myPrivateKey) in sendList:
        txnIn = TransactionInput(prevTxnHash, prevIndex)
        txnIn.createScriptSig(prevPubKeyScript, myPublicKey, myPrivateKey, txnOutputs)
        txnInputs.append(txnIn)
    newTxn = Transaction(txnInputs, txnOutputs, constants.lockTime)
    newTxn.calculateHash()
    return newTxn

def generateCoinBaseTransaction(recvList: List[Tuple[str, int]]) -> Transaction:
    txnOutputs: List[TransactionOutput] = []
    for (recvPubKey, amount) in recvList:
        txnOut = TransactionOutput(amount)
        txnOut.createScriptPubKey(recvPubKey)
        txnOutputs.append(txnOut)
    txnInput = TransactionInput(str(binascii.hexlify(bytearray(32))), int("ffffffff", 16))
    newTxn = Transaction([txnInput], txnOutputs, constants.lockTime)
    return newTxn

nNodes = constants.nNodes
pubKeys: List[List[str]] = []
privateKeys: List[List[str]] = []
for i in range(0, nNodes):
    (pubKey, privateKey) = utils.generateKeys(1024)
    pubKeyStr: str = pubKey.exportKey().decode()
    privateKeyStr: str = privateKey.exportKey().decode()
    pubKeys.append([pubKeyStr])
    privateKeys.append([privateKeyStr])
amount = 1000
nodesList: List[BitCoinNode] = []
'''
nodesTxns: Dict[int, List[Transaction]] = {}
'''
nTxns = Value('i', 0)
mempoolStatus = Array('i', 10)
#lock = Lock()
coinBaseTxns: List[Transaction] = []
for i in range(0, nNodes):
    node = BitCoinNode(pubKeys[i][0], privateKeys[i][0], nNodes)
    node.setTxnCnt(nTxns)
    nodesList.append(node)
    node.setNodesKeys(pubKeys)

    coinBaseTxn = generateCoinBaseTransaction([(pubKeys[i][0], amount)])
    coinBaseTxns.append(coinBaseTxn)

for i in range(0, nNodes):
    print("i: ", i)
    nodesList[i].addGenesisBlock(coinBaseTxns)
    nodesList[i].nodesList = nodesList
    #print("keys: ", nodesList[i].blockchain.currentPrevTxnHashes.keys())

'''
for i in range(0, nNodes):
    prevTxnHash = coinBaseTxns[i].getHash()
    #nodesTxns[i] = [coinBaseTxn]

    prevIndex = 0
    prevPubKeyScript = coinBaseTxns[i].getScriptPubKey(prevIndex)
    txn = generateTransaction([(prevTxnHash, prevIndex, prevPubKeyScript, pubKeys[i], privateKeys[i])], [(pubKeys[1-i], 100)])
    nodesTxns[i] = []
    nodesTxns[i].append(txn)
    nodesList[i].setGeneratedTxns(nodesTxns[i])
'''

procList = []
for i in range(0, nNodes):
    proc = Process(target=nodesList[i].startRunning)
    procList.append(proc)
    proc.start()
    print("started process: ", i)
for i, proc in enumerate(procList):
    print("joining process", i)
    proc.join()
