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
import sys

init.init_network()

dry_run = False  # if true, no transactions will be posted on chain
which_chain = 'mainnet'

#endpoints
secpriv_node = 8332 # secpriv port
vultr_node = 8331 # vultr port

# common prefix parameter
k = 6

# entropy tx parameters
id_user = Id(which_chain, 'a random string') 
#id_user = Id(which_chain)
input_tx = 'aba719b0532e805ff5f83c77bc9f741b1dec24c3b7b9323bfab7631ba0d7b6db'
output_indx = 1
coins = 42504

proof_size = 0

def main():

    if which_chain == 'testnet': fee = 290 # min fee testnet
    if which_chain == 'mainnet': fee = 7200 # mainnet

    entropy_tx = create_entropy_tx(id_user, input_tx, output_indx, coins, fee)
    if not dry_run:
        txid = post_tx(entropy_tx.serialize(), secpriv_node)
        assert txid != None, "Entropy not posted"
        print("This is the txid from sendrawtransaction: ", txid)
    else:
        txid = '474556047d2afe30463adbb387f1c8696b3d5b1dc4b03b76cfaf1c3477521a5f'
    
    print("...waiting for entropy tx to be k =", k, "confirmed...")
    ctr = 0
    which_node = 0
    while True: # query one time one node and the other time the other node
        if ctr%2 == 0: 
            which_node = secpriv_node
        else: 
            which_node = vultr_node
        ctr = ctr + 1
        
        tx_info = get_raw_transaction(txid, which_node) # get tx: within the json there is the block height
        if tx_info['error'] is None:
            if 'confirmations' in tx_info['result']:
                if tx_info['result']['confirmations'] > 6:
                    print("Entropy tx has 6 confirmations")
                    ctr = ctr -1
                    break
                else: continue

    if ctr%2 == 0: 
        entropy_block_header = get_block_header(tx_info['result']['blockhash'], secpriv_node)
        entropy_block_height = entropy_block_header['result']['height']
        retrieve_and_validate_proof(entropy_block_height, txid, secpriv_node, vultr_node)
    else: 
        entropy_block_header = get_block_header(tx_info['result']['blockhash'], vultr_node)
        entropy_block_height = entropy_block_header['result']['height']
        retrieve_and_validate_proof(entropy_block_height, txid, vultr_node, secpriv_node)

    print("this is the proof size: ", proof_size)

 
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
    

def retrieve_and_validate_proof(height: int, txid: str, node1: int, node2: int):
    print("...retrieving and validating proof...")
    for ii in range(height-k, height+k+1):
        #check parent-child
        block_header = get_block_header(get_block_hash(ii, True, node1), node1)
        parenthash = block_header['result']['previousblockhash']
        previousblockhash = get_block_hash(ii-1, False, node1)
        if (ii > height-k): 
            assert parenthash == previousblockhash, "Ancestry check failed"   
        
        #check pow
        bits = block_header['result']['bits']
        block_hash = block_header['result']['hash']
        assert check_pow(bits, block_hash) == True
    print("Ancestry and PoW checks passed")

    #check entropy is in the middle block
    proof = get_txout_proof(txid, get_block_hash(height, True, node1), node1)['result']
    is_txid = verify_txout_proof(proof, node2)['result'][0] # todo: let the other node verify it
    assert txid == is_txid, "Entropy not included in the (k+1)-th block of the proof"
    print("Entropy is in the (k+1)-th block of the proof")


def get_block(block_hash: str, node_port: int):
    return rpc_request("getblock", [block_hash], node_port)


def get_block_hash(block_height: str, log: bool, node_port: int):
    if log: print("get block at height ", block_height)
    while True:
        response = rpc_request("getblockhash", [block_height], node_port)
        #print(response['error']['message'])
        if response['error'] == None:
            return response['result']


def get_block_header(block_hash: str, node_port: int):
    #pprint(rpc_request("getblockheader", [block_hash]))
    return rpc_request("getblockheader", [block_hash], node_port)


def get_chain_tips():
    return rpc_request("getchaintips", [])


def get_raw_transaction(tx_id: str, node_port: int):
    return rpc_request("getrawtransaction", [tx_id, True], node_port) # true is for verbosity

def get_txout_proof(tx_id: str, block_hash: str, node_port: int):
    return rpc_request("gettxoutproof", [[tx_id], block_hash], node_port) #block hash is optional

def verify_txout_proof(proof: str, node_port: int):
    return rpc_request("verifytxoutproof", [proof], node_port) #block hash is optional 

def post_tx(tx_hex: str, node_port: int):
    #print(rpc_request("sendrawtransaction", [tx_hex]))
    return rpc_request("sendrawtransaction", [tx_hex], node_port)['result'] # returns txid

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


def rpc_request(method: str, params, node_port: int):
    data={"jsonrpc": "1.0", "id": "curltest", "method": method, "params": params}
    if which_chain == 'mainnet':
        api_endpoint = 'http://127.0.0.1:'
        response = requests.post(f'{api_endpoint}{node_port}',auth = HTTPBasicAuth('blink', 'blinkpwd'),data=json.dumps(data))
    if which_chain == 'testnet':
        api_endpoint = 'http://127.0.0.1:18332'
        response = requests.post(f'{api_endpoint}',auth = HTTPBasicAuth('__cookie__', '2097ff2078c19aea742a8a9114da10fd32ba615f924571fb420d4958ada0a29b'),data=json.dumps(data)) #testnet
   
    global proof_size 
    proof_size = proof_size + sys.getsizeof(response.json())

    return response.json()


if __name__ == "__main__":
    main()