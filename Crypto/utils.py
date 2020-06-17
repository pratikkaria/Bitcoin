from Crypto.Hash import SHA256


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
