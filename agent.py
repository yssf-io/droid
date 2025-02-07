import random
import time
import numpy as np
import csv


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

# TODO: get these values from the chain
# Initial trait values.
market_sensitivity = 5  # Determines the impact of market drops.
feed_sensitivity = 5  # Determines the impact of feeding.

returns = get_hourly_returns("ETH_1H.csv")
returns.reverse()
return_index = 0
negative = 0


# --- Environment Simulation ---
def discretize_state(health):
    """Discretize health into buckets (0-10, 10-20, ..., 90-100)."""
    return int(health // 10)


def simulate_environment(health, market_sens, feed_sens):
    """
    Simulate one time step.
    - Feed event: a random positive effect, scaled by feed_sensitivity.
    - Market drop: a random negative event, scaled by market_sensitivity.
    """
    # TODO: dynamically get these values
    feed = random.uniform(0, 10)  # Feed increases health.
    global return_index
    global negative
    # Use the next hourly return from the CSV data
    if return_index >= len(returns):
        return_index = 0  # cycle back if we run out
    market_drop = returns[return_index]
    return_index += 1

    if market_drop > 0:
        market_drop = 0
    else:
        negative += 1
        market_drop = abs(market_drop)

    # Adjust the impact:
    # For feed, higher feed_sens means a stronger positive effect.
    # For market, higher market_sens means a stronger negative effect.
    new_health = health + (feed * feed_sens / 10) - (market_drop * market_sens / 10)
    return max(0, min(100, new_health))  # Clamp health between 0 and 100.


def compute_reward(health):
    """
    Reward function: +10 if health is in [40,60], else negative penalty
    proportional to distance from 50.
    """
    if 45 <= health <= 55:
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


# --- Live RL Loop ---
# Starting organism health.
current_health = 50.0

# For now we are testing with a number of episodes, in production it will be an infinite loop
# In a live scenario, each loop represents one decision cycle (e.g., hourly).
num_episodes = 10000
for i in range(num_episodes):
    # 1. Read the current state (simulate on-chain health)
    state = discretize_state(current_health)

    # 2. Choose an action: a composite adjustment (delta_market, delta_feed)
    action_idx = choose_action(state)
    delta_market, delta_feed = ACTION_DELTAS[action_idx]

    # 3. Apply the action: update both traits.
    market_sensitivity = max(1, min(20, market_sensitivity + delta_market))
    feed_sensitivity = max(1, min(20, feed_sensitivity + delta_feed))

    # 4. Simulate the environment with updated traits.
    new_health = simulate_environment(
        current_health, market_sensitivity, feed_sensitivity
    )

    # 5. Compute the reward.
    reward = compute_reward(new_health)

    # 6. Discretize new state and update the Q-table.
    next_state = discretize_state(new_health)
    update_Q(state, action_idx, reward, next_state)

    # 7. Log the decision cycle.
    print(
        f"Health: {current_health:.1f} -> {new_health:.1f} | "
        f"Market Sens: {market_sensitivity} | Feed Sens: {feed_sensitivity} | "
        f"Action: ({delta_market}, {delta_feed}) | Reward: {reward:.2f}"
    )

    # 8. Set new health for next iteration.
    current_health = new_health

    # 9. Wait until next decision cycle (e.g., one hour; for testing, shorten this interval)
    time.sleep(0.001)
print(negative)
