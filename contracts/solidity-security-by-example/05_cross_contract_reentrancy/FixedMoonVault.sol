// SPDX-License-Identifier: BSL-1.0
// Source: https://github.com/serial-coder/solidity-security-by-example/
pragma solidity 0.8.17;

import "./Dependencies.sol";

contract FixedMoonVault is ReentrancyGuard {
    IMoonToken public immutable moonToken;

    constructor(IMoonToken _moonToken) {
        moonToken = _moonToken;
    }

    function deposit() external payable noReentrant {
        bool success = moonToken.mint(msg.sender, msg.value);
        require(success, "Failed to mint token");
    }

    function withdrawAll() external noReentrant {
        uint256 balance = getUserBalance(msg.sender);
        require(balance > 0, "Insufficient balance"); // Check

        bool success = moonToken.burnAccount(msg.sender); // Effect
        require(success, "Failed to burn token");

        (success, ) = msg.sender.call{value: balance}(""); // Interaction
        require(success, "Failed to send Ether");
    }

    function getBalance() external view returns (uint256) {
        return address(this).balance;
    }

    function getUserBalance(address _user) public view returns (uint256) {
        return moonToken.balanceOf(_user);
    }
}
