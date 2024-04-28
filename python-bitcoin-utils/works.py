import requests
from binascii import unhexlify, hexlify
from datetime import datetime
import json
from requests.auth import HTTPBasicAuth 
from pprint import pprint

#endpoint full node
api_endpoint = 'http://127.0.0.1:8332'

# common prefix parameter
k = 6

def main():
    entropy_id = '95c8def697b1c7cc4dfd7fc92f70c5aebcfb32fc6068b48d402e02602704c985'

    print("...waiting for entropy tx to be confirmed...")
    while True:
        tx_info = get_raw_transaction(entropy_id) # get tx: withing the json there is the block height
        #print(tx_info)
        if tx_info['result']['confirmations'] > 6: #in thisway I take tx when it already confirmed: no reorgs
            print("Entropy tx has 6 confirmations")
            break
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

    #print("Target: ", target_hex)
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
            assert parenthash == previousblockhash, "Ancestry check failed" # todo: handle the case of a reorg: parent changes  
        #print("Ancestry check passed")
        bits = block_header['result']['bits']
        block_hash = block_header['result']['hash']
        assert check_pow(bits, block_hash) == True
    print("Proof is valid: ancestry and PoW checks passed")


def get_block(block_hash: str):
    return rpc_request("getblock", [block_hash])


def get_block_hash(block_height: str, log: bool):
    if log: print("...waiting to get block at height... ", block_height)
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


def rpc_request(method: str, params):
    data={"jsonrpc": "1.0", "id": "curltest", "method": method, "params": params}
    #response = requests.post(f'{api_endpoint}',auth = HTTPBasicAuth('__cookie__', '1511bd691798013f380cbdb19eff15d391ff97a130039056ed182cb26669bd08'),data=json.dumps(data)) #testnet
    #mainnet rpcauth=blinklc:f95580392eae1d78790b6f2b09a7ea33$cd42531e702bec2f52cacd7f57f3dec8a948ec877fec0c65ddfcfa561ac5f66a
    response = requests.post(f'{api_endpoint}',auth = HTTPBasicAuth('blink', 'blinkpwd'),data=json.dumps(data))
    return response.json()



if __name__ == "__main__":
    main()