// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0 <0.9.0;

contract Organism {
    uint256 public homeoscore;            // Ranges from 0 to 100
    uint256 public marketSensitivity;     
    uint256 public feedSensitivity;       
    bool public isAlive;

    address public owner;

    event Fed(address indexed from, uint256 value, uint256 newHomeoscore);
    event MarketEvent(uint256 marketDropPercentage, uint256 decreaseAmount, uint256 newHomeoscore);
    event TraitsUpdated(uint256 newMarketSensitivity, uint256 newFeedSensitivity);
    event Death(uint256 finalHomeoscore);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    modifier onlyAlive() {
        require(isAlive, "RIP");
        _;
    }

    constructor() {
        owner = msg.sender;
        homeoscore = 50;           // Starting in the middle.
        marketSensitivity = 5;
        feedSensitivity = 5;
        isAlive = true;
    }

    function feed() external payable onlyAlive {
        require(msg.value > 0, "Send some ETH to feed");
        // Using 1e15 as divisor so 0.001 ETH ~ 1 point (scaled by feedSensitivity)
        uint256 increase = (msg.value * feedSensitivity) / 1e15;
        homeoscore += increase;
        if (homeoscore > 100) {
            homeoscore = 100;
        }
        emit Fed(msg.sender, msg.value, homeoscore);
        checkDeath();
    }

    function updateMarketEvent(uint256 marketDropPercentage) external onlyOwner onlyAlive {
        // Assume marketDropPercentage is already processed so that if it's >0 then it's an actual drop.
        uint256 decrease = (marketDropPercentage * 100 * marketSensitivity) / 100;
        if (decrease > homeoscore) {
            homeoscore = 0;
        } else {
            homeoscore -= decrease;
        }
        emit MarketEvent(marketDropPercentage, decrease, homeoscore);
        checkDeath();
    }

    function updateTraits(uint256 newMarketSensitivity, uint256 newFeedSensitivity) external onlyOwner onlyAlive {
        marketSensitivity = newMarketSensitivity;
        feedSensitivity = newFeedSensitivity;
        emit TraitsUpdated(newMarketSensitivity, newFeedSensitivity);
    }

    // Internal function to mark the organism as dead when terminal state is reached.
    function checkDeath() internal {
        if (homeoscore == 0 || homeoscore == 100) {
            isAlive = false;
            emit Death(homeoscore);
        }
    }

    // Optionally, after death, the owner could withdraw the contract balance.
    function withdraw() external onlyOwner {
        require(!isAlive, "Organism is still alive");
        payable(owner).transfer(address(this).balance);
    }
}
