from pprint import pprint
import init
from merkle_verification import verify_merkle_proof
from node import Node
import globals
from entropy_tx import create_entropy_tx
from pow import check_pow
import configparser
import ast
from jsonschema import validate

#todo: verifier.py with all the logic
#blink.py creates the verifier and runs it

Config = configparser.ConfigParser()
Config.read('./python-bitcoin-utils/config.ini')
k = Config.getint('Settings', 'k')
nodes_endpoints = ast.literal_eval(Config['Settings']['nodes_endpoints'])
network = Config.get('Settings', 'network')

nodes = []
for ii in range(len(nodes_endpoints)):
    node_instance = Node(nodes_endpoints[ii])
    nodes.append(node_instance)
    
init.init_network(network)
globals.init()

#todo: make cli argument 
dry_run = True  # if true, no transaction will be posted on chain

proof_size = 0

def main():

    entropy_tx = create_entropy_tx()
    if not dry_run:
        txid = nodes[0].post_tx(entropy_tx.serialize())
        assert txid != None, "Entropy not posted"
        print("This is the id of newly posted entropy transaction: ", txid)
    else:
        txid = 'f5e923242ce27162bebe3eccbcb7c4d396efc881cc3f3f0c1868f9f5e1e389a6' # test txid
    
    print("...waiting for entropy tx to be k =", k, "confirmed...")
    
    # keep querying nodes until the entropy tx has k confirmations
    while True: 

        exit_while = False

        # loop over all the nodes the client connected to
        for jj in range(len(nodes)): 

            tx_info = nodes[jj].get_raw_transaction(txid) # todo: I need to do some checks to validate the answer. No trust on what I get
            if tx_info == None: continue
            #else: validate(tx_info, schema)
            #print(validate(tx_info, schema), '\n')
            if tx_info['error'] is None: 
                if 'confirmations' in tx_info['result']:
                    if tx_info['result']['confirmations'] > k:
                        print("Entropy tx has ", k, " confirmations")
                        entropy_block_header = nodes[jj].get_block_header(tx_info['result']['blockhash']) 
                        validate(entropy_block_header, globals.schema_block_header) # todo: add try catch 
                        entropy_block_height = entropy_block_header['result']['height']
                        retrieve_and_validate_proof(entropy_block_height, txid, nodes[jj])
                        exit_while = True
                        break 
                    else: continue
        # todo: for else construction. Else is when the loop complete (check)
        if exit_while == True: break

    print("Blink proof size: ", globals.proof_size)
    
# todo: test and handle errors. Return True/False
def retrieve_and_validate_proof(height: int, txid: str, endpoint: Node):
    for ii in range(height-k, height+k+1):
        #check parent-child
        block_hash = endpoint.get_block_hash(ii)
        assert(len(block_hash) == 64) # check it is a 32-bytes string
        block_header = endpoint.get_block_header(block_hash)
        validate(block_header, globals.schema_block_header) # todo: add try catch 
        parenthash = block_header['result']['previousblockhash']
        previousblockhash = endpoint.get_block_hash(ii-1)
        assert(len(previousblockhash) == 64) # check it is a 32-bytes string
        if (ii > height-k): 
            assert parenthash == previousblockhash, "Ancestry check failed"   
        
        #check pow
        bits = block_header['result']['bits']
        block_hash = block_header['result']['hash']
        check_pow(bits, block_hash)

        # check merkle proof of inclusion of entropy tx into the middle block
        if (ii == height):
            proof = endpoint.get_txout_proof(txid, block_hash)['result']
            verify_merkle_proof(proof, block_header['result']['merkleroot'], txid) 

    print("Blink proof is valid. Parent-child and PoW checks passed. Merkle verification of the entropy tx in the middle block passed.") 


if __name__ == "__main__":
    main()
