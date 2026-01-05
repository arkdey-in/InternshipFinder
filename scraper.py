import os
import psycopg2
import smtplib # The Email Library
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()


API_KEY = os.getenv("GOOGLE_API_KEY")
CSE_ID = os.getenv("GOOGLE_CSE_ID")
MAIL_USER = os.getenv("MAIL_USERNAME")
MAIL_PASS = os.getenv("MAIL_PASSWORD")


def find_internships(topic):
    print(f"🔎 Searching for: {topic}...")
    found_jobs = []

    search_term = f'"{topic}" internship India 2025 site:linkedin.com/jobs'

    try:
        service = build("customsearch", "v1", developerKey=API_KEY)
        result = service.cse().list(q=search_term, cx=CSE_ID, num=5).execute()
        
        if 'items' in result:
            for item in result['items']:
                found_jobs.append({
                    "title": item['title'],
                    "link": item['link']
                })
    except Exception as e:
        print(f"API Error: {e}")
        
    return found_jobs


def send_email(to_email, user_name, topic, jobs):
    print(f"📧 Sending email to {to_email}...")

    msg = MIMEMultipart()
    msg['From'] = MAIL_USER
    msg['To'] = to_email
    msg['Subject'] = f"Internship Alert: {topic}"


    body = f"""
    <h2>Hello {user_name},</h2>
    <p>Here are the top internship findings for <b>{topic}</b> today:</p>
    <ul>
    """
    
    for job in jobs:
        body += f"<li><a href='{job['link']}'>{job['title']}</a></li><br>"
    
    body += "</ul><p>Good luck!<br>Your Internship Bot</p>"

    msg.attach(MIMEText(body, 'html'))

    try:
        # Connect to Gmail Server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() # Secure the connection
        server.login(MAIL_USER, MAIL_PASS)
        text = msg.as_string()
        server.sendmail(MAIL_USER, to_email, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Email Error: {e}")

# --- FUNCTION 3: THE MANAGER ---
def run_daily_task():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cur = conn.cursor()

        sql = """
            SELECT users.full_name, users.email, searches.query
            FROM searches 
            JOIN users ON searches.user_id = users.id
        """
        cur.execute(sql)
        user_requests = cur.fetchall()

        print(f"📋 Found {len(user_requests)} tasks in queue.\n")

        for row in user_requests:
            name = row[0]
            email = row[1]
            topic = row[2]
            
            print(f"Processing Task for: {name} ({topic})")
            
            jobs = find_internships(topic)
            
            if jobs:
                print(f"   ✅ Found {len(jobs)} links. Sending email...")
                send_email(email, name, topic, jobs)
            else:
                print("No jobs found, skipping email.")
            
            print("-" * 40)

    except Exception as e:
        print("Database Error:", e)
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    if not MAIL_USER or not MAIL_PASS:
        print("Error: Missing MAIL_USERNAME or MAIL_PASSWORD in .env file")
    else:
        run_daily_task()
