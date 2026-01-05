import os
import psycopg2
from dotenv import load_dotenv

# 1. Load your secret Neon URL
load_dotenv()

# # 2. Connect to the Neon Database
# # This acts like "opening a terminal" to your database
# try:
#     conn = psycopg2.connect(os.getenv("DATABASE_URL"))
#     cursor = conn.cursor() # The 'cursor' is the tool used to execute commands
#     print("Connected to Database...")
# except Exception as e:
#     print("Connection Failed:", e)
#     exit()

# # 3. Define the SQL Commands
# # We use standard SQL. 
# # 'SERIAL' is the Postgres version of 'AUTO_INCREMENT'. 
# # 'TEXT' is used instead of 'VARCHAR' (Postgres handles TEXT very efficiently).

# sql_create_users = """
# CREATE TABLE IF NOT EXISTS users (
#     id SERIAL PRIMARY KEY,
#     full_name TEXT NOT NULL,
#     email TEXT UNIQUE NOT NULL,
#     password_hash TEXT NOT NULL
# );
# """

# sql_create_searches = """
# CREATE TABLE IF NOT EXISTS searches (
#     id SERIAL PRIMARY KEY,
#     user_id INTEGER REFERENCES users(id), -- This links to the users table
#     query TEXT NOT NULL,
#     last_sent_date TEXT
# );
# """

# # 4. Execute the Commands
# try:
#     cursor.execute(sql_create_users)
#     print("Users table created.")
    
#     cursor.execute(sql_create_searches)
#     print("Searches table created.")
    
#     # 5. Commit (Save) the Changes
#     # Crucial Step: If you don't commit, the table is created in memory but not saved.
#     conn.commit() 
#     print("All Done!")

# except Exception as e:
#     print("Error creating tables:", e)
#     conn.rollback() # Undo changes if there was an error

# finally:
#     cursor.close()
#     conn.close() # Close the connection









# # delete old data 
# def clean_database():
#     try:
#         conn = psycopg2.connect(os.getenv("DATABASE_URL"))
#         cur = conn.cursor()

#         print("🧹 Cleaning database...")

#         # 'CASCADE' forces the deletion of linked data in 'searches' automatically
#         # We RESTART IDENTITY so the IDs start back at 1 (instead of 5, 6, 7...)
#         sql = "TRUNCATE TABLE users, searches RESTART IDENTITY CASCADE;"

#         cur.execute(sql)
        
#         # CRITICAL FIX: Commit with the connection, not the cursor
#         conn.commit() 
        
#         print("✅ All old data deleted successfully!")
#         print("✅ IDs reset to 1.")

#     except Exception as e:
#         print("❌ Error:", e)
#     finally:
#         if conn:
#             cur.close()
#             conn.close()



# # Run the function
# if __name__ == "__main__":
#     clean_database()



def get_pending_searches():
  try:
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    print("DB Connected")

    sql="""
SELECT 
users.full_name,
users.email,
searches.query, 
searches.id 
FROM searches JOIN users ON searches.user_id = users.id"""

    cur.execute(sql)
    results=cur.fetchall() # Get all rows

    for row in results:
      name=row[0]
      email=row[1]
      topic=row[2]
      search_id=row[3]

      print(f'User : {name} | Email : {email} | Wants : {topic} | Search id : {search_id}')

  except Exception as e:
        print("Error:", e)
  finally:
        if conn:
            cur.close()
            conn.close()

# Run the function
if __name__ == "__main__":
    get_pending_searches()
