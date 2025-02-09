"use client";

import Link from "next/link";
import type { NextPage } from "next";
import { useAccount } from "wagmi";
import { BugAntIcon, MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import { Address } from "~~/components/scaffold-eth";

const Home: NextPage = () => {
  const { address: connectedAddress } = useAccount();

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

          <img src="healthy.webp" alt="a healthy biodroid" width="50%" className="m-auto rounded-xl" />
          <p>Feed me!</p>
        </div>
      </div>
    </>
  );
};

export default Home;
