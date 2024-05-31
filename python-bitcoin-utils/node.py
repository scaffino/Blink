import requests
from requests.auth import HTTPBasicAuth 
import sys
import json
import globals

# one class with multiple instances of it having different endpoints

def get_block(block_hash: str, endpoint: str):
    return rpc_request("getblock", [block_hash], endpoint)


def get_block_hash(block_height: str, endpoint: str):
    while True:
        response = rpc_request("getblockhash", [block_height], endpoint)
        if response['error'] == None:
            return response['result']


def get_block_header(block_hash: str, endpoint: str):
    return rpc_request("getblockheader", [block_hash], endpoint)


def get_chain_tips():
    return rpc_request("getchaintips", [])


def get_raw_transaction(tx_id: str, endpoint: str):
    return rpc_request("getrawtransaction", [tx_id, True], endpoint) # true is for verbosity


def get_txout_proof(tx_id: str, block_hash: str, endpoint: str):
    return rpc_request("gettxoutproof", [[tx_id], block_hash], endpoint) #block hash is optional


def verify_txout_proof(proof: str, endpoint: str):
    return rpc_request("verifytxoutproof", [proof], endpoint)


def post_tx(tx_hex: str, endpoint: str):
    return rpc_request("sendrawtransaction", [tx_hex], endpoint)['result'] # returns txid         

def rpc_request(method: str, params, endpoint: str):
    data={"jsonrpc": "1.0", "method": method, "params": params}
    try: 
        response = requests.post(endpoint,auth = HTTPBasicAuth('blink', 'blinkpwd'),data=json.dumps(data))
        globals.proof_size = globals.proof_size + sys.getsizeof(response.json())

    except requests.RequestException as e:
        print(f"Error querying node at {endpoint}: {e}")
        return None # Handle the error by returning None 

    return response.json()
