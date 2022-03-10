from brownie import accounts, network, config, interface
from re import L
from scripts.utils import get_account


def get_weth():  # -> exchange ETH to WETH on the given address
    """
    Mints WETH by depositing ETH -> using WETH contract
    """

    # ABI -> came from the IWETH interface
    # Address
    account = get_account()
    print(account.address)
    # IWETH(address owner, address spender)
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit(
        {
            "from": account,
            "value": 0.1 * 10**18,
            "gas_limit": 100000,
            "allow_revert": True,
        }
    )
    tx.wait(1)
    # the return WETH we dont have to write ourself bc it's defined in the SC that we will get it if we deposit ETH

    print("Received 0.1 ETH ")
    return tx


def main():
    get_weth()
