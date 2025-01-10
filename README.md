# Blink Overview

Blink is an *interactive light client for Proof-of-Work blockchains* which, contrary to other existing clients (e.g., [NiPoPoW](https://nipopows.com/), [Flyclient](https://ieeexplore.ieee.org/document/9152680), [SPV](https://bitcoin.org/bitcoin.pdf), and more) operates by only consuming a with constant amount of communication, computational, and storage resources, i.e., $\mathcal{O}(1)$. 

Contrary to $\mathcal{O}(1)$ zero-knowledge based clients, Blink does not assume a trusted setup. 

## Proof Design
In a nutshell, the Blink client connects to multiple full nodes, so that at least one of them can be assumed honest.

The client locally samples a random value $\eta$, includes it in a transaction $\mathsf{Tx}_\eta$, and sends it to the full nodes. For instance, $\mathsf{Tx}_\eta$ can be a payment to a vendor's fresh address, sampled with high entropy.
Then, Blink waits for $\mathsf{Tx}_\eta$ to be included on-chain in a block and confirmed. The full nodes respond to the client with a proof $\pi$ consisting of only $2k+1$ consecutive block headers, with the header of the block including $\mathsf{Tx}_\eta$ sitting in the middle; $k$ is the *common prefix* security parameter, e.g., the conventional $6$ confirmation blocks in Bitcoin.  

This proof ensures that *the first block in the proof is stable* and, therefore, it can be considered as a checkpoint or as a new genesis. 

## Security 
Blink is proven secure in the [Bitcoin Backbone](https://dl.acm.org/doi/full/10.1145/3653445) model, assuming a static population (i.e., static difficulty) and an adaptive adversary holding less than 50% of the computational power of the network.

## Paper

For a full description and formalization, see the [Blink paper](https://eprint.iacr.org/2024/692). 

# The Blink Client

## Config

In the ```src/config.ini``` file, enter the endpoints for full nodes (mainnet and/or testnet), the details of the UTXO the entropy transaction must spend, the common prefix security parameter, and your local path to the file holding your secret key.

## CLI commands

```--mainnet```: the client is run on mainnet. If omitted, testnet is default.

```--dry-run```: the client is run with a default entropy transaction id. If omitted, the client broadcast a new entropy transaction. By using it in combination with ```--entropy_txid```, you can provide a new entropy transaction id to use

## Run 

The Blink client can be executed either via the ```Makefile``` or via the shebang line. If the entropy transaction is already on-chain and its txid is known, you can run the following command:

```make ARGS="--dry-run --mainnet --test-txid=your_entropy_txid"```

else, to create and broadcast a new entropy transaction run 

```make ARGS="--mainnet"``` 
