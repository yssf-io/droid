"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import type { NextPage } from "next";
import { parseEther } from "viem";
import { useAccount, useContractRead, useReadContract, useWatchContractEvent, useWriteContract } from "wagmi";
import { BugAntIcon, MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import { Address } from "~~/components/scaffold-eth";
import { useAllContracts } from "~~/utils/scaffold-eth/contractsData";

const Home: NextPage = () => {
  const { address: connectedAddress } = useAccount();
  const contractsData = useAllContracts();
  const [homeoscore, setHomeoscore] = useState(0);
  const [feedSens, setFeedSens] = useState(0);
  const [marketSens, setMarketSens] = useState(0);
  const { data, refetch } = useReadContract({
    address: contractsData.Organism.address,
    abi: contractsData.Organism.abi,
    functionName: "homeoscore",
  });
  const { data: feedS } = useReadContract({
    address: contractsData.Organism.address,
    abi: contractsData.Organism.abi,
    functionName: "feedSensitivity",
  });
  const { data: marketS } = useReadContract({
    address: contractsData.Organism.address,
    abi: contractsData.Organism.abi,
    functionName: "marketSensitivity",
  });
  const { writeContract } = useWriteContract();
  useWatchContractEvent({
    address: contractsData.Organism.address,
    abi: contractsData.Organism.abi,
    eventName: "Fed",
    onLogs(logs) {
      console.log("fed", logs);
      refetch();
    },
  });

  const handleFeed = () =>
    writeContract({
      address: contractsData.Organism.address,
      abi: contractsData.Organism.abi,
      functionName: "feed",
      value: parseEther("0.001"),
    });

  useEffect(() => {
    if (data) setHomeoscore(parseInt(data.toString()));
    if (feedS) setFeedSens(parseInt(feedS.toString()));
    if (marketS) setMarketSens(parseInt(marketS.toString()));
  }, [data, feedS, marketS]);

  const getDroidImg = () => {
    if (homeoscore === 0 || homeoscore === 100) return "rip.webp";
    if (homeoscore < 40) return "low.webp";
    else if (homeoscore > 60) return "high.webp";
    else return "healthy.webp";
  };

  return (
    <>
      <div className="flex items-center flex-col flex-grow pt-10">
        <div className="px-5 w-1/2">
          <h1 className="text-center mb-8">
            <span className="block text-2xl mb-2">BioDroid</span>
          </h1>
          <p className="text-center">This is a first demo of the BioDroid project!</p>
          <p className="text-justify">
            The goal is to simulate a living organism onchain. It's a smart contract with properties like the
            "homeoscore" for now, and rules that dictate how the properties change. In that simple example, we have two
            rules. One that makes the homeoscore go down when the ETH price drops, and one that makes the homeoscore go
            up when someone feeds ETH to the biodroid. However these rules are scaled by evolving traits, one is "market
            sensitivity" (how much a drop in price affects the biodroid) and another is "feed sensitivity" (how much one
            finney, or 0.001 ETH, affects the biodroid).
          </p>
          <p className="text-justify">
            What makes these traits evolve is a Reinforcement Learning Agent running offchain and carrying the private
            key to update these traits. It is like the "brain" of the biodroid. However, this agent runs the model
            directly onchain, meaning that each episode is an actual update that gets reflected on the biodroid's smart
            contract.
          </p>
          <p className="text-justify">
            We can almost think of the smart contract as the body of the biodroid, the chain its environment and the
            agent its brain.
          </p>
          <div className="border border-gray-400"></div>
          <p className="text-justify">
            For this demo, only one biodroid (the one below) has been deployed, you can see its homeoscore. For now we
            consider that a healthy score is between 40 and 60. Below that the biodroid is tired and needs to be fed
            while above that it becomes overfed and needs less feeding and more drops in price. At 0 or 100, it dies.
          </p>
          <p className="text-justify">
            Each state will be reflected by a picture below as it's just a simple demo, but we could imagine having a
            live animated biodroid.
          </p>
          <p className="text-2xl font-bold w-full text-center">Homeoscore: {homeoscore}</p>
          <div className="w-full text-center">
            <button
              onClick={homeoscore > 60 ? () => {} : handleFeed}
              disabled={homeoscore > 60}
              className="text-center mb-4 border rounded-lg px-3 py-2 bg-blue-400 hover:bg-blue-400/80 w-fit text-white"
            >
              {homeoscore > 60 ? "feeding unnecessary" : "Feed me!"}
            </button>
          </div>
          <img src={getDroidImg()} alt="a healthy biodroid" width="50%" className="m-auto rounded-xl" />

          <p className="text-lg w-full text-center">
            Market Sensitivity: {marketSens} | Feed Sensitivity: {feedSens}
          </p>
        </div>
      </div>
    </>
  );
};

export default Home;
