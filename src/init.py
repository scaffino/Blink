import bitcoinutils.setup as setup

def init_network(network: str):
    if setup.get_network() == None:
        setup.setup(network)