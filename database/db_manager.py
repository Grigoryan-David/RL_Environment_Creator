import sqlite3
import bcrypt


class DatabaseManager:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name, timeout=120)
        self._create_tables()

    def _create_tables(self):
        with self.connection:
            self.connection.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password BLOB,  -- Change password type to BLOB for binary data
                env_num INTEGER DEFAULT 0
            );""")
            self.connection.execute("""CREATE TABLE IF NOT EXISTS environments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        board_size TEXT,
                        obstacle_count INTEGER,
                        obstacle_position TEXT,
                        start TEXT,
                        end TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );""")
            self.connection.execute("""CREATE TABLE IF NOT EXISTS results (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    board_id INTEGER,
                                    actions_taken INTEGER,
                                    reward INTEGER DEFAULT 0,
                                    player_username TEXT,                                    
                                    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    FOREIGN KEY (board_id) REFERENCES environments (id) ON DELETE CASCADE
                                );""")

    def username_exists(self, username):
        cursor = self.connection.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        return cursor.fetchone() is not None

    def add_user(self, username, password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        with self.connection:
            self.connection.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                                    (username, hashed_password))

    def verify_password(self, username, password):
        cursor = self.connection.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            stored_password_hash = row[0]  # This should be bytes if stored as BLOB
            # Compare the plaintext password with the stored hash directly
            if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash):
                return True
        return False

    def store_environment(self, env, username):
        # Use the username to create a unique table for the user's environments
        with self.connection:
            self.connection.execute(f"INSERT INTO environments (username, board_size, obstacle_count, obstacle_position, start, end) VALUES (?, ?, ?, ?, ?, ?)",
                                    (username, str(env.board_size), env.obstacle_count, str(env.obstacles), str(env.start), str(env.end)))
            self.connection.execute("UPDATE users SET env_num = env_num + 1 WHERE username = ?;", (username,))

    def get_user_environments(self, username) -> list[tuple]:
        """
        Retrieve environments with an option for all or only the user's environments.
        """
        cursor = self.connection.cursor()

        while True:
            user_input = input("Do you want to retrieve all environments? (y/n): ").strip().lower()
            if user_input in ['y', 'n', '']:
                break
            print("Invalid input. Please enter 'y' for all environments or 'n' for only your environments.")

        try:
            if user_input == 'y' or user_input == '':
                # Fetch all environments
                query = """
                SELECT 
                    e.id AS environment_id,
                    e.username AS creator,
                    e.board_size,
                    e.obstacle_count,
                    e.obstacle_position,
                    e.start,
                    e.end,
                    e.created_at,
                    (SELECT COUNT(*) FROM results r WHERE r.board_id = e.id) AS play_count
                FROM environments e
                ORDER BY e.created_at DESC
                """
                cursor.execute(query)
            else:
                # Fetch only the user's environments
                query = """
                SELECT 
                    e.id AS environment_id,
                    e.username AS creator,
                    e.board_size,
                    e.obstacle_count,
                    e.obstacle_position,
                    e.start,
                    e.end,
                    e.created_at,
                    (SELECT COUNT(*) FROM results r WHERE r.board_id = e.id) AS play_count
                FROM environments e
                WHERE e.username = ?
                ORDER BY e.created_at DESC
                """
                cursor.execute(query, (username,))

            environments = cursor.fetchall()

            if not environments:
                print("No environments found.")
                return []

            return environments
        except sqlite3.OperationalError as e:
            print(f"Database error occurred: {e}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return []

    def get_user_history(self, username) -> list:
        """
        Retrieve detailed play history for environments created by the user.
        Handles NULL values gracefully by using COALESCE.
        """
        cursor = self.connection.cursor()
        try:
            query = """
            SELECT 
                e.id AS environment_id, 
                e.username AS creator, 
                e.board_size, 
                e.obstacle_position,
                e.start, 
                e.end
            FROM environments e
            LEFT JOIN (
                SELECT 
                    r.board_id, 
                    COUNT(*) AS play_count  -- Count total plays per board_id
                FROM results r
                GROUP BY r.board_id
            ) play_data ON e.id = play_data.board_id
            WHERE e.username = ?
            ORDER BY e.id ASC
            """

            cursor.execute(query, (username,))
            return cursor.fetchall()
        except sqlite3.OperationalError as e:
            print(f"Error retrieving play history: {e}")
            return []

    def store_result(self, board_id, actions_taken, reward, player_username):
        with self.connection:
            self.connection.execute(
                "INSERT INTO results (board_id, actions_taken, reward, player_username) VALUES (?, ?, ?, ?)",
                (board_id, actions_taken, reward, player_username)
            )

    def get_results_for_user(self, username):
        """
        Retrieve all results for the user's environments, grouped by environment.
        """
        cursor = self.connection.cursor()
        query = """
        SELECT 
            r.board_id, e.board_size, e.start, e.end,
            COUNT(r.id) AS play_count, SUM(r.reward) AS total_reward
        FROM results r
        JOIN environments e ON r.board_id = e.id
        WHERE e.username = ?
        GROUP BY r.board_id
        ORDER BY e.created_at
        """
        cursor.execute(query, (username,))
        return cursor.fetchall()

    def clear(self):
        with self.connection:
            self.connection.execute("DELETE FROM users;")
            self.connection.execute("DELETE FROM environments;")

    def drop_all_tables(self):
        with self.connection:
            tables = ["environments", "users"]
            for table in tables:
                self.connection.execute(f"DROP TABLE IF EXISTS {table};")

    def close(self):
        """Close the database connection."""
        self.connection.close()

