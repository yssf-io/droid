# droid

The goal is to simulate a living organism onchain. It's a smart contract with properties like the "homeoscore" for now, and rules that dictate how the properties change. In that simple example, we have two rules. One that makes the homeoscore go down when the ETH price drops, and one that makes the homeoscore go up when someone feeds ETH to the biodroid.

However these rules are scaled by evolving traits, one is "market sensitivity" (how much a drop in price affects the biodroid) and another is "feed sensitivity" (how much one finney, or 0.001 ETH, affects the biodroid).

At every interval (like an hour), the AI agent (powered by reinforcement learning) updates the traits, kind of emulating or giving the impression of life. The agent decides how to update with the goal of staying in a healthy homeoscore range (of 40-60 in our example).

In essence the AI agent is essentially the “brain” of biodroid. It continuously monitors the organism’s state—its “homeoscore,” which reflects its overall balance—and learns, through trial and error, how to adjust key parameters (like market and feed sensitivity) so that the biodroid remains in an optimal, healthy range. In other words, based on each outcome (whether biodroid becomes too low or too high), the agent tweaks its settings to better respond to unpredictable market events and user feeds. Over time, it develops a strategy that helps the organism adapt to its environment, much like a living creature learning to survive.

### Technical

This project is divided into three parts: the AI agent, the frontend and the smart contract.

The smart contract is a simple contract holding three things:

- properties (just the "homeoscore" in that first demo) -> what is affected by the environment
- rules (two in the first demo, describing how the homeoscore increases/decreases) -> how the environment affects the properties
- traits (also two, one for each rule) -> regulating how much the rules affect the properties
  These three concepts together define our onchain living organism and how it reacts to its environment (the chain itself).
  The two rules and traits are simple for this demo:
- when the ETH price drops, it reduces the homeoscore, and the related trait is "market sensitivity" (the higher it is, the bigger the reduction in homeoscore will be when market drops)
- when someone feeds 0.001 ETH (1 finney), it increases the homeoscore, and the related trait is "feed sensitivity" (the higher it is, the bigger the increase in homeoscore will be when fed)

The AI agent is a Python script which has the power to update the traits. The agent is very similar to a Reinforcement Learning (RL) agent, in that it will observe how the market and feeding affect the homeoscore and will update (at every interval, like an hour) the traits to keep the biodroid in a healthy range of 40-60. Below 40 we consider the biodroid tired while above 60 we consider it overfed, both are bad and command a negative reward for the RL agent. We can make the hypothesis that the RL agent, over time, will know when to increase or decrease the two traits (market and feed sensitivities). The only difference between our agent and a normal RL agent is that we are not iterating over a lot of episodes quickly, instead each episode is a real-time interval happening onchain. The goal of that to emulate (maybe even simulate) organic life onchain.
On the technical side, our off-chain RL agent continuously observes the biodroid's discretized homeoscore, selects traits adjustments (for market and feed sensitivities) using an epsilon-greedy Q-learning policy, and updates its Q-values based on a reward function that measures deviation from an optimal balance, thereby learning an adaptive strategy to maximize long-term survival under unpredictable onchain conditions.

The frontend uses scaffold (nextjs, tailwind, viem, ...) to simply explain the project, display images of the biodroid (in the future it will be a live animation) depending on its homeoscore (looking healthy when in the correct range, or tired/overfed when outside, and dead/deactivated when at 0 or a 100) and has a "Feed Me!" button to send it one finney. I would also like to add all the evolution that the agent has chosen (although it can be just seen on the chain).
