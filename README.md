# Environment Creator

## Overview
The **Environment Creator** project is a tool designed to facilitate the creation and management of custom environments for reinforcement learning (RL). It integrates SQL-based data storage and retrieval for environment definitions, making it suitable for tasks requiring dynamic state-action-reward configurations.

---

## Features
- **Environment Configuration:** Define RL environments using SQL tables for states, actions, and rewards.
- **Database Integration:** Store and manage environment data in an SQLite database (`environment_data.db`).
- **Modular Design:** Organized into separate modules for configuration, database interaction, and interface.
- **RL Algorithm Compatibility:** Compatible with Q-learning, SARSA, and other RL algorithms.

---

## Project Structure
```
EnvironmentCreator/
├── config/              # Configuration files or scripts
├── database/            # Database-related files or scripts
├── environment/         # Environment-related modules
├── environment_data.db  # SQLite database file
├── interface/           # User interface-related files
├── just.py              # Additional script
├── main.py              # Main entry point of the application
├── requirements.txt     # Dependencies for the project
├── view_database.py     # Script for viewing database contents
```

---

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Required libraries (see `requirements.txt`):
  - `numpy`
  - `pandas`
  - `sqlalchemy`
  - Additional dependencies for UI or database management

Install dependencies using:
```bash
pip install -r requirements.txt
```

### Setting Up the Project
1. Clone the repository:
   ```bash
   git clone https://github.com/Grigoryan-David/RL_Environment_Creator.git
   ```
2. Navigate to the project directory:
   ```bash
   cd EnvironmentCreator
   ```
3. Set up the SQLite database if not already initialized:
   ```bash
   python view_database.py
   ```

### Running the Application
Start the application by running:
```bash
python main.py
```

---

## Modules

### 1. `config/`
Contains configuration scripts and settings for environment initialization.

### 2. `database/`
Includes scripts to interact with and manage the SQLite database.

### 3. `environment/`
Houses the core logic for RL environment creation and interaction.

### 4. `interface/`
Handles user interface components, if applicable.

### 5. `main.py`
The main entry point of the application. It ties together the configuration, database, and environment modules.

### 6. `view_database.py`
Utility script to view and debug the contents of the database.


## Contributing
Contributions are welcome! Submit a pull request or open an issue to report bugs or suggest new features.


