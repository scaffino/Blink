#!/Users/gscaffino/anaconda3/bin/python

import init
from node import Node
from verifier import Verifier
from entropy_tx import create_entropy_tx
import configparser
import ast
import argparse

def main():

    # read cli commands
    parser = argparse.ArgumentParser(description="A simple CLI tool.")
    parser.add_argument('--no-dry-run', action='store_false', default=True) 
    parser.add_argument('--test-txid', type=str, default='e30df7cd39d12577f6a7b4cb91f545484822125728e7b9e0812366971b646525') 
    parser.add_argument('--config', default='./src/config.ini')
    args = parser.parse_args()

    # read config file
    Config = configparser.ConfigParser()
    Config.read(args.config) 
    k = Config.getint('Settings', 'k')
    nodes_endpoints = ast.literal_eval(Config['Settings']['nodes_endpoints'])
    nodes_usernames = ast.literal_eval(Config['Settings']['nodes_usernames'])
    nodes_passwords = ast.literal_eval(Config['Settings']['nodes_passwords'])
    network = Config.get('Settings', 'network')

    # connect to prover nodes
    nodes = []
    for ii in range(len(nodes_endpoints)):
        node_instance = Node(nodes_endpoints[ii], nodes_usernames[ii], nodes_passwords[ii])
        print(node_instance)
        nodes.append(node_instance)
    init.init_network(network)

    # create entropy
    entropy_tx = create_entropy_tx()
    
    # verifier logic
    verifier = Verifier()
    txid = verifier.broadcast_entropy(args.no_dry_run, args.test_txid, nodes, entropy_tx) 
    
    print("...waiting for entropy tx to be k = {} confirmed...".format(k))
    verifier.get_valid_proof(txid, nodes, k)

    # compute bytes send and received by the verifier 
    bytes_received = 0
    bytes_sent = 0
    for node in range(len(nodes_endpoints)):
        bytes_received = bytes_received + nodes[node].bytes_received
        bytes_sent = bytes_sent + nodes[node].bytes_sent

    print("Bytes received with {} provers: {}".format(len(nodes_endpoints), bytes_received))
    print("Bytes sent with {} provers: {}".format(len(nodes_endpoints), bytes_sent))

if __name__ == "__main__":
    main()
