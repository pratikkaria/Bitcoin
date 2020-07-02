from collections import deque
import utils
from Crypto.PublicKey import RSA
from constants import opcodeList
from typing import List
from constants import hashSize

def createPubKeyScript(pubKeyHash: str) -> str:
    return "OP_DUP\tOP_HASH160\t"+pubKeyHash+"\tOP_EQUALVERIFY\tOP_CHECKSIG"

def createScriptSig(pubKeyScript: str, publicKey: str, signature: str) -> str:
    return signature+"\t"+publicKey+"\t"+pubKeyScript

def verifyScriptSig(scriptSig: str, msg: str) -> bool:
    stack: deque = deque()
    params: List[str] = scriptSig.split("\t")
    stack.append(params[0])
    popped: str = ""
    for i in range(1,len(params)):
        if params[i] not in opcodeList:
            stack.append(params[i])
        else:
            if params[i]=="OP_DUP":
                popped = stack.pop()
                stack.append(popped)
                stack.append(popped)
            elif params[i]=="OP_HASH160":
                popped = stack.pop()
                reqHash:str = utils.getHashValue(popped, hashSize)
                stack.append(reqHash)
            elif params[i]=="OP_EQUALVERIFY":
                first:str = stack.pop()
                second:str = stack.pop()
                if first!=second:
                    return False
            elif params[i]=="OP_CHECKSIG":
                pubKey = RSA.importKey(stack.pop())
                signature:str = stack.pop()
                if not utils.verify(pubKey, msg, signature):
                    return False

    return True


def createPubKeyMultiSigScript(m: int, n: int, pubKey: List[str]) -> str:
    temp: str = "\t".join([i for i in pubKey])
    return str(m)+"\t"+temp+"\t"+str(n)+"\tOP_CHECKMULTISIG"


def createScriptSigMultiSig(pubKeyScript: str, signatureList: List[str]) -> str:
    temp: str = "\t".join([i for i in signatureList])
    return temp + "\t" + pubKeyScript


def verifyMultiSig(scriptSig: str, msg:str):
    listData: List[str] = scriptSig.split("\t")
    if listData[-1]!= "OP_CHECKMULTISIG":
        return False
    n = int(listData[-2])
    m = int(listData[len(listData)-3-n])
    if m>n:
        return False
    publicKeyList: List[str] = []
    signatureList: List[str] = []
    for i in range(len(listData)-3, len(listData)-3 -n,-1):
        publicKeyList.append(listData[i])
    for i in range(len(listData)-3-n-1,-1,-1):
        if listData[i]!="":
            signatureList.append(listData[i])

    print(signatureList)
    if len(signatureList)==0:
        return False
    signPtr = 0
    pubPtr = 0
    count=0
    while signPtr< len(signatureList) and pubPtr< len(publicKeyList):
        if utils.verify(RSA.importKey(publicKeyList[pubPtr]), msg, signatureList[signPtr])==True:
            count+=1
            signPtr+=1
            pubPtr+=1
        else:
            pubPtr+=1

    return count>=m


'''
Usage:

(pubKey, pvtKey) = utils.generateKeys(1024)
msg = "My Name Is Message"
publicKeyStr = pubKey.exportKey().decode()
privateKeyStr = pvtKey.exportKey().decode()
pubKeyHash = utils.getHashValue(publicKeyStr, "")
pubKeyScript = createPubKeyScript(pubKeyHash)
signature = utils.sign(pvtKey, msg)
scriptSig = createScriptSig(pubKeyScript, publicKeyStr, signature)
print(verifyScriptSig(scriptSig, msg))

Usage(multisig):
msg: str = "Hello" <- Change to transaction
(pubKey1, pvtKey1) = utils.generateKeys(1024)
(pubKey2, pvtKey2) = utils.generateKeys(1024)
(pubKey3, pvtKey3) = utils.generateKeys(1024)
sig1 = utils.sign(pvtKey1, msg)
sig2 = utils.sign(pvtKey2, msg)
sig3 = utils.sign(pvtKey3, msg)
m = 2
n = 3
pubKeyScript = createPubKeyMultiSigScript(m,n,[pubKey1.exportKey().decode(),pubKey2.exportKey().decode(),pubKey3.exportKey().decode()])
scriptSig = createScriptSigMultiSig(pubKeyScript,[sig1,sig2,sig3])
print(verifyMultiSig(scriptSig,msg))
'''
