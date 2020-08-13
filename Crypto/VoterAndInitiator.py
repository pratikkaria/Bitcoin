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

class Voter:
    def __init__(self, nNodes:int ) -> None:
        self.keys: List[Tuple] = []
        self.candidates: List[str] = []
        self.hasVoted: bool = False
        (pubKey, privateKey) = utils.generateKeys(1024)
        pubKeyStr: str = pubKey.exportKey().decode()
        privateKeyStr: str = privateKey.exportKey().decode()
        self.privateKey = privateKeyStr
        self.publicKey = pubKeyStr
        self.nNodes = nNodes
        self.nodeObject: BitCoinNode = BitCoinNode(pubKeyStr, privateKeyStr, self.nNodes)
        self.messages: Queue = Queue()
        self.vote: str = ""
        self.type = "voter"

    def vote(self):
        numberOfCandidates: int = len(self.candidates)
        myVote: string = self.candidates[random.randint(0,len)]
        self.hasVoted = True
        self.vote = myVote

    def startRunning(self) -> None:
        pid = os.getpid()
        print("Voter : "+ str(pid))
        while(True):
            if self.messages.empty():
                continue
            break

        message: VoterMessage = self.messages.get_nowait()
        self.candidates = message.candidates
        self.vote()
        initiatorPublicKey = message.InitiatorPublicKey

class Initiator(Voter):
    def __init__(self, votingOptions: List[str], nNodes: int, nodeList: List[Voter]) -> None:
        self.candidates: List[str] = votingOptions
        self.keys: List[Tuple] = []
        self.votes: Dict[str, int] = {}
        self.messages: Queue = Queue()
        self.currVoteCount: int = 0
        self.peopleVoted: List[str] = []
        (pubKey, privateKey) = utils.generateKeys(1024)
        pubKeyStr: str = pubKey.exportKey().decode()
        privateKeyStr: str = privateKey.exportKey().decode()
        self.privateKey = privateKeyStr
        self.publicKey = pubKeyStr
        self.nNodes = nNodes
        self.nodeList: List[Voter] = nodeList
        self.nodeObject: BitCoinNode = BitCoinNode(pubKeyStr, privateKeyStr, self.nNodes)
        self.type = "initiator"

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


    def startRunning(self) -> None:
        pid = os.getpid()
        print("Initiator : " + str(pid))
        while(True):
            for voter in self.nodeList:
                msg: VoterMessage = VoterMessage(self.nodeList, self.publicKey)
                voter.messages.put(msg)

            break
