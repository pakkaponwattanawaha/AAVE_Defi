from re import L
from scripts.utils import get_account


def main():
    pass


def get_weth():
    """
    Mints WETH by depositing ETH -> using WETH contract
    """

    # ABI
    # Address
    account = get_account()
    # IWETH(address owner, address spender)
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": 0.1 * 10**18})
    tx.wait(1)
    print("Received 0.1 ETH ")
