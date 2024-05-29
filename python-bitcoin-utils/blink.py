from pprint import pprint
import init
from merkle_verification import verify_merkle_proof
from query_node import post_tx, get_block_hash, get_block_header, get_raw_transaction, get_txout_proof
import globals
from entropy_tx import create_entropy_tx
from check_pow import check_pow
import configparser
import ast

#todo: verifier.py with all the logic
#blink.py creates the verifier and runs it

Config = configparser.ConfigParser()
Config.read('./python-bitcoin-utils/config.ini')
k = Config.getint('Settings', 'k')
nodes_endpoints = ast.literal_eval(Config['Settings']['nodes_endpoints'])
network = Config.get('Settings', 'network')

init.init_network(network)
globals.init()

#todo: make cli argument 
dry_run = True  # if true, no transaction will be posted on chain

proof_size = 0

def main():

    entropy_tx = create_entropy_tx()
    if not dry_run:
        txid = post_tx(entropy_tx.serialize(), nodes_endpoints[0])
        assert txid != None, "Entropy not posted"
        print("This is the id of newly posted entropy transaction: ", txid)
    else:
        txid = 'f5e923242ce27162bebe3eccbcb7c4d396efc881cc3f3f0c1868f9f5e1e389a6' # test txid
    
    print("...waiting for entropy tx to be k =", k, "confirmed...")
    
    # keep querying nodes until the entropy tx has k confirmations
    while True: 

        exit_while = False

        # loop over all the nodes the client connected to
        for endpoint in nodes_endpoints: 

            tx_info = get_raw_transaction(txid, endpoint) # todo: I need to do some checks to validate the answer. No trust on what I get
            if tx_info == None: continue
            if tx_info['error'] is None: 
                if 'confirmations' in tx_info['result']:
                    if tx_info['result']['confirmations'] > k:
                        print("Entropy tx has ", k, " confirmations")
                        entropy_block_header = get_block_header(tx_info['result']['blockhash'], endpoint) #todo: check I get it and check validity 
                        entropy_block_height = entropy_block_header['result']['height']
                        retrieve_and_validate_proof(entropy_block_height, txid, endpoint)
                        exit_while = True
                        break 
                    else: continue
        # todo: for else construction. Else is when the loop complete (check)
        if exit_while == True: break

    print("Blink proof size: ", globals.proof_size)
    
# todo: test and handle errors. Return True/False
def retrieve_and_validate_proof(height: int, txid: str, endpoint: str):
    for ii in range(height-k, height+k+1):
        #check parent-child
        block_hash = get_block_hash(ii, endpoint)
        block_header = get_block_header(block_hash, endpoint)
        parenthash = block_header['result']['previousblockhash']
        previousblockhash = get_block_hash(ii-1, endpoint)
        if (ii > height-k): 
            assert parenthash == previousblockhash, "Ancestry check failed"   
        
        #check pow
        bits = block_header['result']['bits']
        block_hash = block_header['result']['hash']
        check_pow(bits, block_hash)

        # check merkle proof of inclusion of entropy tx into the middle block
        if (ii == height):
            proof = get_txout_proof(txid, block_hash, endpoint)['result']
            verify_merkle_proof(proof, block_header['result']['merkleroot'], txid) 

    print("Blink proof is valid. Parent-child and PoW checks passed. Merkle verification of the entropy tx in the middle block passed.") 


if __name__ == "__main__":
    main()