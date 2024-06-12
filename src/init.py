import bitcoinutils.setup as setup


def init_network(network: str):
    if setup.get_network() is None:
        setup.setup(network)