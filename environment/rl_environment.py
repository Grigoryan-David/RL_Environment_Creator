import random
import time

from colorama import Fore, Style


class Environment:
    def __init__(self, board_size: tuple, obstacle_count: int, start: tuple, end: tuple, obstacles=None,
                 rewards=None, action_space=None, termination_conditions=None):
        self.current_position = None
        self.board_size = board_size
        self.obstacle_count = obstacle_count
        self.start = start
        self.end = end
        self.obstacles = obstacles if obstacles is not None else self.generate_obstacles()
        self.rewards = rewards
        self.action_space = action_space if action_space is not None else ['up', 'down', 'left', 'right']
        self.termination_conditions = termination_conditions if termination_conditions is not None \
            else self.default_termination_conditions()

    def generate_obstacles(self) -> set:
        print(self.start, self.end)
        """Randomly generate obstacles on the board."""
        obstacles = set()
        while len(obstacles) < self.obstacle_count:
            x = random.randint(0, self.board_size[0] - 1)
            y = random.randint(0, self.board_size[1] - 1)
            while (x, y) == self.start or (x, y) == self.end:
                x = random.randint(0, self.board_size[0] - 1)
                y = random.randint(0, self.board_size[1] - 1)
            obstacles.add((x, y))
        return obstacles

    @staticmethod
    def default_termination_conditions() -> dict:
        """Define default termination conditions."""
        return {
            'goal_reached': False,
            'max_steps': 100  # Max steps before termination
        }

    def validate(self):
        """Validate parameters for consistency."""

        # Check if the start point is within bounds
        try:
            if not (0 <= self.start[0] < self.board_size[0] and 0 <= self.start[1] < self.board_size[1]):
                raise ValueError("Start point is out of bounds.")
        except ValueError as e:
            return f"ERROR! {e}", "start"

        # Check if the end point is within bounds
        try:
            if not (0 <= self.end[0] < self.board_size[0] and 0 <= self.end[1] < self.board_size[1]):
                raise ValueError("End point is out of bounds.")
        except ValueError as e:
            return f"ERROR! {e}", "end"

        # Check if start and end points are the same
        try:
            if self.start == self.end:
                raise ValueError("Start and end points cannot be the same.")
        except ValueError as e:
            return f"ERROR! {e}", "end"

        # Check if there are too many obstacles
        try:
            if self.obstacle_count >= (self.board_size[0] * self.board_size[1]) - 1:
                raise ValueError("Too many obstacles; there must be at least one empty space for a win option.")
        except ValueError as e:
            return f"ERROR! {e}", "obstacle_count"

        # Ensure the end point can be reached based on the number of obstacles
        try:
            empty_spaces = (self.board_size[0] * self.board_size[
                1]) - self.obstacle_count - 2  # Exclude start and end points
            if empty_spaces < sum(self.board_size) - 3:
                raise ValueError("There are not enough empty spaces for a valid path.")
        except ValueError as e:
            return f"ERROR! {e}", "empty_spaces"

        # try:
        #     first_items_equal = all(item[0] == next(iter(self.obstacles))[0] for item in self.obstacles)
        #     second_items_equal = all(item[1] == next(iter(self.obstacles))[1] for item in self.obstacles)
        #     if first_items_equal or second_items_equal:
        #         raise ValueError("Obstacles occupy all horizontal or vertical squares in line")
        # except ValueError as e:
        #     return f"ERROR! {e}", "obstacles"

        # Check if start and end points are not occupied by obstacles
        try:
            if self.obstacles.intersection({self.start, self.end}):
                raise ValueError("Obstacles cannot occupy the start or end points.")
        except ValueError as e:
            return f"ERROR! {e}", "end"

        return None, None  # No errors

    def __str__(self):
        print()
        return (f"The Created Environment Has:\n"
                f"size={self.board_size},\n"
                f"obstacles={self.obstacles},\n"
                f"start={self.start},\n"
                f"end={self.end},\n")

    def test_run(self, agent, delay=0.5):
        """
        Simulate a test run on the board with real-time movement visualization.
        """
        board = self.initialize_board()  # Initialize the static board
        print(board)
        current_position = self.start
        previous_position = None
        steps = 0
        state = self.state_to_index(current_position)  # Get initial state index

        print(f"Starting test run from {self.start} to {self.end}.\n")

        while steps < (self.board_size[0] * self.board_size[1]):
            # Update board visualization dynamically
            if steps > 0:  # Clear previous agent position unless it's the first step
                board[current_position[0]][current_position[1]] = 'O'

            # Agent selects an action based on current state
            action_index = agent.select_action(state)  # Select action from Q-table
            action = self.action_space[action_index]  # Map action index to action string

            # Calculate the next position
            next_position = self.take_action(current_position, action)

            self.display_board(board, steps, current_position, previous_position, last_action=action)

            # Print the action and movement for debugging
            print(f"Step {steps}: Action to do: {action}")
            print(f"Step {steps + 1}: Current Position: {current_position}, Next Position: {next_position}")

            # Check if the move is valid
            if self.is_valid_position(next_position, board):
                previous_position = current_position
                current_position = next_position  # Update position
                state = self.state_to_index(current_position)  # Update state index
                board[current_position[0]][current_position[1]] = 'H'  # Mark the new agent position
            else:
                print(
                    f"{Fore.RED}Step {steps + 1}: Hit an obstacle or invalid position at {next_position}. "
                    f"Staying at {current_position}.{Style.RESET_ALL}"
                )

            self.display_board(board, steps + 1, current_position, previous_position, last_action=action)

            # Check if the agent reached the goal
            if current_position == self.end:
                board[current_position[0]][current_position[1]] = 'H'  # Final position
                self.display_board(board, steps + 1, current_position, previous_position, last_action=action)
                print(f"{Fore.GREEN}Goal reached at {current_position} in {steps + 1} steps!{Style.RESET_ALL}")
                return steps + 1

            steps += 1
            time.sleep(delay)

        # Max steps reached without reaching the goal
        self.display_board(board, steps, current_position, previous_position, last_action=action)
        print(f"{Fore.RED}Max steps reached without reaching the goal.{Style.RESET_ALL}")
        return None

    def initialize_board(self):
        """
        Create a 2D board with obstacles and open spaces.
        """
        board = [['O' for _ in range(self.board_size[1])] for _ in range(self.board_size[0])]

        # Place obstacles
        for obstacle in self.obstacles:
            if 0 <= obstacle[0] < self.board_size[0] and 0 <= obstacle[1] < self.board_size[1]:
                board[obstacle[0]][obstacle[1]] = 'X'
            else:
                print(f"Warning: Obstacle at {obstacle} is out of bounds and will be ignored.")

        # Place start position
        if board[self.start[0]][self.start[1]] == 'X':
            raise ValueError(f"Start position {self.start} overlaps with an obstacle.")
        board[self.start[0]][self.start[1]] = 'H'

        # Place goal position
        if board[self.end[0]][self.end[1]] == 'X':
            raise ValueError(f"Goal position {self.end} overlaps with an obstacle.")
        board[self.end[0]][self.end[1]] = 'G'

        return board

    @staticmethod
    def display_board(board, step, agent_position, previous_position=None, visited_positions=None, last_action=None):
        """
        Display the board dynamically with visualization for every step.
        """
        if visited_positions is None:
            visited_positions = set()
        # Clear terminal
        print("\033[H\033[J", end="")

        print(f"{Fore.CYAN}Step {step}:{Style.RESET_ALL}")
        if last_action:
            print(f"Last Action: {Fore.MAGENTA}{last_action}{Style.RESET_ALL}")

        # Mark the previous position as visited
        if previous_position and previous_position != agent_position:
            visited_positions.add(previous_position)

        # Update the board
        for pos in visited_positions:
            board[pos[0]][pos[1]] = '*'

        # Mark the agent's current position
        board[agent_position[0]][agent_position[1]] = 'H'

        # Display the updated board
        print(f"{Fore.YELLOW}+" + ("-" * 5 * len(board[0])) + f"+{Style.RESET_ALL}")
        for row in board:
            row_display = "|"
            for cell in row:
                if cell == 'H':  # Agent
                    row_display += f"{Fore.GREEN}[ H ]{Style.RESET_ALL}"
                elif cell == 'G':  # Goal
                    row_display += f"{Fore.BLUE}[ G ]{Style.RESET_ALL}"
                elif cell == 'X':  # Obstacle
                    row_display += f"{Fore.RED}[ X ]{Style.RESET_ALL}"
                elif cell == '*':  # Previously visited
                    row_display += f"{Fore.BLUE}[ * ]{Style.RESET_ALL}"
                else:  # Open space
                    row_display += f"{Fore.WHITE}[   ]{Style.RESET_ALL}"
            row_display += "|"
            print(row_display)

        # Bottom border
        print(f"{Fore.YELLOW}+" + ("-" * 5 * len(board[0])) + f"+{Style.RESET_ALL}")

        print(f"Agent is at {Fore.GREEN}{agent_position}{Style.RESET_ALL}\n")

    @staticmethod
    def is_valid_position(position, board):
        """
        Check if the position is within bounds and not an obstacle.
        """
        rows = len(board)
        cols = len(board[0])
        if 0 <= position[0] < rows and 0 <= position[1] < cols:
            return board[position[0]][position[1]] != 'X'
        return False

    @staticmethod
    def take_action(position, action):
        if action == 'up':
            return position[0] - 1, position[1]
        elif action == 'down':
            return position[0] + 1, position[1]
        elif action == 'left':
            return position[0], position[1] - 1
        elif action == 'right':
            return position[0], position[1] + 1
        # elif action == 'jump':
        #     return position[0], position[1] + 2
        # elif action == 'diagonal':
        #     return position[0] + 1, position[1] + 1
        return position  # Return the same position if action is invalid

    def reset(self):
        """
        Reset the environment to the initial state.
        """
        self.current_position = self.start
        return self.state_to_index(self.current_position)  # Return the initial state as index

    def step(self, action):
        """
        Take an action in the environment and return (next_state, reward, done).
        """
        next_position = self.take_action(self.current_position, action)

        # Check if the next position is out of bounds
        if not self._is_in_bounds(next_position):
            return self.state_to_index(self.current_position), -1, False  # Penalty for invalid move

        # Check if the next position is an obstacle
        if next_position in self.obstacles:
            self.current_position = self.start  # Reset position to the start
            return self.state_to_index(self.current_position), -1, False  # Penalty and restart

        # Check if the goal is reached
        if next_position == self.end:
            self.current_position = next_position  # Update position
            return self.state_to_index(next_position), 1, True  # Reward for reaching goal

        # Normal move
        self.current_position = next_position
        return self.state_to_index(next_position), 0, False  # No reward for normal moves

    # Normal transition

    def state_to_index(self, position):
        """
        Convert a (row, col) position into a unique state index for Q-learning.
        """
        return position[0] * self.board_size[1] + position[1]

    def _is_in_bounds(self, position):
        """
        Check if the given position is within the board bounds.
        """
        return 0 <= position[0] < self.board_size[0] and 0 <= position[1] < self.board_size[1]
