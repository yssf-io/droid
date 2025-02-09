import random
import time
import csv
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3eth = Web3(
    Web3.HTTPProvider(
        "https://eth-mainnet.g.alchemy.com/v2/4HvmaqDcH1O3ZNkHhtFZA5ydU2rgV9Sl"
    )
)

address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
abi = '[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"finalHomeoscore","type":"uint256"}],"name":"Death","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"newHomeoscore","type":"uint256"}],"name":"Fed","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"marketDropPercentage","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"decreaseAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"newHomeoscore","type":"uint256"}],"name":"MarketEvent","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"newMarketSensitivity","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"newFeedSensitivity","type":"uint256"}],"name":"TraitsUpdated","type":"event"},{"inputs":[],"name":"feed","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"feedSensitivity","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"homeoscore","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"isAlive","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"marketSensitivity","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"marketDropPercentage","type":"uint256"}],"name":"updateMarketEvent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"newMarketSensitivity","type":"uint256"},{"internalType":"uint256","name":"newFeedSensitivity","type":"uint256"}],"name":"updateTraits","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"}]'

eth_feed_address = "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419"
eth_feed_abi = '[{"inputs":[],"name":"latestAnswer","outputs":[{"internalType":"int256","name":"","type":"int256"}],"stateMutability":"view","type":"function"}]'

biodroid = w3.eth.contract(address=address, abi=abi)
eth_feed = w3eth.eth.contract(address=eth_feed_address, abi=eth_feed_abi)


def get_hourly_returns(csv_filename):
    returns = []
    with open(csv_filename, "r") as csvfile:
        reader = csv.reader(csvfile)
        # Skip header if one exists:
        header = next(reader)
        # Read all lines (each representing one hour)
        lines = list(reader)
        # Compute returns for each adjacent pair
        for i in range(len(lines) - 1):
            current_close = float(lines[i][6])  # column index 6 is Close
            previous_close = float(lines[i + 1][6])
            # Calculate the percentage return:
            ret = (current_close - previous_close) / previous_close * 100
            # # If there's an increase, set drop to 0; if a drop, take absolute value.
            # if ret > 0:
            #     ret = 0
            # else:
            #     ret = abs(ret)
            returns.append(ret)
    return returns


# This RL agent will serve as the "brain" of our smart contract based organism.
# It will emulate a kind of "organic life" by changing the organism's traits according
# to environmental changes, both market going down and users feeding it.

# --- RL Setup ---
# Now our actions are composite: each action is (delta_market, delta_feed)
# For example, (-1, 0) means reduce market sensitivity by 1, leave feed sensitivity unchanged.
ACTION_DELTAS = [(dm, df) for dm in [-1, 0, 1] for df in [-1, 0, 1]]
# Total of 9 actions.

# Q-table: maps discretized state (health bucket) to list of Q-values (one for each composite action).
Q = {}

ALPHA = 0.1  # Learning rate
GAMMA = 0.9  # Discount factor
EPSILON = 0.1  # Exploration probability

# Initial trait values.
market_sensitivity = (
    biodroid.functions.marketSensitivity().call()
)  # Determines the impact of market drops.
feed_sensitivity = (
    biodroid.functions.feedSensitivity().call()
)  # Determines the impact of feeding.

returns = get_hourly_returns("ETH_1H.csv")
returns.reverse()
return_index = 0
negative = 0


# --- Environment Simulation ---
def discretize_state(health):
    """Discretize health into buckets (0-10, 10-20, ..., 90-100)."""
    return int(health // 10)


def simulate_environment():
    """
    Simulate one time step.
    Unlike normal RL simulation, we directly update the chain
    """
    # Process market drop if there is one
    current_price = eth_feed.functions.latestAnswer().call() / 1e8
    price_last_interval = (
        eth_feed.functions.latestAnswer().call(block_identifier=-300) / 1e8
    )
    last_hour_return = (current_price - price_last_interval) / price_last_interval * 100
    if last_hour_return < 0:
        tx = biodroid.functions.updateMarketEvent(abs(last_hour_return)).transact()
        print(tx)
        time.sleep(5)

    homeoscore = biodroid.functions.homeoscore().call()

    # Return the impact of the last interval:
    return max(0, min(100, homeoscore))  # Clamp health between 0 and 100.


def compute_reward(health):
    """
    Reward function: +10 if health is in [40,60], else negative penalty
    proportional to distance from 50.
    """
    if 40 <= health <= 60:
        return 10
    else:
        return -abs(health - 50) / 2


def choose_action(state):
    if state not in Q:
        Q[state] = [0.0 for _ in ACTION_DELTAS]
    if random.random() < EPSILON:
        return random.randint(0, len(ACTION_DELTAS) - 1)
    else:
        max_value = max(Q[state])
        candidates = [i for i, value in enumerate(Q[state]) if value == max_value]
        return random.choice(candidates)


def update_Q(state, action, reward, next_state):
    if next_state not in Q:
        Q[next_state] = [0.0 for _ in ACTION_DELTAS]
    best_next = max(Q[next_state])
    Q[state][action] += ALPHA * (reward + GAMMA * best_next - Q[state][action])


def updateTraits(market_sensitivity, feed_sensitivity):
    """
    Update the traits onchain before next iteration.
    """
    tx = biodroid.functions.updateTraits(
        market_sensitivity, feed_sensitivity
    ).transact()
    print(tx)


# --- Live RL Loop ---
# Starting organism health.
current_health = biodroid.functions.homeoscore().call()

# In a live scenario, each loop represents one decision cycle (e.g., hourly).
while True:
    # 1. Read the current state (simulate on-chain health)
    state = discretize_state(current_health)

    # 2. Choose an action: a composite adjustment (delta_market, delta_feed)
    action_idx = choose_action(state)
    delta_market, delta_feed = ACTION_DELTAS[action_idx]

    # 3. Apply the action: update both traits.
    market_sensitivity = max(1, min(20, market_sensitivity + delta_market))
    feed_sensitivity = max(1, min(20, feed_sensitivity + delta_feed))

    # 4. Simulate the environment with updated traits.
    new_health = simulate_environment()

    # 5. Compute the reward.
    reward = compute_reward(new_health)

    # 6. Discretize new state and update the Q-table as well as onchain traits.
    next_state = discretize_state(new_health)
    update_Q(state, action_idx, reward, next_state)
    updateTraits(market_sensitivity, feed_sensitivity)

    # 7. Log the decision cycle.
    print(
        f"Health: {current_health:.1f} -> {new_health:.1f} | "
        f"Market Sens: {market_sensitivity} | Feed Sens: {feed_sensitivity} | "
        f"Action: ({delta_market}, {delta_feed}) | Reward: {reward:.2f}"
    )

    # 8. Set new health for next iteration.
    current_health = new_health

    # 9. Wait until next decision cycle (e.g., one hour; for testing, shorten this interval)
    time.sleep(3600)
