from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto import Random
import base64

def verifyMerkleTree(mrkl_root):
    if mrkl_root.leftNode is None and mrkl_root.rightNode is None:
        return True
    if mrkl_root.hashValue == getHashValue(mrkl_root.leftNode.hashValue, mrkl_root.rightNode.hashValue):
        return verifyMerkleTree(mrkl_root.leftNode) and verifyMerkleTree(mrkl_root.rightNode)

    return False

def getHashValue(left: str, right: str) -> str:
    newHash = SHA256.new()
    newData: str = left+right
    newHash.update(newData.encode('utf-8'))

    return newHash.hexdigest()

def generateKeys(bits: int):
    new_key = RSA.generate(bits)
    private_key = new_key
    public_key = new_key.publickey()
    return (public_key, private_key)

def sign(privatekey, message: str) -> str:
    hashOfMessage: str = getHashValue(message, "")
    hashInBytes: bytes = str.encode(hashOfMessage)
    return base64.b64encode(str((privatekey.sign(hashInBytes,''))[0]).encode()).decode()

def verify(publickey, message:str, signature: str) -> bool:
    hashOfMessage: str = getHashValue(message, "")
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
