from pow import check_pow
from merkle_verification import verify_merkle_proof
from jsonschema import validate
from schemas import (
    schema_block_header, schema_general, schema_confirmed_raw_tx
)
from node import Node
from jsonschema.exceptions import ValidationError
from transactions import Transaction

class Verifier():

    def broadcast_entropy(self, dry_run: str, nodes: list, entropy_tx: Transaction, txid: str): 

        honest_prover_counter = 0

        if dry_run: return True
        else:
            for node in nodes:
                received_txid = node.post_tx(entropy_tx.serialize()) 
                try: 
                    assert (txid == received_txid), "Assertion failed: txid received from prover is incorrect"
                    honest_prover_counter += 1
                except Exception as e:
                    print("Error while posting the entropy transaction to {}: {}".format(node,e) )
            if honest_prover_counter != 0: return True

    # Wait until the entropy tx has k confirmations, then check Blink proof
    def get_valid_proof(self, txid: str, nodes: list, k: int):
        valid_proof = False
        while not valid_proof:
            for node in nodes:
                tx_info = node.get_raw_transaction(txid)
                # wait until the entropy tx appears in the ledger and can be queried
                if not tx_info or not all(k in tx_info for k in ['result', 'error', 'id']) or tx_info['error'] is not None or 'confirmations' not in tx_info['result']:
                    continue
                else:
                    # wait until the entropy tx has k confirmations
                    check_received_data(tx_info, schema_confirmed_raw_tx, "Raw tx")
                    if tx_info['result']['confirmations'] > k:
                        print("Entropy tx with id {} has {} confirmations. Getting and validating Blink proof...".format(txid,k))
                        return self.check_proof(txid, tx_info, node, k)   
            # todo: add a break in case there is no valid proof ever ?     

    # Get and check the Blink proof of 2k + 1 blocks
    def check_proof(self, txid: str, tx_info: str, node: Node, k: int):
        entropy_block_header = node.get_block_header(
            tx_info['result']['blockhash']
        )
        check_received_data(
            entropy_block_header, schema_block_header, "Block header"
        )
        entropy_block_height = entropy_block_header['result']['height']

        for ii in range(entropy_block_height - k, entropy_block_height + k + 1):
            block_hash = ''
            while True:
                block_hash = node.get_block_hash(ii)
                if block_hash['error'] is None:
                    break
            check_received_data(block_hash, schema_general, "Block hash")
            block_hash = block_hash['result']
            block_header = node.get_block_header(block_hash)
            check_received_data(block_header, schema_block_header, "Block header")

            parenthash = block_header['result']['previousblockhash']
            previousblockhash = node.get_block_hash(ii - 1)
            check_received_data(previousblockhash, schema_general, "Block hash")
            previousblockhash = previousblockhash['result']
            if ii > entropy_block_height - k:
                assert parenthash == previousblockhash, "Ancestry check failed"

            # check pow
            bits = block_header['result']['bits']
            block_hash = block_header['result']['hash']
            check_pow(bits, block_hash)

            # check merkle proof of inclusion of entropy tx into the middle block
            if ii == entropy_block_height:
                proof = node.get_txout_proof(txid, block_hash)
                check_received_data(proof, schema_general, "Proof of tx inclusion")
                verify_merkle_proof(
                    proof['result'], block_header['result']['merkleroot'], txid
                )

        print("Blink proof is valid!")
        return True


def check_received_data(data: str, schema: str, data_type: str):
    if data is not None:
        if data_type == "Block hash":
            assert len(data['result']) == 64, f"Assertion failed: {data_type} is not 32 bytes"
        try:
            validate(data, schema)
        except ValidationError as e:
            validate(data, schema_general)
            print(f"{data_type} is not in the correct format: {e.message}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
