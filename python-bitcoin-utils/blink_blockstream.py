#bitcoin testnet faucet
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.script import Script
from bitcoinutils.keys import P2pkhAddress, PrivateKey, PublicKey
from schnorr import schnorr_sign
from identity import Id
from helper import hash256, gen_secret
import init
import scripts
import txs
import hashlib
import struct
import requests
import time
import os
import random
import string
from binascii import unhexlify, hexlify
from datetime import datetime
from bitcoinutils.constants import SIGHASH_ALL
import json

init.init_network()

dry_run = True  # if true, no transactions will be posted to the testnet

#endpoints 
blockstream = 'https://blockstream.info/testnet/api' #blockstream
testnet_node = 'http://127.0.0.1:8332' #mainnet node
mainnet_node = 'http://127.0.0.1:8332' #testnet node
api_endpoint = blockstream

# k: common prefix parameter
k = 6

# entropy tx parameters
#id_user = Id('d44348ff037a7f65bcf9b7c86181828f5e05dbfe6cf2efe9af6362c8d53a00b0') #address is mhdTzofrDHXF18US18Y6ZfV5JhqCxa13yh
id_user = Id()
input_tx = 'a7235ddc11de3a1088ead0fcb47934105ed1a018518ea6ee6bffe96c0b83df5c'
output_indx = 1
coins = 98217

def main():

    
    fee = 283 # min fee blockstream testnet

    # test coins from faucet received at txid: 4ca4e42f3e83219cd2c7482322fb1f47c237d0533b31d054838db1410e22a54c
    #faucet https://testnet.help/en/btcfaucet/testnet#log

    entropy_tx = create_entropy_tx(id_user, input_tx, output_indx, coins, fee)
    if not dry_run:
        entropy_id = post_tx(entropy_tx)
    else:
        entropy_id = 'a7235ddc11de3a1088ead0fcb47934105ed1a018518ea6ee6bffe96c0b83df5c'

    print("...waiting for entropy tx to be confirmed...")
    while True:
        tx_with_block_info = get_tx(entropy_id) # get tx: withing the json there is the block height
        txjson = json.loads(tx_with_block_info)
        if txjson['status']['confirmed'] == True:
            print("Entropy tx is confirmed")
            break

    print("...retrieving and validating proof...")
    retrieve_and_validate_proof(txjson['status']['block_height']) 

# # # # # # # #
# Create entropy transaction 
# # # # # # # #

def create_entropy_tx(id_user: Id, input_txid: str, output_num: int, val: int, fee: int): 
    #input
    #tx_in = TxInput('1f0de4710d6d7d7e1cc38e8c86510eaa18ca5e42a176f39496c88e9cf25c11fb', 0) 
    tx_in = TxInput(input_txid, output_num)
    # entropy output
    op_return_script =  Script(['OP_RETURN', get_randomess(50)])
    tx_out = TxOutput(0, op_return_script)
    # payback output
    tx_out1 = TxOutput(int(val-fee), id_user.p2pkh)
    # create tx
    tx = Transaction([tx_in], [tx_out, tx_out1])
    #compute signature
    sig_user = id_user.sk.sign_input(tx, 0, id_user.p2pkh) 
    # unlocking script for the input
    tx_in.script_sig = Script([sig_user, id_user.pk.to_hex()])

    print("Entropy transaction: ", tx.serialize())
    return tx 

# # # # # # # #
# Post transaction 
# # # # # # # #

def post_tx(tx: Transaction):
    while True:
        response = requests.post(f'{api_endpoint}/tx', tx.serialize())  # blockstream
        if 'error' not in response.text:
            print("ENTROPY TX ID:  ", response.text )
            return(response.text)

# # # # # # # #
# Get transaction 
# # # # # # # #
    
def get_tx(txid: str):
    while True:
        response = requests.get(f'{api_endpoint}/tx/{txid}')  # blockstream
        if 'error' not in response.text:
            return(response.text)

# # # # # # # #
# Get block height 
# # # # # # # #

def get_blockid_at_height(height: str):
    while True:
        response = requests.get(f'{api_endpoint}/block-height/{height}') # blockstream
        if 'Block not found' not in response.text:
            return(response.text)

# # # # # # # #
# Get block header from id
# # # # # # # #

def get_blockheader_from_id(blockid: str):
    while True:
        response = requests.get(f'{api_endpoint}/block/{blockid}') # blockstream
        if 'Block not found' not in response.text:
            return(response.text)

# # # # # # # #
# Retrieve blocks for the Blink proof
# # # # # # # #

def retrieve_and_validate_proof(height: int):
    ids = []
    parents = []
    print("retrieveing blocks for the Blink proof")
    for ii in range(height-k, height+k+1):
        id = get_blockid_at_height(ii)
        ids.append(id)
        block_header = get_blockheader_from_id(id)
        # read json to extract the parent block
        blockheaderjson = json.loads(block_header)
        # check parent-child relations 
        parents.append(blockheaderjson['previousblockhash'])
        ctr = 0
        if (ii > height-6): 
            assert parents[ctr+1] == ids[ctr], "Child must contain parent" #todo: handle the case of a reorg: parent changes 
        ctr = ctr +1   
    print("Parent-child relation successfully checked")

# # # # # # # #
# Get randomness
# # # # # # # #

def get_randomess(length):
    return os.urandom(length).hex()

if __name__ == "__main__":
    main()

# Bloom filter python library: https://github.com/KenanHanke/rbloom




