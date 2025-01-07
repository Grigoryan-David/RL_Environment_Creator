import numpy as np
import random

from config.config import DEFAULT_CONFIG


class QLearningAgent:
    def __init__(self, state_space_size, action_space_size=len(DEFAULT_CONFIG['action_space']), learning_rate=0.2, gamma=0.9, epsilon=1, decay_rate=0.001):
        self.q_table = np.zeros((state_space_size, action_space_size))
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.decay_rate = decay_rate
        self.max_epsilon = 1
        self.min_epsilon = 0.01

    def train(self, env, total_episodes=None, max_steps_per_episode=None):
        """
        Train the Q-learning agent in the given environment.
        """
        if total_episodes is None:
            total_episodes = int((env.board_size[0]*env.board_size[1])/16*1000)  # +env.board_size[0]/4*1000)
        if max_steps_per_episode is None:
            max_steps_per_episode = env.board_size[0]*env.board_size[1]
        # Reset the Q-table for a new environment
        self.q_table = np.zeros_like(self.q_table)
        current_state = env.reset()
        for episode in range(total_episodes):
            state = env.reset()
            # current_position = 0
            for step in range(max_steps_per_episode):
                if random.uniform(0, 1) > self.epsilon:
                    action_index = np.argmax(self.q_table[state, :])  # Best action from Q-table
                else:
                    action_index = random.randint(0, len(env.action_space) - 1)  # Random action

                action = env.action_space[action_index]  # Map action index to action string

                next_state, reward, done = env.step(action)
                # current_position = env._state_to_index(next_state)

                # Update Q-value
                self.q_table[state, action_index] += self.learning_rate * (
                        reward + self.gamma * np.max(self.q_table[next_state, :]) - self.q_table[state, action_index]
                )

                if done:
                    break

                state = next_state

            # Decay epsilon after each episode
            self.epsilon = max(
                self.min_epsilon,
                self.max_epsilon * np.exp(-self.decay_rate * episode)
            )

    def select_action(self, state):
        """
        Select the best action for a given state based on the Q-table.
        """
        return np.argmax(self.q_table[state, :])
