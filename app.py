from flask import Flask, render_template
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

DATABASE = "C:/Users/20157/OneDrive - Wellington College/13 DT/Project/Dicitionary.db"


def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
    return None


@app.route('/')
def render_homepage():
    return render_template('home.html')


@app.route('/menu')
def render_homepage():
    query = "SELECT Maori, English, Category, Definition, Level FROM Words"
    cur = con.cursor()
    cur.execute(query)
    word_list = cur.fetchall()
    con.close()
    print(word_list)
    return render_template('menu.html', words=word_list)


@app.route('/signup', methods=['POST', 'GET'])
def render_signup_page():
    if request.method('POST'):
        print(request.form)
        fname = request.form.get('fname').title().strip()
        lname = request.form.get('lname').title().strip()
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            return redirect("/signup?error=Passwords+do+not+match")

        if password < 8:
            return redirect("/signup?error=Password+must+be+at+least+8+letters")

        con = open_database('DATABASE')
        query = 'INSERT INTO user (fname, lname, email, password) VALUES (?, ?, ?, ?)'

        try:
            cur.execute(query, (fname, lname, email, password))
        except sqlite3.IntegrityError:
            con.close()
            return redirect("/signup?error=Email+is+all+ready+in+use")
    return render_template('signup.html')





if __name__ == '__main__':
    app.run()
