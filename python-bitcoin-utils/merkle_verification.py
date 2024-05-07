import hashlib
import math

def verify_merkle_proof(proof, merkle_root, txid):
    """ Verify the merkle proof of a transaction in a block, 
    using the Bitcoin Core proof convention, obtained by 
    the RPC call gettxoutproof. Given the
    - proof
    - merkle_root
    - txid
    returns True if the proof is valid, False otherwise
    """
    # Reverse endianess
    merkle_root = reverse_endianess(merkle_root)
    txid = reverse_endianess(txid)

    # Check if proof contains merkle_root
    if merkle_root not in proof:
        return False
    
    # Extract data from proof
    # number of transactions (little endian)
    num_tx = int(reverse_endianess(proof.partition(merkle_root)[2][24:32]),16) 
    num_hashes = int(proof.partition(merkle_root)[2][32:34],16)
    height = math.ceil(math.log(num_tx, 2))
    body = proof.partition(merkle_root)[2][34:34+num_hashes*64]
    hashes = [body[i:i+64] for i in range(0, len(body), 64)]
    flags = proof.partition(merkle_root)[2][34+num_hashes*64:]
    num_flagbytes = 0
    flagbytes = ""
    if len(flags[2:])/2 == int(flags[:2], 16):
        num_flagbytes = int(flags[:2], 16)
        flagbytes = flags[2:]
    elif len(flags[4:])/2 == int(flags[:4], 16):
        num_flagbytes = int(flags[:4], 16)
        flagbytes = flags[4:]
    elif len(flags[6:])/2 == int(flags[:6], 16):
        num_flagbytes = int(flags[:6], 16)
        flagbytes = flags[6:]
    else:
        return False
    bits = ""
    for i in range (0,len(flagbytes),2):
        bits += bin(int(flagbytes[i:i+2], 16))[2:].zfill(8)[::-1]
    bits = bits[:2*height-1]

    # Check if body contains tx_id
    if txid not in body:
        return False

    # Traverse the partial merkle tree to reconstruct the root
    # start from the second one, since first one is root and always 1
    computed_root = traverse(bits[1:], 0, height, hashes)[2] 

    return computed_root == merkle_root

def traverse(bits, pos, height, hashes):
    """ Recursively traverses a partial merkle tree to reconstruct the root, given the 
        - flag bits indicating the position of the tx
        - position within the list of hashes
        - the current height 
        - the list of hashes
        Returns the 
        - new position 
        - the new list of bits
        - the computed hash
    """
    # This special case occurs when there are very few transactions in the block
    if len(bits) == 0 and pos == 0:
        return bits, pos, hash256(hashes[0] + hashes[1])
    # If height is 0, we have reached the leaf nodes
    if height == 0:
        return pos+1, bits, hashes[pos]
    else:
        bit = bits[0]
        if bit == '1':
            pos, bits, left = traverse(bits[1:], pos, height - 1, hashes)
            # Duplicate nodes if we ran out
            if (pos >= len(hashes)):
                right = left
            else:
                right = hashes[pos]
                pos += 1
        else:
            left = hashes[pos]
            pos += 1
            # we consume two bits here 0 because left is empty, 1 because right is not empty
            pos, bits, right = traverse(bits[2:], pos, height - 1, hashes)
        return pos, bits, hash256(left + right)


def reverse_endianess(hex_str):
    """ Reverse the endianness of a hex string """
    ba = bytearray.fromhex(hex_str)
    ba.reverse()
    return ba.hex()

def hash256(hex_str):
    """ Hash a hex string using double SHA-256 """
    bytes_str = bytes.fromhex(hex_str)
    hash_once = hashlib.sha256(bytes_str).digest()
    return hashlib.sha256(hash_once).digest().hex()
