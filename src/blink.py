#!/Users/gscaffino/anaconda3/bin/python

import ast
import argparse
import configparser

import init
from node import Node
from verifier import Verifier
from entropy_tx import create_entropy_tx


def main():
    # Read CLI commands
    parser = argparse.ArgumentParser(description="A simple CLI tool.")
    parser.add_argument('--dry-run', action='store_true', default=False)
    parser.add_argument('--mainnet', action='store_true', default=False)
    parser.add_argument(
        '--test-txid', 
        type=str, 
        default='e30df7cd39d12577f6a7b4cb91f545484822125728e7b9e0812366971b646525'
    )
    parser.add_argument('--config', default='./src/config.ini')
    args = parser.parse_args()

    # Read config file
    config = configparser.ConfigParser()
    config.read(args.config)

    k = config.getint('Common Prefix', 'k')

    if args.mainnet:
        nodes_endpoints = ast.literal_eval(config['Mainnet Settings']['nodes_endpoints'])
        nodes_usernames = ast.literal_eval(config['Mainnet Settings']['nodes_usernames'])
        nodes_passwords = ast.literal_eval(config['Mainnet Settings']['nodes_passwords'])
        network = config.get('Mainnet Settings', 'network')
        input_txid = ast.literal_eval(config['Mainnet Settings']['input_txid'])
        output_id = config.getint('Mainnet Settings', 'output_id')
        coins = config.getint('Mainnet Settings', 'coins')
        fee = config.getint('Mainnet Settings', 'fee')
    else:
        nodes_endpoints = ast.literal_eval(config['Testnet Settings']['nodes_endpoints'])
        nodes_usernames = ast.literal_eval(config['Testnet Settings']['nodes_usernames'])
        nodes_passwords = ast.literal_eval(config['Testnet Settings']['nodes_passwords'])
        network = config.get('Testnet Settings', 'network')
        input_txid = ast.literal_eval(config['Testnet Settings']['input_txid'])
        output_id = config.getint('Testnet Settings', 'output_id')
        coins = config.getint('Testnet Settings', 'coins')
        fee = config.getint('Testnet Settings', 'fee')

    # Connect to prover nodes
    nodes = []
    for ii in range(len(nodes_endpoints)):
        node_instance = Node(nodes_endpoints[ii], nodes_usernames[ii], nodes_passwords[ii])
        print(node_instance)
        nodes.append(node_instance)

    init.init_network(network)

    # Create entropy
    entropy_tx = create_entropy_tx(input_txid, output_id, coins, fee)

    # Verifier logic
    verifier = Verifier()
    txid = verifier.broadcast_entropy(args.dry_run, args.test_txid, nodes, entropy_tx)

    print("...waiting for entropy tx to be k = {} confirmed...".format(k))
    verifier.get_valid_proof(txid, nodes, k)

    # Compute bytes sent and received by the verifier
    bytes_received = 0
    bytes_sent = 0

    for node in nodes:
        bytes_received += node.bytes_received
        bytes_sent += node.bytes_sent

    print("Bytes received with {} provers: {}".format(len(nodes_endpoints), bytes_received))
    print("Bytes sent with {} provers: {}".format(len(nodes_endpoints), bytes_sent))


if __name__ == "__main__":
    main()
