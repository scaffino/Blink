#!/Users/gscaffino/anaconda3/bin/python

import init
from merkle_verification import verify_merkle_proof
from node import Node
from verifier import Verifier
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
    parser.add_argument('--test-txid', type=str, default='e30df7cd39d12577f6a7b4cb91f545484822125728e7b9e0812366971b646525') #'f5e923242ce27162bebe3eccbcb7c4d396efc881cc3f3f0c1868f9f5e1e389a6') e30df7cd39d12577f6a7b4cb91f545484822125728e7b9e0812366971b646525
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
    
    verifier = Verifier()
    txid = verifier.broadcast_entropy(args.no_dry_run, args.test_txid, nodes, entropy_tx) 
    print("...waiting for entropy tx to be k =", k, "confirmed...")
    verifier.get_proof(txid, nodes, k)

if __name__ == "__main__":
    main()
