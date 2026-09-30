// SPDX-License-Identifier: BSL-1.0
// Source: https://github.com/serial-coder/solidity-security-by-example/
pragma solidity 0.8.13;

interface IAirdropReceiver {
    function canReceiveAirdrop() external returns (bool);
}
