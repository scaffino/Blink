from transactions import Transaction, TxInput, TxOutput
from identity import Id
from bitcoinutils.script import Script
import os

with open("./src/secret-key.txt", "r") as f:  # Use `with` for file handling
    secret_key = f.readline()

id_user = Id(secret_key)


def create_entropy_tx(input_txid: str, output_id: int, coins: int, fee: int):
    # Input
    tx_in = TxInput(input_txid, output_id)
    
    # Entropy output
    op_return_script = Script(['OP_RETURN', get_randomness(20)])
    tx_out = TxOutput(0, op_return_script)
    
    # Payback output
    tx_out1 = TxOutput(int(coins - fee), id_user.p2pkh)
    
    # Create transaction
    tx = Transaction([tx_in], [tx_out, tx_out1])
    
    # Compute signature
    sig_user = id_user.sk.sign_input(tx, 0, id_user.p2pkh)
    
    # Unlocking script for the input
    tx_in.script_sig = Script([sig_user, id_user.pk.to_hex()])
    
    print("Entropy transaction:", tx.serialize())
    return tx


def get_randomness(length):
    return os.urandom(length).hex()
