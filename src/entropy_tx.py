from transactions import Transaction, TxInput, TxOutput
from identity import Id
from bitcoinutils.script import Script
import os

f = open("./src/secret-key.txt", "r") # the secret key file only contains the secret key
secret_key = f.readline()

id_user = Id(secret_key) 
input_txid = 'aba719b0532e805ff5f83c77bc9f741b1dec24c3b7b9323bfab7631ba0d7b6db'
output_num = 1
coins = 42504
fee = 7200

def create_entropy_tx(): 
    # input
    tx_in = TxInput(input_txid, output_num)
    # entropy output
    op_return_script = Script(['OP_RETURN', get_randomess(20)])
    tx_out = TxOutput(0, op_return_script)
    # payback output
    tx_out1 = TxOutput(int(coins - fee), id_user.p2pkh)
    # create tx
    tx = Transaction([tx_in], [tx_out, tx_out1])
    # compute signature
    sig_user = id_user.sk.sign_input(tx, 0, id_user.p2pkh) 
    # unlocking script for the input
    tx_in.script_sig = Script([sig_user, id_user.pk.to_hex()])
    # txid = Transaction.get_transaction_digest(tx, 0, id_user.p2pkh)

    print("Entropy transaction: ", tx.serialize())
    return tx


def get_randomess(length):
    return os.urandom(length).hex()
