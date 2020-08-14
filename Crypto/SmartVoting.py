from multiprocessing import Process
from BitCoinNode import BitCoinNode
from Transaction import Transaction, TransactionOutput, TransactionInput
import utils, binascii, constants
from typing import List, Tuple, Dict
from SmartContractNode import SmartContractNode


def createCoinBase(recvList: List[Tuple[str, int]])->Transaction:
    txnOutputs: List[TransactionOutput] = []
    for (recvPubKey, amount) in recvList:
        txnOut = TransactionOutput(amount)
        txnOut.createScriptPubKey(recvPubKey)
        txnOutputs.append(txnOut)
    txnInput = TransactionInput(str(binascii.hexlify(bytearray(32))), int("ffffffff", 16))
    newTxn = Transaction([txnInput], txnOutputs, constants.lockTime)
    return newTxn


nNodes = 4
voters: List[SmartContractNode] = []
nodeDict = {}
for i in range(0,nNodes-1):
    newNode = SmartContractNode("voter",nNodes)
    voters.append(newNode)

initiator: SmartContractNode = SmartContractNode("initiator", nNodes, constants.candidates)
voters.append(initiator)
initiator.nodeList = voters[:-1]

for i in range(0, nNodes-1):
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

# voters: List[Voter] = []
# for i in range(0,nNodes-1):
#     voters.append(Voter(nNodes))
#
# initiator: Initiator = Initiator(constants.candidates, 10, voters)
# coinBaseTxns: List[Transaction] = []
# for node in voters:
#     coinBaseTxn = createCoinBase([(node.publicKey, constants.coinbase)])
#     coinBaseTxns.append(coinBaseTxn)
#
# coinBaseTxns.append(createCoinBase([(initiator.publicKey, constants.coinbase)]))
# for node in voters:
#     node.nodeObject.addGenesisBlock(coinBaseTxns)
#
# initiator.nodeObject.addGenesisBlock(coinBaseTxns)
#
#
# procList = []
# proc = Process(target = initiator.startRunning)
# procList.append(proc)
# proc.start()
# for nodes in voters:
#     proc = Process(target=nodes.startRunning)
#     procList.append(proc)
#     proc.start()
#
# for proc in procList:
#     proc.join()
