#!/usr/local/bin/python 

import ast
import argparse
import configparser
import init
from identity import Id
from node import Node
from verifier import Verifier
from entropy_tx import create_entropy_tx


def main():

    # read cli commands
    parser = argparse.ArgumentParser(description="A simple CLI tool for Blink PoPoW.")
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
    network = 'Mainnet' if args.mainnet else 'Testnet' 
    settings = {key: ast.literal_eval(config[network][key]) for key in [
        'nodes_endpoints', 
        'nodes_usernames', 
        'nodes_passwords' 
    ]}
    nodes = [
        Node(endpoint, username, password) 
        for endpoint, username, password in zip(settings['nodes_endpoints'], settings['nodes_usernames'], settings['nodes_passwords']) 
    ]
    number_of_nodes = len(nodes)
    input_txid = ast.literal_eval(config[network]['input_txid'])
    output_id = config.getint(network, 'output_id')
    coins = config.getint(network, 'coins')
    fee = config.getint(network, 'fee')
    sk_file = ast.literal_eval(config['Secret Key File']['key_file'])
    k = config.getint('Common Prefix', 'k')

    init.init_network(network)

    # Initialize user
    f = open(sk_file, "r") # the secret key file only contains the secret key
    secret_key = f.readline()
    id_user = Id(secret_key)

    # Create entropy
    entropy_tx = create_entropy_tx(input_txid, output_id, coins, fee, id_user)

    # Verifier logic
    verifier = Verifier()
    txid = verifier.broadcast_entropy(args.dry_run, args.test_txid, nodes, entropy_tx)

    print("...waiting for entropy tx to be k = {} confirmed...".format(k))
    verifier.get_valid_proof(txid, nodes, k)

    # Compute bytes sent and received by the verifier
    bytes_received = 0
    bytes_sent = 0
    for node in nodes: 
        bytes_received += bytes_received + node.bytes_received 
        bytes_sent = bytes_sent + node.bytes_sent

    print("Bytes received with {} provers: {}".format(number_of_nodes, bytes_received))
    print("Bytes sent with {} provers: {}".format(number_of_nodes, bytes_sent))


if __name__ == "__main__":
    main()
