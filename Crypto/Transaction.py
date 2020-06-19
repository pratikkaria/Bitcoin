from utils import getObjHash, encodeVariant, readVariant
from typing import Tuple, List
from script import Script

class Transaction:
    def __init__(self, version, txnInputs, txnOutputs, lockTime, testNet = False):
        self.version = version
        self.txnInputs = txnInputs
        self.txnOutputs = txnOutputs
        self.lockTime = lockTime
        self.testNet = testNet

    def __repr__(self):
        tx_ins = ''
        for tx_in in self.txnInputs:
            tx_ins += tx_in.__repr__() + '\n'
        tx_outs = ''
        for tx_out in self.txnOutputs:
            tx_outs += tx_out.__repr__() + '\n'
        return 'tx: {}\nversion: {}\ntx_ins:\n{}tx_outs:\n{}locktime: {}'.format(self.id(),self.version,tx_ins,tx_outs,self.lockTime)

    def id(self):
        return self.hash()

    def hash(self):
        '''Binary hash of the legacy serialization'''
        return hash256(self.serialize())[::-1]

    @classmethod
    def parse(cls, stream):
        version = little_endian_to_int(stream.read(4))
        num_inputs = readVarint(s)
        inputs = []
        for _ in range(num_inputs):
            inputs.append(TransactionInput.parse(s))

        num_outputs = readVarint(s)
        outputs = []
        for _ in range(num_outputs):
            outputs.append(TransactionOutput.parse(s))
        locktime = little_endian_to_int(s.read(4))
        return cls(version, inputs, outputs, locktime, testnet=testnet)

    def serialize(self):
        result = int_to_little_endian(self.version, 4)
        result += encode_varint(len(self.txnInputs))
        for tx_in in self.txnInputs:
            result += tx_in.serialize()
        result += encode_varint(len(self.txnOutputs))
        for tx_out in self.txnOutputs:
            result += tx_out.serialize()
        result += int_to_little_endian(self.locktime, 4)
        return result


class TransactionInput:
    def __init__(self,prevTxn, prevIndex, scriptSig=None, seq=0xffffffff):
        self.prevTxn = prevTxn
        self.prevIndex = prevIndex
        if scriptSig is None:
            self.scriptSig = Script()
        else:
            self.scriptSig = scriptSig

        self.seq = seq

    def __repr__(self):
        return '{}:{}'.format(self.prevTxn.hex(),self.prevIndex)

    @classmethod
    def parse(cls, s):
        prevTxn = s.read(32)[::-1]
        prevIndex = little_endian_to_int(s.read(4))
        scriptSig = Script.parse(s)
        seq = little_endian_to_int(s.read(4))
        return cls(prevTxn, prevIndex, scriptSig, seq)

    def serialize(self):
        '''Returns the byte serialization of the transaction input'''
        result = self.prevTxn[::-1]
        result += int_to_little_endian(self.prevIndex, 4)
        result += self.scriptSig.serialize()
        result += int_to_little_endian(self.seq, 4)
        return result



class TransactionOutput:
    def __init__(self, amount, scriptPubKey):
        self.amount = amount
        self.scriptPubKey = scriptPubKey

    def __repr__(self):
        return '{}:{}'.format(self.amount, self.script_pubkey)


    @classmethod
    def parse(cls, s):
        amount = little_endian_to_int(s.read(8))
        scriptPubKey = Script.parse(s)
        return cls(amount, scriptPubKey)


    def serialize(self):
        '''Returns the byte serialization of the transaction output'''
        result = int_to_little_endian(self.amount, 8)
        result += self.scriptPubKey.serialize()
        return result
