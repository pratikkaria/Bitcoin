from multiprocessing import Process
from BitCoinNode import BitCoinNode
from Transaction import Transaction, TransactionOutput, TransactionInput
import utils, binascii, constants
from typing import List, Tuple, Dict
from SmartContractNode import SmartContractNode
import random
import time
start_time = time.time()

def createCoinBase(recvList: List[Tuple[str, int]])->Transaction:
    txnOutputs: List[TransactionOutput] = []
    for (recvPubKey, amount) in recvList:
        txnOut = TransactionOutput(amount)
        txnOut.createScriptPubKey(recvPubKey)
        txnOutputs.append(txnOut)
    txnInput = TransactionInput(str(binascii.hexlify(bytearray(32))), int("ffffffff", 16))
    newTxn = Transaction([txnInput], txnOutputs, constants.lockTime)
    return newTxn

nNodes = constants.nNodes
voters: List[SmartContractNode] = []
nodes: List[SmartContractNode] = []
nodeDict = {}
nodeVal: List[int] = []
for i in range(0,nNodes-1):
    newNode = SmartContractNode("voter",constants.smartContractNodes)
    nodes.append(newNode)

for i in range(0, nNodes - 1):
    if i not in constants.compulsorySmartContract:
        nodeVal.append(i)

voterVal: List[int] = random.sample(nodeVal, constants.smartContractNodes - len(constants.compulsorySmartContract) - 1)
for i in voterVal:
    print(i)
    voters.append(nodes[i])

for i in constants.compulsorySmartContract:
    print(i)
    voters.append(nodes[i])

initiator: SmartContractNode = SmartContractNode("initiator", constants.smartContractNodes, constants.candidates)
initiator.nodeList = voters
voters.append(initiator)

for i in range(0,len(voters)):
    voters[i].nodeList = voters
    voters[i].initiator.append(initiator)

coinBaseTxns: List[Transaction] = []
for node in voters:
    coinBaseTxn = createCoinBase([(node.publicKey, constants.genesisTxnAmount)])
    coinBaseTxns.append(coinBaseTxn)

coinBaseTxns.append(createCoinBase([(initiator.publicKey, constants.genesisTxnAmount)]))

for node in voters:
    node.nodeObject.addGenesisBlock(coinBaseTxns)
initiator.nodeObject.addGenesisBlock(coinBaseTxns)

procList = []
proc = Process(target = initiator.startContract)
procList.append(proc)
proc.start()
for nodes in voters[:-1]:
    proc = Process(target = nodes.startContract)
    procList.append(proc)
    proc.start()

for proc in procList:
    proc.join()

print("--- %s seconds ---" % (time.time() - start_time))
