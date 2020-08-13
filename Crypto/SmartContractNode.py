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

        if type=="voter":
            self.vote: str = ""
            self.hasVoted: bool = False
            self.candidates: List[str] = []
        elif type=="initiator":
            self.votes: Dict[str, int] = {}
            self.currVoteCount: int = 0
            self.peopleVoted: List[str] = []
            self.nodeList: List[SmartContractNode] = []
            self.candidates: List[str] = votingOptions

        self.type: str = type


    def haveAllVotesCome(self)->bool:
        if self.currVoteCount==(self.nNodes-1):
            print("Voting Complete")
            maxVotes: int = 0
            winner: str = ""
            for key,value in self.votes.items():
                if value>maxVotes:
                    maxVotes= value
                    winner = key

            print("Winner of Voting is : " + str(winner) + " with a votecount of : "+str(maxVotes))
            return True
        else:
            return False


    def castVote(self):
        numberOfCandidates: int = len(self.candidates)
        toVote = random.randint(0,numberOfCandidates-1)
        myVote: string = self.candidates[toVote]
        self.hasVoted = True
        self.vote = myVote


    def getDetailsForTxn(self):
        keys = self.nodeObject.blockchain.unspntTxOut.keys()
        # prevTxnHash = list(self.nodeObject.blockchain.blockPrevTxnHashes.keys())[0]
        prevTxnHash: str = list(self.nodeObject.blockchain.currentPrevTxnHashes.keys())[0]
        prevIndex: int = self.nodeObject.blockchain.currentPrevTxnHashes[prevTxnHash]
        prevScriptSig: str = self.nodeObject.blockchain.unspntTxOut[prevTxnHash][prevIndex]
        return (prevTxnHash, prevIndex, prevScriptSig)


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
            # print(initiatorPublicKey)
            # self.getDetailsForTxn()
            print(str(pid))
            (prevTxnHash, prevIndex, prevScriptSig) = self.getDetailsForTxn()
            self.


        elif self.type=="initiator":
            pid = os.getpid()
            print("Initiator : " + str(pid))
            completedSending = 0
            while(True):
                if completedSending==0:
                    msg: List[str] = self.candidates
                    msg.append(self.publicKey)
                    for voter in self.nodeList:
                        voter.messages.put(msg)
                    completedSending = 1
                else:
                    break
