from bitcoinutils.keys import P2pkhAddress, PrivateKey, PublicKey
from bitcoinutils.setup import setup

class Id:
    """
    Helper class for handling identity related keys and addresses easily
    """
    def __init__(self, sk: str, network: str):
        setup(network) # needed to compute mainnet address or testnet address
        self.sk = PrivateKey(secret_exponent=int(sk, 16))
        self.pk = self.sk.get_public_key()
        self.addr = self.pk.get_address().to_string()
        print("Address:", self.addr)
        self.p2pkh = P2pkhAddress(self.addr).to_script_pub_key()
