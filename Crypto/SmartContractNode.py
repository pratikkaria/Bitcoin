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
from BitCoinNode import BitCoinNode
from SmartContractMessages import VoterMessage, InitiatorMessage
import constants


class SmartContractNode:
    def __init__(self, type: str, nNodes:int, votingOptions: List[str] = [])->None:
        self.keys: List[Tuple] = []
        (pubKey, privateKey) = utils.generateKeys(1024)
        pubKeyStr: str = pubKey.exportKey().decode()
        privateKeyStr: str = privateKey.exportKey().decode()
        self.privateKey = privateKeyStr
        self.publicKey = pubKeyStr
        self.nNodes = nNodes
        self.nodeObject: BitCoinNode = BitCoinNode(pubKeyStr, privateKeyStr, self.nNodes)
        self.messages: Queue = Queue()
        self.nodeList: List[SmartContractNode] = []
        if type=="voter":
            self.vote: str = ""
            self.hasVoted: bool = False
            self.candidates: List[str] = []
            self.initiator: List[SmartContractNode] = []
        elif type=="initiator":
            self.votes: List[str] = []
            self.currVoteCount: int = 0
            self.peopleVoted: List[str] = []
            self.candidates: List[str] = votingOptions

        self.type: str = type
        # self.nodeId: int = nodeId

    def haveAllVotesCome(self)->bool:
        if self.currVoteCount==(self.nNodes-1):
            print("Voting Complete")
            maxVotes: int = 0
            winner: str = max(set(self.votes), key = self.votes.count)
            for i in self.votes:
                if i==winner:
                    maxVotes+=1

            print("Winner of Voting is : " + str(winner) + " with a votecount of : "+str(maxVotes))
            return True
        else:
            return False


    def castVote(self):
        numberOfCandidates: int = len(self.candidates)
        toVote = random.randint(0,numberOfCandidates-1)
        myVote: str = self.candidates[toVote]
        self.hasVoted = True
        self.vote = myVote
        print("My Vote: ",self.vote)


    def getDetailsForTxn(self):
        keys = self.nodeObject.blockchain.unspntTxOut.keys()
        # prevTxnHash = list(self.nodeObject.blockchain.blockPrevTxnHashes.keys())[0]
        prevTxnHash: str = list(self.nodeObject.blockchain.currentPrevTxnHashes.keys())[0]
        prevIndex: int = self.nodeObject.blockchain.currentPrevTxnHashes[prevTxnHash][0]
        prevScriptSig: str = self.nodeObject.blockchain.unspntTxOut[prevTxnHash][prevIndex].scriptPubKey
        return (prevTxnHash, prevIndex, prevScriptSig)


    def generateTransaction(self,sendList: List[Tuple[str, int, str, str, str]], recvList: List[Tuple[str, int]]) -> Transaction:
        pid = os.getpid()
        prevAmount = 0
        for (prevTxnHash, prevIndex, prevPubKeyScript, myPublicKey, myPrivateKey) in sendList:
            if prevTxnHash in self.nodeObject.blockchain.mempool:
                prevAmount = self.blockchain.mempool[prevTxnHash].txnOutputs[prevIndex].amount
            elif prevTxnHash in self.nodeObject.blockchain.unspntTxOut:
                if prevIndex in self.nodeObject.blockchain.unspntTxOut[prevTxnHash]:
                    prevAmount = self.nodeObject.blockchain.unspntTxOut[prevTxnHash][prevIndex].amount
        print(pid, ": prevAmount = ", prevAmount)
        selfAmount = 0
        txnOutputs: List[TransactionOutput] = []
        for (recvPubKey, amount) in recvList:
            txnOut = TransactionOutput(amount)
            txnOut.createScriptPubKey(recvPubKey)
            txnOutputs.append(txnOut)
            if prevAmount - amount > 0:
                selfAmount = prevAmount - amount
        if selfAmount > 0:
            txnOut = TransactionOutput(selfAmount)
            txnOut.createScriptPubKey(self.publicKey)
            txnOutputs.append(txnOut)

        txnInputs: List[TransactionInput] = []
        for (prevTxnHash, prevIndex, prevPubKeyScript, myPublicKey, myPrivateKey) in sendList:
            txnIn = TransactionInput(prevTxnHash, prevIndex)
            txnIn.createScriptSig(prevPubKeyScript, myPublicKey, myPrivateKey, txnOutputs)
            txnInputs.append(txnIn)
        newTxn = Transaction(txnInputs, txnOutputs, constants.lockTime)
        newTxn.calculateHash()
        return newTxn

    def startContract(self) -> None:
        if self.type=="voter":
            pid = os.getpid()
            while(True):
                if self.messages.empty():
                    continue
                break
            message: List[str] = self.messages.get_nowait()
            self.candidates = message[:-1]
            self.castVote()
            initiatorPublicKey = message[-1]
            (prevTxnHash, prevIndex, prevScriptSig) = self.getDetailsForTxn()
            newTxn: Transaction = self.generateTransaction([(prevTxnHash, prevIndex, prevScriptSig,self.publicKey, self.privateKey)],[(initiatorPublicKey,constants.contractFees)])
            blockNodeList: List[BitCoinNode] = []
            for node in self.nodeList:
                blockNodeList.append(node.nodeObject)
            # self.nodeObject.broadcastAndRunTillSettled(newTxn, blockNodeList)

            # print("Balance is " + str(self.nodeObject.blockchain.currentBalance))
            # print("All node Balance")
            # for i in blockNodeList:
            #     print(i.blockchain.currentBalance)
            self.initiator[0].messages.put(self.vote)
            print("Done")
            return;
        elif self.type=="initiator":
            pid = os.getpid()
            print("Initiator : " + str(pid))
            completedSending = 0
            print("Initiator Node List: " + str(len(self.nodeList)))
            while(True):
                if completedSending==0:
                    msg: List[str] = self.candidates
                    msg.append(self.publicKey)
                    for voter in self.nodeList:
                        voter.messages.put(msg)
                    completedSending = 1
                else:
                    if self.messages.qsize()==(self.nNodes-1):
                            while not self.messages.empty():
                                self.votes.append(self.messages.get_nowait())
                            maxVotes: int = 0
                            print(self.votes)
                            winner: str = max(set(self.votes), key = self.votes.count)
                            for i in self.votes:
                                if i==winner:
                                    maxVotes+=1

                            print("Winner of Voting is : " + str(winner) + " with a votecount of : "+str(maxVotes))
                            break;
