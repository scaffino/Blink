#!/Users/gscaffino/anaconda3/bin/python

import init
from merkle_verification import verify_merkle_proof
from node import Node
import globals 
from entropy_tx import create_entropy_tx
from pow import check_pow
import configparser
import ast
from jsonschema import validate
from schemas import schema_block_header
import argparse

def main():

    parser = argparse.ArgumentParser(description="A simple CLI tool.")
    parser.add_argument('--no-dry-run', action='store_false', default=True) 
    parser.add_argument('--test-txid', type=str, default='f5e923242ce27162bebe3eccbcb7c4d396efc881cc3f3f0c1868f9f5e1e389a6')
    parser.add_argument('--config', default='./src/config.ini')
    args = parser.parse_args()

    Config = configparser.ConfigParser()
    Config.read(args.config) 
    k = Config.getint('Settings', 'k')
    nodes_endpoints = ast.literal_eval(Config['Settings']['nodes_endpoints'])
    nodes_usernames = ast.literal_eval(Config['Settings']['nodes_usernames'])
    nodes_passwords = ast.literal_eval(Config['Settings']['nodes_passwords'])
    network = Config.get('Settings', 'network')

    nodes = []
    for ii in range(len(nodes_endpoints)):
        node_instance = Node(nodes_endpoints[ii], nodes_usernames[ii], nodes_passwords[ii])
        print(node_instance)
        nodes.append(node_instance)
        
    init.init_network(network)
    globals.init()

    entropy_tx = create_entropy_tx()
    if not args.no_dry_run: 
        txid = nodes[0].post_tx(entropy_tx.serialize())
        assert txid is not None, "Entropy not posted"
        print("This is the id of newly posted entropy transaction: ", txid)
    else:
        txid = args.test_txid 
    
    print("...waiting for entropy tx to be k =", k, "confirmed...")
    
    # keep querying nodes until the entropy tx has k confirmations
    confirmed = False
    while not confirmed:         

        # loop over all the nodes the client connected to
        for node in nodes:

            tx_info = node.get_raw_transaction(txid)  
            if tx_info is None:
                continue
            if tx_info['error'] is None: 
                if 'confirmations' in tx_info['result']:
                    if tx_info['result']['confirmations'] > k:
                        print("Entropy tx has ", k, " confirmations")
                        entropy_block_header = node.get_block_header(tx_info['result']['blockhash']) 
                        validate(entropy_block_header, schema_block_header)  
                        entropy_block_height = entropy_block_header['result']['height']
                        retrieve_and_validate_proof(entropy_block_height, txid, node, k)
                        confirmed = True
                        break

    print("Blink proof size: ", globals.proof_size)


# todo: test and handle errors. 
def retrieve_and_validate_proof(height: int, txid: str, endpoint: Node, k: int):
    for ii in range(height-k, height+k+1):
        # check parent-child
        block_hash = endpoint.get_block_hash(ii)
        assert (len(block_hash) == 64)  # check it is a 32-bytes string
        block_header = endpoint.get_block_header(block_hash)
        validate(block_header, schema_block_header)  # todo: add try catch 
        parenthash = block_header['result']['previousblockhash']
        previousblockhash = endpoint.get_block_hash(ii-1)
        assert (len(previousblockhash) == 64)  # check it is a 32-bytes string
        if (ii > height-k):
            assert parenthash == previousblockhash, "Ancestry check failed"  
        
        # check pow
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
