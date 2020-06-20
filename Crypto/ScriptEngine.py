from collections import deque
import utils
from Crypto.PublicKey import RSA
from constants import opcodeList
from typing import List

def createPubKeyScript(pubKeyHash: str) -> str:
    return "OP_DUP\tOP_HASH160\t"+pubKeyHash+"\tOP_EQUALVERIFY\tOP_CHECKSIG"

def createScriptSig(pubKeyScript: str, publicKey: str, signature: str) -> str:
    return signature+"\t"+publicKey+"\t"+pubKeyScript

def verifyScriptSig(scriptSig: str, msg: str) -> bool:
    stack: deque = deque()
    params: List[str] = scriptSig.split("\t")
    stack.append(params[0])
    for i in range(1,len(params)):
        if params[i] not in opcodeList:
            stack.append(params[i])
        else:
            if params[i]=="OP_DUP":
                popped:str = stack.pop()
                stack.append(popped)
                stack.append(popped)
            elif params[i]=="OP_HASH160":
                popped:str = stack.pop()
                reqHash:str = utils.getHashValue(popped, "")
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
'''
