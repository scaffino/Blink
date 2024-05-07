from bitcoinutils.keys import P2pkhAddress, PrivateKey, PublicKey
import init
from helper import decompress_pubkey
from bitcoinutils.setup import setup
import binascii

init.init_network()

class Id:
    """
    Helper class for handling identity related keys and addresses easily
    """
    #def __init__(self, sk: str):
    def __init__(self, sk: str):
        self.sk = PrivateKey(secret_exponent=int(sk,16))
        print("Private Key: ", binascii.hexlify(PublicKey.to_bytes(self.sk)))
        self.pk = self.sk.get_public_key()
        #print("Compressed Public Key: ", self, "  ", self.sk.get_public_key().to_hex())
        #print("Uncompressed Public Key: ", binascii.hexlify(decompress_pubkey(binascii.unhexlify(self.sk.get_public_key().to_hex()))).decode())
        self.addr = self.pk.get_address().to_string()
        print("address: ", self.pk.get_address().to_string())
        self.p2pkh = P2pkhAddress(self.addr).to_script_pub_key()
        #print("p2pkh: ", self.p2pkh)
