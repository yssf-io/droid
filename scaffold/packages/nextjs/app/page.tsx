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
        <div className="px-5">
          <h1 className="text-center mb-24">
            <span className="block text-2xl mb-2">BioDroid</span>
          </h1>

          <img src="healthy.webp" alt="a healthy biodroid" width="50%" className="m-auto rounded-xl" />
          <p>Feed me!</p>
        </div>
      </div>
    </>
  );
};

export default Home;
