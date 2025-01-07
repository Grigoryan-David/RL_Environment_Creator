import ast
import time

from config.config import DEFAULT_CONFIG
from environment.agent import QLearningAgent
from environment.rl_environment import Environment


class ConsoleInterface:
    def __init__(self, db_manager, username):
        self.db_manager = db_manager
        self.username = username

    def run(self):
        while True:
            print("\n1. Create New Environment")
            print("2. Run Test Simulation")
            print("3. My Environments")
            print("4. Exit")
            choice = input("Select an option: ")
            if choice == "1":
                self.create_environment()
            elif choice == "2":
                self.run_test_simulation()
            elif choice == "3":
                self.view_history()
            elif choice == "4":
                break

    @staticmethod
    def get_input(default_value: int | tuple, value_type, prompt=None) -> int | tuple:
        """Helper function to get user input with validation and default handling."""
        while True:
            if prompt is None:
                prompt = "Please enter a valid input: "
            user_input = input(f"{prompt}(default: {default_value}): ")
            if user_input == "":
                print(default_value)
                return default_value
            try:
                if value_type == tuple:
                    return value_type(map(int, user_input.split()))
                elif value_type == int:
                    return int(user_input)
            except ValueError:
                print(f"Invalid input. Please enter a valid {value_type.__name__}.")

    def create_environment(self):
        print("Create a New Environment")

        while True:
            board_size: tuple = self.get_input(prompt="Enter board size (e.g., 10 10)",
                                               default_value=DEFAULT_CONFIG['board_size'], value_type=tuple)
            obstacle_count: int = self.get_input(prompt="Enter number of obstacles",
                                                 default_value=DEFAULT_CONFIG['obstacle_count'], value_type=int)
            start: tuple = self.get_input(prompt="Enter start point (e.g., 0 0)",
                                          default_value=DEFAULT_CONFIG['start'], value_type=tuple)
            end: tuple = self.get_input(prompt=f"Enter end point (e.g., {board_size[0] - 1} {board_size[1] - 1})",
                                        default_value=(board_size[0] - 1, board_size[1] - 1), value_type=tuple)
            # obstacles = self.get_input(prompt=f"Enter obstacle positions (e.g. [0 2] [3 1])",
            # default_value=None, value_type=tuple)
            rewards = DEFAULT_CONFIG['rewards']
            action_space = DEFAULT_CONFIG['action_space']
            # extra_actions = input("Enter extra possible actions except [up, down, left, right] "
            #                        "(possible actions to be added: jump diagonal): ").split()
            # action_space.extend([f"{extra} {action}" for action in action_space for extra in extra_actions])
            env_data = {
                "board_size": board_size,
                "obstacle_count": obstacle_count,
                "start": start,
                "end": end,
                "rewards": rewards,
                "action_space": action_space
            }

            env = Environment(board_size=env_data["board_size"], obstacle_count=env_data["obstacle_count"],
                              start=env_data["start"], end=env_data["end"],
                              rewards=env_data["rewards"], action_space=env_data["action_space"])

            validation_error, invalid_variable = env.validate()
            if validation_error:
                print(validation_error)
                print()
                user_input = input(f"Do you want to re-enter the parameter for '{invalid_variable}' "
                                   f"or reset the environment? (click Enter to continue or type 'reset'): ")
                if not user_input:
                    if invalid_variable == "obstacle_count":
                        env_data[invalid_variable] = self.get_input(default_value=DEFAULT_CONFIG[invalid_variable],
                                                                    value_type=int)
                    else:
                        env_data[invalid_variable] = self.get_input(default_value=DEFAULT_CONFIG[invalid_variable],
                                                                    value_type=tuple)
                else:
                    continue

            self.db_manager.store_environment(env, self.username)
            print("Environment created and stored in the database:")
            print(env)
            break

    @staticmethod
    def _show_results(env, index=0):
        try:
            print(
                f"{index + 1}: "
                f"Creator: {env[1]}, "
                f"Board Size: {env[2]}, "
                f"Obstacles: {env[3]}, "
                f"Start: {env[5]}, "
                f"End: {env[6]} ")
        except IndexError:
            print(
                f"{index + 1}: "
                f"Creator: {env[1]}, "
                f"Board Size: {env[2]}, "
                f"Obstacles: {env[3]}, "
                f"Start: {env[4]}, "
                f"End: {env[5]} ")

    def run_test_simulation(self):
        """
        Allow the user to pick an environment and run the Q-Learning agent on it after training.
        """
        print("Retrieving environments...")
        environments = self.db_manager.get_user_environments(self.username)

        if not environments:
            print("You do not have any environments created yet. Please create one first.")
            return

        # Display environments
        print("Available Environments:")
        for index, env in enumerate(environments):
            try:
                print(
                    f"{index + 1}: Board Size: {env[2]}, Obstacles: {env[4]}, Start: {env[5]}, End: {env[6]}, Number of wins: {env[8]}"
                )
            except Exception as e:
                print(f"Error displaying environment {index + 1}: {e}")
                continue

        # Prompt user for selection
        try:
            selected_index = int(input("Select an environment to test (enter number): ")) - 1

            if 0 <= selected_index < len(environments):
                selected_env = environments[selected_index]
                environment_id = selected_env[0]  # Correct environment ID from the database

                # Safely parse the obstacles
                try:
                    obstacles = selected_env[4]
                    if isinstance(obstacles, str):
                        obstacles = ast.literal_eval(obstacles)
                    if not isinstance(obstacles, (set, list, tuple)):
                        raise ValueError("Parsed obstacles are not in a valid format.")
                except (ValueError, SyntaxError) as e:
                    print(f"Error parsing obstacles: {e}")
                    return

                # print("Board size: ", tuple(map(int, selected_env[2].strip("()").split(","))))
                # print("Obstacles: ", obstacles)
                # print("start: ", tuple(map(int, selected_env[5].strip("()").split(","))))
                # print("end: ", tuple(map(int, selected_env[6].strip("()").split(","))))

                # Initialize the selected environment
                try:
                    env = Environment(
                        board_size=tuple(map(int, selected_env[2].strip("()").split(","))),
                        obstacle_count=len(obstacles),
                        start=tuple(map(int, selected_env[5].strip("()").split(","))),
                        end=tuple(map(int, selected_env[6].strip("()").split(","))),
                        obstacles=obstacles,
                    )
                except Exception as e:
                    print(f"Error initializing the environment: {e}")
                    return

                # Initialize the Q-Learning agent
                state_space_size = env.board_size[0] * env.board_size[1]
                print(f"State space size: {state_space_size}")
                action_space_size = len(env.action_space)
                print(f"Action space size: {action_space_size}")
                agent = QLearningAgent(state_space_size, action_space_size)

                # Train the agent silently
                print(f"Training the agent on environment ID {environment_id}...")
                agent.train(env)
                print("Training complete.")
                print(agent)
                # Run the test simulation
                print(f"Running test simulation on the selected environment with ID {environment_id}...\n")
                env.test_run(agent)

            else:
                print("Invalid selection. Please select a number from the list.")
        except ValueError as e:
            print(f"Invalid input. Please enter a valid number. {e}")

    def view_history(self):
        print("Displaying your custom environments...")
        results = self.db_manager.get_user_history(self.username)
        if results:
            for idx, result in enumerate(results):
                self._show_results(index=idx, env=result)
