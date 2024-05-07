from pprint import pprint
import init
from consts import k
from merkle_verification import verify_merkle_proof
from query_node import post_tx, get_block_hash, get_block_header, get_raw_transaction, get_txout_proof
import globals
from entropy_tx import create_entropy_tx
from check_pow import check_pow

init.init_network()
globals.init()

dry_run = True  # if true, no transaction will be posted on chain

proof_size = 0

def main():

    entropy_tx = create_entropy_tx()
    if not dry_run:
        txid = post_tx(entropy_tx.serialize())
        assert txid != None, "Entropy not posted"
        print("This is the id of newly posted entropy transaction: ", txid)
    else:
        txid = '474556047d2afe30463adbb387f1c8696b3d5b1dc4b03b76cfaf1c3477521a5f'
    
    print("...waiting for entropy tx to be k =", k, "confirmed...")
    
    while True: 
        
        tx_info = get_raw_transaction(txid)
        if tx_info['error'] is None:
            if 'confirmations' in tx_info['result']:
                if tx_info['result']['confirmations'] > 6:
                    print("Entropy tx has 6 confirmations")
                    entropy_block_header = get_block_header(tx_info['result']['blockhash'])
                    entropy_block_height = entropy_block_header['result']['height']
                    retrieve_and_validate_proof(entropy_block_height, txid)
                    break
                else: continue
        globals.counter = globals.counter + 1

    print("Blink proof size: ", globals.proof_size)
    

def retrieve_and_validate_proof(height: int, txid: str):
    for ii in range(height-k, height+k+1):
        #check parent-child
        block_hash = get_block_hash(ii)
        block_header = get_block_header(block_hash)
        parenthash = block_header['result']['previousblockhash']
        previousblockhash = get_block_hash(ii-1)
        if (ii > height-k): 
            assert parenthash == previousblockhash, "Ancestry check failed"   
        
        #check pow
        bits = block_header['result']['bits']
        block_hash = block_header['result']['hash']
        check_pow(bits, block_hash)

        # check merkle proof of inclusion of entropy tx into the middle block
        if (ii == height):
            proof = get_txout_proof(txid, block_hash)['result']
            verify_merkle_proof(proof, block_header['result']['merkleroot'], txid)

    print("Blink proof is valid. Parent-child and PoW checks passed. Merkle verification of the entropy tx in the middle block passed.") 


if __name__ == "__main__":
    main()