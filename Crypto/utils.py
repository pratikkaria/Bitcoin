from Crypto.Hash import SHA256,SHA224,SHA384,SHA512
from hashlib import sha1
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto import Random
from constants import hashSize
import base64

def verifyMerkleTree(mrkl_root):
    if len(mrkl_root.nodeList)==0:
        return True
    if mrkl_root.hashValue == calculateLevelHashMerkle(mrkl_root.nodeList):
        out: bool = True
        for i in mrkl_root.nodeList:
            out = out & verifyMerkleTree(i)
        return out
    return False

def calculateLevelHashMerkle(nodeList) -> str:
    hash = ""
    for i in nodeList:
        hash+=i.hashValue
    hash = getHashValue(hash, hashSize)
    return hash


def getHashValue(toHash: str, hashSize :int ) -> str:
    if hashSize == 256:
        newHash = SHA256.new()
        newHash.update(toHash.encode('utf-8'))
        return newHash.hexdigest()
    elif hashSize == 224:
        newHash = SHA224.new()
        newHash.update(toHash.encode('utf-8'))
        return newHash.hexdigest()
    elif hashSize == 384:
        newHash = SHA384.new()
        newHash.update(toHash.encode('utf-8'))
        return newHash.hexdigest()
    elif hashSize == 512:
        newHash = SHA512.new()
        newHash.update(toHash.encode('utf-8'))
        return newHash.hexdigest()
    elif hashSize == 160:
        newHash = sha1(toHash.encode('utf-8'))
        return newHash.hexdigest()
    else:
        raise TypeError("Invalid Hash Size")

def generateKeys(bits: int):
    new_key = RSA.generate(bits)
    private_key = new_key
    public_key = new_key.publickey()
    return (public_key, private_key)

def sign(privatekey, message: str) -> str:
    hashOfMessage: str = getHashValue(message, hashSize)
    hashInBytes: bytes = str.encode(hashOfMessage)
    return base64.b64encode(str((privatekey.sign(hashInBytes,''))[0]).encode()).decode()

def verify(publickey, message:str, signature: str) -> bool:
    hashOfMessage: str = getHashValue(message, hashSize)
    hashInBytes: bytes = str.encode(hashOfMessage)
    signatureInBytes: bytes = str.encode(signature)
    return publickey.verify(hashInBytes,(int(base64.b64decode(signatureInBytes)),))


'''
Usage:
(pub,pvt) = utils.generateKeys(1024)
msg = "My Name Is Pratik"
signa = utils.sign(pvt, msg)
print(signa)
print(utils.verify(pub, msg, signa))
'''
# print(getHashValue("hello",160))
