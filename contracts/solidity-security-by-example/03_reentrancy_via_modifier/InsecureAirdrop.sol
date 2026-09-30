// SPDX-License-Identifier: BSL-1.0
// Source: https://github.com/serial-coder/solidity-security-by-example/
pragma solidity 0.8.13;

import "./Dependencies.sol";

contract InsecureAirdrop {
    mapping (address => uint256) private userBalances;
    mapping (address => bool) private receivedAirdrops;
    uint256 public immutable airdropAmount;

    constructor(uint256 _airdropAmount) {
        airdropAmount = _airdropAmount;
    }

    function receiveAirdrop() external neverReceiveAirdrop canReceiveAirdrop {
        userBalances[msg.sender] += airdropAmount;
        receivedAirdrops[msg.sender] = true;
    }

    modifier neverReceiveAirdrop {
        require(!receivedAirdrops[msg.sender], "You already received an Airdrop");
        _;
    }

    function _isContract(address _account) internal view returns (bool) {
        uint256 size;
        assembly {
            size := extcodesize(_account)
        }
        return size > 0;
    }

    modifier canReceiveAirdrop() {
        if (_isContract(msg.sender)) {
            require(
                IAirdropReceiver(msg.sender).canReceiveAirdrop(),
                "Receiver cannot receive an airdrop"
            );
        }
        _;
    }

    function getUserBalance(address _user) external view returns (uint256) {
        return userBalances[_user];
    }

    function hasReceivedAirdrop(address _user) external view returns (bool) {
        return receivedAirdrops[_user];
    }
}
