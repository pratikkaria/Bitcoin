import ScriptEngine
from Crypto.PublicKey import RSA
import utils
from typing import List

class TransactionInput:
    def __init__(self,prevTxn, prevIndex):
        self.prevTxn = prevTxn
        self.prevIndex = prevIndex
        self.scriptSig = ""

    def __repr__(self):
        return '{}:{}'.format(self.prevTxn.hex(),self.prevIndex)


    def createDataToSign(self, prevPubKeyScript: str, myPublicKey: str, txnOutputs: List[TransactionOutput]):
        inp = self #First Create TxnInp and txnOutputs
        dataToSign = ""
        dataToSign += inp.prevTxn
        dataToSign += str(inp.prevIndex)
        for i in txnOutputs:
            dataToSign += str(i.amount)
            dataToSign += i.scriptPubKey

        return dataToSign


    def createSignature(self, dataToSign: str, privateKey):
        return utils.sign(privateKey, dataToSign)


    def createScriptSig(self, prevPubKeyScript: str, myPublicKey: str, myPrivateKey: str, txnOutputs: List[TransactionOutput]):
        dataToSign = self.createDataToSign(prevPubKeyScript, myPublicKey, txnOutputs)
        signature = self.createSignature(dataToSign, RSA.importKey(myPrivateKey))
        self.scriptSig = ScriptEngine.createScriptSig(prevPubKeyScript, myPublicKey, signature)


class TransactionOutput:
    def __init__(self, amount: int):
        self.amount = amount
        self.scriptPubKey = ""

    def __repr__(self):
        return '{}:{}'.format(self.amount, self.script_pubkey)

    def createScriptPubKey(self, publicKeyOfReceiver:str):
        self.scriptPubKey = ScriptEngine.createPubKeyScript(utils.getHashValue(publicKeyOfReceiver,""))


class Transaction:
    def __init__(self, txnInputs: List[TransactionInput], txnOutputs: List[TransactionOutput], lockTime: int):
        self.txnInputs = txnInputs
        self.txnOutputs = txnOutputs
        self.lockTime = lockTime
        self.hash = ""

    def getRawDataToHash(self):
        dataToHash = ""
        dataToHash+= str(self.txnInputs.size())
        for i in self.txnInputs:
            dataToHash+= i.prevTxn
            dataToHash+= str(i.prevIndex)
            dataToHash+= i.scriptSig

        dataToHash+= str(self.txnOutputs.size())
        for i in self.txnOutputs:
            dataToHash+= str(i.amount)
            dataToHash+= str(i.scriptPubKey)

        dataToHash+= str(self.lockTime)

        return dataToHash


    def calculateHash(self):
        rawData = self.getRawDataToHash()
        self.hash = utils.getHashValue(rawData,"")

    def getHash(self):
        if self.hash == "":
            self.calculateHash()
        return self.hash
