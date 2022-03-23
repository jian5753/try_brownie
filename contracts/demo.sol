pragma solidity ^0.8.0;
// SPDX-License-Identifier: MIT

interface IXXswap{
    // source https://github.com/Uniswap/uniswap-v2-periphery/blob/master/contracts/UniswapV2Router02.sol
    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts);
    function WETH() external pure returns (address); 
}

interface IERC20 {
    // source function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function transferFrom(
        address sender,
        address recipient,
        uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
    function allowance(address owner, address spender) external view returns (uint256);
}

contract TwoWayArbi{
    address internal owner;

    constructor(){
        owner = msg.sender;
    }
    
    function tokenAInTokenBOut(
        address _platform1,
        address _platform2,
        uint amountIn,
        address[] calldata firstway,
        address[] calldata secondway
    ) external {
        require(msg.sender == owner);
        IXXswap platform1 = IXXswap(_platform1);
        IXXswap platform2 = IXXswap(_platform2);
        IERC20 firstERC = IERC20(firstway[0]);
        IERC20 secondERC = IERC20(secondway[0]);
        
        // transfer tokens to this contract
        firstERC.transferFrom(msg.sender, address(this), amountIn);
        
        // approve platform1 to spend token1 tokenAInTokenBOut
        firstERC.approve(address(platform1), amountIn);

        // swap
        platform1.swapExactTokensForTokens(
            amountIn,
            0,
            firstway,
            address(this),
            999999999999999
        );
        
        uint256 secondTokenReceived = secondERC.balanceOf(address(this));
        
        // approve platform2 to spend our token2
        secondERC.approve(address(platform2), secondTokenReceived);
        secondERC.allowance(address(this), address(platform2));
        
        //second swap
        platform2.swapExactTokensForTokens(
             secondTokenReceived,
             0,
             secondway,
             address(this),
             999999999999999
        );
        uint256 finalReceived = firstERC.balanceOf(address(this));
        if (finalReceived < amountIn)
        {
            revert();
        }
        
    }   

    function showOwner() view external returns(address ownerAddress){
        ownerAddress = owner;
    }
}