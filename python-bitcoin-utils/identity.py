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
    def __init__(self, which_chain: str, sk: str):
        setup(which_chain)
        self.sk = PrivateKey(secret_exponent=int(sk,16))
        print("Private Key: ", binascii.hexlify(PublicKey.to_bytes(self.sk)))
        self.pk = self.sk.get_public_key()
        #print("Compressed Public Key: ", self, "  ", self.sk.get_public_key().to_hex())
        #print(binascii.hexlify(decompress_pubkey(binascii.unhexlify('0229b3e0919adc41a316aad4f41444d9bf3a9b639550f2aa735676ffff25ba3898'))).decode())
        #print("Uncompressed Public Key: ", binascii.hexlify(decompress_pubkey(binascii.unhexlify(self.sk.get_public_key().to_hex()))).decode())
        self.addr = self.pk.get_address().to_string()
        print("address: ", self.pk.get_address().to_string())
        self.p2pkh = P2pkhAddress(self.addr).to_script_pub_key()
        #print("p2pkh: ", self.p2pkh)

    """ def __init__(self):

        setup("mainnet")

        # create a private key (deterministically)
        self.sk = PrivateKey(secret_exponent=1)

        # compressed is the default
        #print("\nPrivate key WIF:", self.sk.to_wif(compressed=True))

        # get the public key
        self.pk = self.sk.get_public_key()
        
        # compressed is the default
        print("Public key:", self.pk.to_hex(compressed=True))

        # get address from public key
        self.addr = self.pk.get_address()

        self.p2pkh = P2pkhAddress(self.addr).to_script_pub_key() """
