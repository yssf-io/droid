import { expect } from "chai";
import { ethers } from "hardhat";
import { Organism } from "../typechain-types";
import { parseEther } from "ethers";

describe("Organism", function () {
  // We define a fixture to reuse the same setup in every test.

  let yourContract: Organism;
  before(async () => {
    const yourContractFactory = await ethers.getContractFactory("Organism");
    yourContract = (await yourContractFactory.deploy()) as Organism;
    await yourContract.waitForDeployment();
  });

  describe("Deployment", function () {
    it("Should have the right initial parameters", async function () {
      expect(await yourContract.homeoscore()).to.equal(50);
      expect(await yourContract.marketSensitivity()).to.equal(5);
      expect(await yourContract.feedSensitivity()).to.equal(5);
    });

    it("Should feed correctly", async function () {
      await yourContract.feed({ value: parseEther("0.001") });
      expect(await yourContract.homeoscore()).to.equal(55);
    });

    it("Should decrease correctly", async function () {
      await yourContract.updateMarketEvent(2);
      expect(await yourContract.homeoscore()).to.equal(45);
    });

    it("Should not decrease", async function () {
      const [_, addy2] = await ethers.getSigners();
      await expect(yourContract.connect(addy2).updateMarketEvent(2)).to.be.reverted;
    });

    it("Should rip", async function () {
      await yourContract.feed({ value: parseEther("1") });
      expect(await yourContract.isAlive()).to.equal(false);
    });

    it("Should not be able to feed", async function () {
      await expect(yourContract.feed({ value: parseEther("0.001") })).to.be.revertedWith("RIP");
    });
  });
});
