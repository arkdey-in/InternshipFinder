from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import psycopg2 
from flask_bcrypt import Bcrypt 


from scraper import find_internships, send_email

load_dotenv()

app = Flask(__name__)
app.config["DEBUG"] = False
app.secret_key = "some_random_secret_text" 
bcrypt = Bcrypt(app) 

def get_db_connection():
    url = os.getenv("DATABASE_URL")
    return psycopg2.connect(url)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/registration", methods=["GET","POST"])
def registration():
    if request.method == "POST":
        name = request.form["fullname"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"] 

        if password != confirm_password:
            flash("Passwords do not match!")
            return redirect(url_for('registration'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        conn = get_db_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s)",
                (name, email, hashed_password)
            )
            conn.commit()   
            flash("Account created! Please Login.")
            return redirect(url_for('login'))
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash("That email is already registered.")
        finally:
            cur.close()
            conn.close()

    return render_template("registration.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id, full_name, password_hash, email FROM users WHERE email = %s", (email,))
        user = cur.fetchone() 

        cur.close()
        conn.close()

        if user:

            if bcrypt.check_password_hash(user[2], password):
                session['user_id'] = user[0]
                session['user_name'] = user[1]
                session['user_email'] = user[3] 
                return redirect(url_for('query'))
        
        flash("Invalid email or password")

    return render_template("login.html")

@app.route("/query", methods=["GET","POST"])
def query():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    

    found_jobs = [] 
    
    if request.method == "POST":
        topic = request.form["query"]
        user_id = session['user_id']
        user_email = session.get('user_email') # Get email from session
        user_name = session.get('user_name')

        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO searches (user_id, query) VALUES (%s, %s)",
            (user_id, topic)
        )
        conn.commit()
        cur.close()
        conn.close()


        flash(f'Searching specifically for "{topic}"... This may take a few seconds.')
        
        try:

            found_jobs = find_internships(topic)
            

            if found_jobs:
                send_email(user_email, user_name, topic, found_jobs)
                flash(f"Success! We found {len(found_jobs)} jobs and sent them to your email.")
            else:
                flash("Search saved, but no results found right now. We will keep checking daily.")
                
        except Exception as e:
            print(f"Error running immediate search: {e}")
            flash("Search saved! Background scanner will check for jobs daily.")


    return render_template("query.html", jobs=found_jobs)

@app.route("/logout")
def logout():
    session.clear() 
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(port=5000)
























































# from flask import Flask, render_template , redirect , request , url_for , session , flash
# from flask_sqlalchemy import SQLAlchemy
# from dotenv import load_dotenv
# import os
# import psycopg2 # The driver to talk to Postgres (like mysql-connector)
# from flask_bcrypt import Bcrypt # Tool to secure (hash) passwords

# # Load the secret variables from .env file
# load_dotenv()

# app = Flask(__name__)
# app.config["DEBUG"] = False

# app.secret_key = "some_random_secret_text" # Required to use 'session'
# bcrypt = Bcrypt(app) # Initialize the security tool


# def get_db_connection():
#     url = os.getenv("DATABASE_URL")
#     return psycopg2.connect(url)

# @app.route("/")
# def home():
#     return render_template("index.html")

# @app.route("/registration", methods=["GET","POST"])
# def registration():
#     if request.method == "POST":
#         name=request.form["fullname"]
#         email=request.form["email"]
#         password = request.form["password"]
#         confirm_password = request.form["confirm_password"] 

#         if password != confirm_password:
#             flash("Passwords do not match!")
#             return redirect(url_for('registration'))

#         # Hash the password
#         hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

#         # Connect to DB
#         conn = get_db_connection()
#         cur = conn.cursor()

#         try:
#             cur.execute(
#                 "INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s)",
#                 (name, email, hashed_password)
#             )
#             conn.commit()    # Save the data
#             flash("Account created! Please Login.")
#             return redirect(url_for('login'))
#         except psycopg2.errors.UniqueViolation:
#             # This catches the error if the email already exists
#             conn.rollback()
#             flash("That email is already registered.")
#         finally:
#             cur.close()
#             conn.close()


#     return render_template("registration.html")

# @app.route("/login",methods=["GET","POST"])
# def login():
#     if request.method=="POST":
#         email = request.form["email"]
#         password = request.form["password"]

#         conn = get_db_connection()
#         cur = conn.cursor()

#         # SQL SELECT
#         # finding the user with that email
#         cur.execute("SELECT id, full_name, password_hash FROM users WHERE email = %s", (email,))
#         user = cur.fetchone() # fetchone() grabs the first matching row

#         cur.close()
#         conn.close()

#         if user:
#             # 'user' is a list: [id, name, hash]
#             # user[2] is the password hash from the database
#             if bcrypt.check_password_hash(user[2], password):
#                 # SUCCESS!
#                 # We save their ID in the 'session' (browser cookie)
#                 session['user_id'] = user[0]
#                 session['user_name'] = user[1]
#                 return redirect(url_for('query'))
        
#         flash("Invalid email or password")

#     return render_template("login.html")

# @app.route("/query",methods=["GET","POST"])
# def query():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
    
#     if request.method == "POST":
#         topic = request.form["query"]
#         user_id = session['user_id'] # Get the ID we saved during login

#         conn = get_db_connection()
#         cur = conn.cursor()
        
#         # 7. Insert the Search
#         cur.execute(
#             "INSERT INTO searches (user_id, query) VALUES (%s, %s)",
#             (user_id, topic)
#         )
#         conn.commit()
#         cur.close()
#         conn.close()

#         flash(f'Saved! We will search for: {topic}')
        
#         # return f"Saved! We will search for: {topic}"

#     return render_template("query.html")

# @app.route("/logout")
# def logout():
#     session.clear() # Delete the session data so they are logged out
#     return redirect(url_for('home'))


# if __name__ == "__main__":
#     app.run(port=5000)
