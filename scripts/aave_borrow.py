from webbrowser import get
from brownie import accounts, network, config, interface
from scripts.utils import get_account
from scripts.get_weth import get_weth
from web3 import Web3

# 0.1
AMOUNT = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        print("getting weth!!")
        get_weth()
    # ABI
    # Address
    lending_pool = get_lending_pool()

    # we then need to approvce the sending out of ERC20 token
    approve_erc20(AMOUNT, lending_pool.address, erc20_address, account)
    print("Depositing...")
    tx = lending_pool.deposit(
        erc20_address, AMOUNT, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("Deposited!")

    # borrow from colladeral -> how much should we borrow????
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)

    # borrowing
    # get DAI with respect to ETH (DAI/ETH) -> use chainlink pricefeed
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )

    amount_dai_to_borrow = (borrowable_eth * 0.95) / dai_eth_price
    # can only borrow 95% of ETH in DAI
    print(f"We are borrowing {amount_dai_to_borrow} DAI")

    # actually borrowing -> call borrow function in Lendingpools
    dai_address = config["networks"][network.show_active()]["dai_token"]
    # """borrow(
    #         address asset,
    #         uint256 amount,
    #         uint256 interestRateMode,
    #         uint16 referralCode,
    #         address onBehalfOf
    #     )"""
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,  # stable mode
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("borrowed some dai")
    get_borrowable_data(lending_pool, account)
    repay_all(Web3.toWei(amount_dai_to_borrow, "ether"), lending_pool, account)
    get_borrowable_data(lending_pool, account)


def repay_all(amount, lending_pool, account):
    approve_erc20(
        amount,
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amount,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("Repaid!!!!")


def get_asset_price(price_feed_address):
    # ABI
    # address
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)

    # get only price from the returned data
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"The DAI price is {converted_latest_price}")
    return float(converted_latest_price)


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        avaliaible_borrow_eth,
        current_liquidation_treshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    avaliaible_borrow_eth = Web3.fromWei(avaliaible_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f" You have {total_collateral_eth} worth of ETH deposited.")
    print(f" You have {total_debt_eth} worth of ETH borrowed.")
    print(f" You can borrow {avaliaible_borrow_eth} worth of ETH deposited.")
    return (float(avaliaible_borrow_eth), float(total_debt_eth))


def approve_erc20(amount, spender, erc20_address, account):
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    # ABI
    # Address
    return tx


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    # ABI
    # Address
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool
