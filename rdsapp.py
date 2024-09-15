from flask import Flask, render_template, request
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

db_config = {
    'host': '{{resolve:ssm:/database/phonebook/dbname:1}}',
    'user': 'admin',
    'password': '{{resolve:ssm-secure:/database/phonebook/password:1}}',
    'database': '{{resolve:ssm-secure:/database/phonebook/username:1}}'
}

def get_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as error:
        print("Failed to connect to database:", error)
        return None

def setup_database():
    """Configure the database"""
    connection = get_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Create the table if it doesn't exist
            users_table = """ 
            CREATE TABLE IF NOT EXISTS users(
            username VARCHAR(255) NOT NULL PRIMARY KEY,
            email VARCHAR(255));
            """
            cursor.execute(users_table)
            
            # Insert the datas if they don't exist
            data = """
            INSERT IGNORE INTO users (username, email)
            VALUES
                ('dora', 'dora@amazon.com'),
                ('cansın', 'cansın@google.com'),
                ('sencer', 'sencer@bmw.com'),
                ('uras', 'uras@mercedes.com'),
                ('ares', 'ares@porche.com');
            """
            cursor.execute(data)
            
            # Save the changes
            connection.commit()
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            connection.close()

# Call setup_database only when starting the app
setup_database()

def find_emails(keyword):
    """Finds email addresses based on a specific keyword"""
    connection = get_connection()
    if connection:
        cursor = connection.cursor()
        query = f"SELECT * FROM users WHERE username LIKE '%{keyword}%'"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        if not result:
            return [("Not Found", "Not Found")]
        return result

def insert_email(name, email):
    """Insert new users to the database"""
    connection = get_connection()
    if connection:
        cursor = connection.cursor()
        response = ''
        if not name or not email:
            response = 'Username or email cannot be empty!'
        else:
            query = f"SELECT * FROM users WHERE username = '{name}'"
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                response = f"User {name} already exists"
            else:
                insert = f"INSERT INTO users (username, email) VALUES ('{name}', '{email}')"
                cursor.execute(insert)
                connection.commit()
                response = f"User {name} and {email} have been added successfully"
        cursor.close()
        connection.close()
        return response

@app.route('/', methods=['GET', 'POST'])
def emails():
    if request.method == 'POST':
        user_app_name = request.form['user_keyword']
        user_emails = find_emails(user_app_name)
        return render_template('emails.html', name_emails=user_emails, keyword=user_app_name, show_result=True)
    else:
        return render_template('emails.html', show_result=False)

@app.route('/add', methods=['GET', 'POST'])
def add_email():
    if request.method == 'POST':
        user_app_name = request.form['username']
        user_app_email = request.form['useremail']
        result_app = insert_email(user_app_name, user_app_email)
        return render_template('add-email.html', result_html=result_app, show_result=True)
    else:
        return render_template('add-email.html', show_result=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
