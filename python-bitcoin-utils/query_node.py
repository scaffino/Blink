import requests
from requests.auth import HTTPBasicAuth 
import sys
import json
import globals
from consts import our_node, vultr_node


def get_block(block_hash: str):
    return rpc_request("getblock", [block_hash])


def get_block_hash(block_height: str):
    while True:
        response = rpc_request("getblockhash", [block_height])
        if response['error'] == None:
            return response['result']


def get_block_header(block_hash: str):
    return rpc_request("getblockheader", [block_hash])


def get_chain_tips():
    return rpc_request("getchaintips", [])


def get_raw_transaction(tx_id: str):
    return rpc_request("getrawtransaction", [tx_id, True]) # true is for verbosity


def get_txout_proof(tx_id: str, block_hash: str):
    return rpc_request("gettxoutproof", [[tx_id], block_hash]) #block hash is optional


def verify_txout_proof(proof: str):
    return rpc_request("verifytxoutproof", [proof])


def post_tx(tx_hex: str):
    return rpc_request("sendrawtransaction", [tx_hex])['result'] # returns txid

def get_node(counter: int):
    return our_node if counter % 2 == 0 else vultr_node

def rpc_request(method: str, params):
    data={"jsonrpc": "1.0", "id": "curltest", "method": method, "params": params}
    api_endpoint = 'http://127.0.0.1:'
    response = requests.post(f'{api_endpoint}{get_node(globals.counter)}',auth = HTTPBasicAuth('blink', 'blinkpwd'),data=json.dumps(data))

    globals.proof_size = globals.proof_size + sys.getsizeof(response.json())

    return response.json()
