import requests
from binascii import unhexlify, hexlify
from datetime import datetime
import json
from requests.auth import HTTPBasicAuth 
from pprint import pprint
from transactions import Transaction, TxInput, TxOutput
from bitcoinutils.script import Script
from bitcoinutils.keys import P2pkhAddress, PrivateKey, PublicKey
from identity import Id
import init
import os

init.init_network()

dry_run = True  # if true, no transactions will be posted on chain
which_chain = 'mainnet'

# common prefix parameter
k = 6

# entropy tx parameters
id_user = Id(which_chain, 'd44348ff037a7f65bcf9b7c86181828f5e05dbfe6cf2efe9af6362c8d53a00b0') 
#id_user = Id(which_chain)
input_tx = '4840fba885c6c319d756c6560c5f305cbba14e837d52dc78cbb58cf6a21694ca'
output_indx = 1
coins = 42225

def main():

    if which_chain == 'testnet': fee = 290 # min fee testnet
    if which_chain == 'mainnet': fee = 7000 #252 # min fee mainnet

    entropy_tx = create_entropy_tx(id_user, input_tx, output_indx, coins, fee)
    if not dry_run:
        txid = post_tx(entropy_tx.serialize())
        assert txid != None, "Entropy not posted"
        print("This is the txid from sendrawtransaction: ", txid)
    else:
        txid = '107b77e7b2bde5f3e0a47fd7bdadb1cc0d14c7056a02878b3d30904e5a73d4ff'
    
    print("...waiting for entropy tx to be k =", k, "confirmed...")
    while True:
        tx_info = get_raw_transaction(txid) # get tx: withing the json there is the block height
        #print(tx_info)
        if 'confirmations' in tx_info['result']:
            if tx_info['result']['confirmations'] > 6:
                print("Entropy tx has 6 confirmations")
                break
            else: continue
    entropy_block_header = get_block_header(tx_info['result']['blockhash'])
    entropy_block_height = entropy_block_header['result']['height']
    #pprint(get_raw_transaction('2276949477c406eae0e7cad0c11afc50b2a9def720c6b5ba111d605b9574743d'))
    retrieve_and_validate_proof(entropy_block_height)

 
def bits_to_target(bits): 
    bits_int = int(bits, 16)
    exp = bits_int >> 24 
    coeff = bits_int & 0xFFFFFF 
    target = coeff * (2 ** (8 * (exp - 3))) # Calculate target
    # Convert the target to a hexadecimal string and ensure it is 256 bits long (64 hex characters)
    target_hex = hex(target)[2:].zfill(64)  # Remove the '0x' and zero-pad to 64 characters
    return target_hex
    

def check_pow(bits: str, block_hash):
    target = bits_to_target(bits)
    if (block_hash <= target):
        return True
    

def retrieve_and_validate_proof(height: int):
    print("...retrieving and validating proof...")
    for ii in range(height-k, height+k+1):
        block_header = get_block_header(get_block_hash(ii, True))
        parenthash = block_header['result']['previousblockhash']
        previousblockhash = get_block_hash(ii-1, False)
        if (ii > height-k): 
            assert parenthash == previousblockhash, "Ancestry check failed" 

        bits = block_header['result']['bits']
        block_hash = block_header['result']['hash']
        assert check_pow(bits, block_hash) == True
    print("Ancestry and PoW checks passed")


def get_block(block_hash: str):
    return rpc_request("getblock", [block_hash])


def get_block_hash(block_height: str, log: bool):
    if log: print("get block at height ", block_height)
    while True:
        response = rpc_request("getblockhash", [block_height])
        #print(response['error']['message'])
        if response['error'] == None:
            return response['result']


def get_block_header(block_hash: str):
    #pprint(rpc_request("getblockheader", [block_hash]))
    return rpc_request("getblockheader", [block_hash])


def get_chain_tips():
    return rpc_request("getchaintips", [])


def get_raw_transaction(tx_id: str):
    return rpc_request("getrawtransaction", [tx_id, True]) # true is for verbosity

def post_tx(tx_hex: str):
    #print(rpc_request("sendrawtransaction", [tx_hex]))
    return rpc_request("sendrawtransaction", [tx_hex])['result'] # returns txid

def create_entropy_tx(id_user: Id, input_txid: str, output_num: int, val: int, fee: int): 
    #input
    #tx_in = TxInput('1f0de4710d6d7d7e1cc38e8c86510eaa18ca5e42a176f39496c88e9cf25c11fb', 0) 
    tx_in = TxInput(input_txid, output_num)
    # entropy output
    op_return_script =  Script(['OP_RETURN', get_randomess(20)])
    tx_out = TxOutput(0, op_return_script)
    # payback output
    tx_out1 = TxOutput(int(val-fee), id_user.p2pkh)
    # create tx
    tx = Transaction([tx_in], [tx_out, tx_out1])
    #compute signature
    sig_user = id_user.sk.sign_input(tx, 0, id_user.p2pkh) 
    # unlocking script for the input
    tx_in.script_sig = Script([sig_user, id_user.pk.to_hex()])
    txid = Transaction.get_transaction_digest(tx, 0, id_user.p2pkh)

    print("Entropy transaction: ", tx.serialize())
    return tx

def get_randomess(length):
    return os.urandom(length).hex()


def rpc_request(method: str, params):
    data={"jsonrpc": "1.0", "id": "curltest", "method": method, "params": params}
    if which_chain == 'mainnet':
        api_endpoint = 'http://127.0.0.1:8332' # secpriv
        #mainnet rpcauth=blinklc:f95580392eae1d78790b6f2b09a7ea33$cd42531e702bec2f52cacd7f57f3dec8a948ec877fec0c65ddfcfa561ac5f66a
        response = requests.post(f'{api_endpoint}',auth = HTTPBasicAuth('blink', 'blinkpwd'),data=json.dumps(data))
    if which_chain == 'testnet':
        api_endpoint = 'http://127.0.0.1:18332'
        response = requests.post(f'{api_endpoint}',auth = HTTPBasicAuth('__cookie__', '2097ff2078c19aea742a8a9114da10fd32ba615f924571fb420d4958ada0a29b'),data=json.dumps(data)) #testnet
    #print(response)
    return response.json()



if __name__ == "__main__":
    main()
