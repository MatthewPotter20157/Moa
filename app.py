from flask import Flask, render_template, request, redirect
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

DATABASE = "C:/Users/20157/OneDrive - Wellington College/13 DT/Project/identifier.sqlite"


def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
    return None


def open_database(database):
    return sqlite3.connect(database)


@app.route('/')
def render_homepage():
    return render_template('home.html')


@app.route('/menu')
def menu():
    con = create_connection(DATABASE)
    query = "SELECT Maori, English, Category, Definition, Level FROM Words"
    cur = con.cursor()
    cur.execute(query)
    word_list = cur.fetchall()
    con.close()
    print(word_list)
    return render_template('menu.html', words=word_list)


@app.route('/login', methods=['POST', 'GET'])
def render_login_page():
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def render_signup_page():
    if request.method == 'POST':
        print(request.form)
        f_name = request.form.get('fname').title().strip()
        l_name = request.form.get('lname').title().strip()
        email_user = request.form.get('email').lower().strip()
        password_user = request.form.get('password')
        password2 = request.form.get('password2')
        teacher = 'on'

        if password_user != password2:
            print(f'password1: {password_user}, password2: {password2}')
            return redirect("/signup?error=Passwords+do+not+match")

        if len(password_user) < 8:
            return redirect("/signup?error=Password+must+be+at+least+8+letters")

        con = open_database(DATABASE)
        query = 'INSERT INTO Users (fname, lname, email, password, teacher) VALUES (?, ?, ?, ?,?)'
        cur = con.cursor()
        try:
            cur.execute(query, (f_name, l_name, email_user, password_user, teacher))
            con.commit()
        except sqlite3.IntegrityError:
            con.close()
            return redirect("/signup?error=Email+is+all+ready+in+use")

    return render_template('signup.html')


if __name__ == '__main__':
    app.run()
