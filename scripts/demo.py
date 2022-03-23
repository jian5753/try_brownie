from brownie import Contract, TwoWayArbi, accounts
import warnings

def main(owner, nonOwner, guyA, guyB):
    warnings.filterwarnings("ignore")

    UINT256_MAX = 115792089237316195423570985008687907853269984665640564039457584007913129639935
    END_OF_TIME = 999999999999999

    #region contract address
    PANCAKE_FACTORY_ADDRESS = "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73" 
    BAKERY_FACTORY_ADDRESS = "0x01bF7C66c6BD861915CdaaE475042d3c4BaE16A7" 
    PANCAKE_ROUTER_ADDRESS = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
    BAKERY_ROUTER_ADDRESS = "0xCDe540d7eAFE93aC5fE6233Bee57E1270D3E330F"
    BUSD_ADDRESS = "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"
    WBNB_ADDRESS = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
    #endregion
    #region fetching
    WBNB = Contract.from_explorer(WBNB_ADDRESS)
    BUSD = Contract.from_explorer(BUSD_ADDRESS)
    pancakeRouter = Contract.from_explorer(PANCAKE_ROUTER_ADDRESS)
    #pancakeFactory = Contract.from_explorer(PANCAKE_FACTORY_ADDRESS)
    #bakeryFactory = Contract.from_explorer(BAKERY_FACTORY_ADDRESS)
    bakeryRouter = Contract.from_explorer(BAKERY_ROUTER_ADDRESS)
    #pPair = Contract.from_explorer(pancakeFactory.getPair(BUSD_ADDRESS, WBNB_ADDRESS))
    #bPair = Contract.from_explorer(bakeryFactory.getPair(BUSD_ADDRESS, WBNB_ADDRESS))

    guyB.transfer(guyA, f"{guyB.balance() / 1e18 } ether");
    WBNB.deposit({'from': guyA, 'value': guyA.balance()})
    WBNB.approve(PANCAKE_ROUTER_ADDRESS, UINT256_MAX, {'from': guyA})
    BUSD.approve(BAKERY_ROUTER_ADDRESS, UINT256_MAX, {'from': guyB})
    #endregion
    #region create opportunity of arbitrage
    for i in range(3):
        pancakeRouter.swapExactTokensForTokens(
            WBNB.balanceOf(guyA),
            0,
            [WBNB_ADDRESS, BUSD_ADDRESS],
            guyB,
            END_OF_TIME,
            {'from': guyA}
        )
        bakeryRouter.swapExactTokensForTokens(
            BUSD.balanceOf(guyB),
            0,
            [BUSD_ADDRESS, WBNB_ADDRESS],
            guyA,
            END_OF_TIME,
            {'from': guyB}
        )
        #endregion

    #region deploy, deposit and approve
    TwoWayArbi.deploy({'from': owner})
    WBNB.deposit({'from': owner, 'value': 2 * 1e18})
    WBNB.approve(TwoWayArbi[0].address, UINT256_MAX, {'from': owner})
    #endregion
    #region normal arbitrage
    print('\n normal arbitrage \n')
    TwoWayArbi[0].tokenAInTokenBOut(
        BAKERY_ROUTER_ADDRESS, PANCAKE_ROUTER_ADDRESS,
        1e18,
        [WBNB_ADDRESS, BUSD_ADDRESS],
        [BUSD_ADDRESS, WBNB_ADDRESS],
        {'from': owner}
    )
    WBNB.withdraw(WBNB.balanceOf(owner), {'from': owner})
    #endregion
    #region non-owner
    print('\n non-owner \n')
    WBNB.deposit({'from': nonOwner, 'value': 1e18})
    WBNB.approve(TwoWayArbi[0].address, UINT256_MAX, {'from': nonOwner})
    TwoWayArbi[0].tokenAInTokenBOut(
        BAKERY_ROUTER_ADDRESS, PANCAKE_ROUTER_ADDRESS,
        1e18,
        [WBNB_ADDRESS, BUSD_ADDRESS],
        [BUSD_ADDRESS, WBNB_ADDRESS],
        {'from': nonOwner}
    )
    #endregion
    #region cost-loss;
    print('\n cost-loss \n')
    TwoWayArbi[0].tokenAInTokenBOut(
        PANCAKE_ROUTER_ADDRESS, BAKERY_ROUTER_ADDRESS, 
        1e18,
        [WBNB_ADDRESS, BUSD_ADDRESS],
        [BUSD_ADDRESS, WBNB_ADDRESS],
        {'from': owner}
    )
    #endregion
    #region balance
