import requests
from requests.auth import HTTPBasicAuth 
import sys
import json
import globals


class Node():

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def display(self):
        print(f"Endpoint: {self.endpoint}")

    def get_block(self, block_hash: str,):
        return self.rpc_request("getblock", [block_hash])


    def get_block_hash(self, block_height: str):
        while True:
            response = self.rpc_request("getblockhash", [block_height])
            if response['error'] == None:
                return response['result']


    def get_block_header(self, block_hash: str):
        return self.rpc_request("getblockheader", [block_hash])


    def get_chain_tips(self):
        return self.rpc_request("getchaintips", [])


    def get_raw_transaction(self, tx_id: str):
        return self.rpc_request("getrawtransaction", [tx_id, True]) # true is for verbosity


    def get_txout_proof(self, tx_id: str, block_hash: str):
        return self.rpc_request("gettxoutproof", [[tx_id], block_hash]) #block hash is optional


    def verify_txout_proof(self, proof: str):
        return self.rpc_request("verifytxoutproof", [proof])


    def post_tx(self, tx_hex: str):
        return self.rpc_request("sendrawtransaction", [tx_hex])['result'] # returns txid         

    def rpc_request(self, method: str, params):
        data={"jsonrpc": "1.0", "method": method, "params": params}
        try: 
            response = requests.post(self.endpoint,auth = HTTPBasicAuth('blink', 'blinkpwd'),data=json.dumps(data))
            globals.proof_size = globals.proof_size + sys.getsizeof(response.json())

        except requests.RequestException as e:
            print(f"Error querying node at {self.endpoint}: {e}")
            return None # Handle the error by returning None 

        return response.json()
