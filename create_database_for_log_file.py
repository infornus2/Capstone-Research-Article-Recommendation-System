import sqlite3

conn = sqlite3.connect('user.db')
cursor = conn.cursor()

# Create a users table with an additional column to store selected domain names
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        domain TEXT
    )
''')

cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_interests (user_id INTEGER , paper_id INTEGER, activity_type REAL, login INTEGER)
            ''')

cursor.execute("SELECT paper_id,activity_type FROM user_interests WHERE user_id='1'")
paper = cursor.fetchall()
print(paper)

#print(sum(item[1] for item in paper))
#print(paper)
#print(type(paper[0][0]))

#conn.commit()
conn.close()
