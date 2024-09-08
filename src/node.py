import requests
from requests.auth import HTTPBasicAuth 
import sys
import json

class Node():

    def __init__(self, endpoint, username, password):
        self.endpoint = endpoint
        self.username = username
        self.password = password
        self.bytes_received = 0
        self.bytes_sent = 0
        self.responsive = True

    def __repr__(self):
        return (f"Node(endpoint = {self.endpoint!r}, "
                f"username = {self.username!r}, "
                f"password = {self.password!r})")

    def get_block(self, block_hash: str,):
        return self.rpc_request("getblock", [block_hash])
    
    def get_block_hash(self, block_height: str):
        return self.rpc_request("getblockhash", [block_height])

    def get_block_header(self, block_hash: str):
        return self.rpc_request("getblockheader", [block_hash])

    def get_chain_tips(self):
        return self.rpc_request("getchaintips", [])

    def get_raw_transaction(self, tx_id: str):
        return self.rpc_request("getrawtransaction", [tx_id, True])  # true for obtaining a json

    def get_txout_proof(self, tx_id: str, block_hash: str):
        return self.rpc_request("gettxoutproof", [[tx_id], block_hash])  # block hash is optional

    def verify_txout_proof(self, proof: str):
        return self.rpc_request("verifytxoutproof", [proof])

    def post_tx(self, tx_hex: str):
        return self.rpc_request("sendrawtransaction", [tx_hex])['result']  # returns txid         

    def rpc_request(self, method: str, params):
        request_payload = {"jsonrpc": "1.0", "method": method, "params": params}

        self.bytes_sent = self.bytes_sent + len(json.dumps(request_payload).encode('utf-8'))

        try: 
            response = requests.post(self.endpoint, auth=HTTPBasicAuth(str(self.username), str(self.password)), data=json.dumps(request_payload))  
            self.bytes_received = self.bytes_received + sys.getsizeof(response.json()) 

            return response.json()

        except requests.RequestException as e:
            if self.responsive: 
                print(f"Node at {self.endpoint} is unresponsive: {e}")
                self.responsive = False
