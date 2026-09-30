// SPDX-License-Identifier: BSL-1.0
// Source: https://github.com/serial-coder/solidity-security-by-example/
pragma solidity 0.8.13;

abstract contract ReentrancyGuard {
    bool internal locked;

    modifier noReentrant() {
        require(!locked, "No re-entrancy");
        locked = true;
        _;
        locked = false;
    }
}
