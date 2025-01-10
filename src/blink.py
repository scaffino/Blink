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
    parser = argparse.ArgumentParser(description="A simple CLI tool for the Blink client.")
    parser.add_argument('--dry-run', action='store_true', default=False)
    parser.add_argument('--mainnet', action='store_true', default=False)
    parser.add_argument(
        '--entropy-txid', 
        type=str, 
        default='e30df7cd39d12577f6a7b4cb91f545484822125728e7b9e0812366971b646525'
    )
    parser.add_argument('--config', default='./src/config.ini')
    args = parser.parse_args()

    # Read config file
    config = configparser.ConfigParser()
    config.read(args.config)
    network = 'mainnet' if args.mainnet else 'testnet' 
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
    input_txid = ast.literal_eval(config['entropy transaction']['input_txid'])
    output_id = config.getint('entropy transaction', 'output_id')
    coins = config.getint('entropy transaction', 'coins')
    fee = config.getint('entropy transaction', 'fee')
    sk_file = ast.literal_eval(config['secret key file']['key_file'])
    k = config.getint('common prefix', 'k')

    init.init_network(network)

    # Initialize user
    f = open(sk_file, "r") # the secret key file only contains the secret key
    secret_key = f.readline()
    id_user = Id(secret_key, network)

    # Create entropy
    entropy_tx, txid = create_entropy_tx(input_txid, output_id, coins, fee, id_user)
    if args.dry_run: txid = args.entropy_txid

    # Verifier logic
    verifier = Verifier()
    assert (verifier.broadcast_entropy(args.dry_run, nodes, entropy_tx, txid)), "All provers returned an incorrect txid"

    print("...waiting for entropy tx to be k = {} confirmed...".format(k))
    assert (verifier.get_valid_proof(txid, nodes, k)), "All received Blink proofs are invalid"

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
