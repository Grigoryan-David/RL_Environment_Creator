import msvcrt
import os

from interface.console_interface import ConsoleInterface
from database.db_manager import DatabaseManager


def main():
    def password_input(prompt="Enter your password: "):
        password = ""
        if os.name == 'nt':  # Windows
            print(prompt, end="", flush=True)
            while True:
                char = msvcrt.getch()
                if char == b'\r' and len(password) > 4:  # Enter key
                    break
                elif char == b'\x08':  # Backspace key
                    if len(password) > 0:
                        password = password[:-1]
                        print("\b \b", end="", flush=True)
                else:
                    password += char.decode("utf-8")
                    print("*", end="", flush=True)
        print()
        return password

    db_manager = DatabaseManager("environment_data.db")
    # db_manager.drop_all_tables()
    check = True
    while check:
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Select an option: ")
        max_attempts = 3
        if choice == "1":
            while True:
                username = input("Enter username: ")
                if db_manager.username_exists(username):
                    print("Username already exists. Please choose a different username.")
                else:
                    password = password_input()
                    db_manager.add_user(username, password)
                    print("Registration successful!")
                    interface = ConsoleInterface(db_manager, username)
                    interface.run()
                    check = False
                    break
        elif choice == "2":
            attempts = 0
            while attempts < max_attempts:
                username = input("Enter username: ")
                if not db_manager.username_exists(username):
                    print("Username does not exist.")
                    attempts += 1
                    continue
                password = password_input(prompt="Enter password: ")
                if db_manager.verify_password(username, password):
                    print("Login successful!")
                    interface = ConsoleInterface(db_manager, username)
                    interface.run()
                    check = False
                    break
                else:
                    attempts += 1
                    print("Invalid username or password.")
                    if attempts == max_attempts:
                        print("Maximum login attempts exceeded. Please try again later.")
                        check = False
                        break
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")

    db_manager.close()


if __name__ == "__main__":
    main()
