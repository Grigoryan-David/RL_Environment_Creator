import sqlite3


conn = sqlite3.connect('environment_data.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM environments")
environments = cursor.fetchall()
print("Environments Table:")
for env in environments:
    print(env)
print()
cursor.execute("SELECT id, username FROM users")
users = cursor.fetchall()
print("Users Table:")
for user in users:
    print(user)
conn.close()
