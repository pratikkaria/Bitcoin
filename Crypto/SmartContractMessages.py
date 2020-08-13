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

class VoterMessage:
    def __init__(self, candidates: List[str], pubKeyInititor: str) -> None:
        self.candidates: List[str] = candidates
        self.InitiatorPublicKey: str = pubKeyInititor

class InitiatorMessage:
    def __init__(self, candidateVoted: str) -> None:
        self.vote = candidateVoted
