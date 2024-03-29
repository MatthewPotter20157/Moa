from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "f89say987fy87ats87"
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


def is_logged_in():
    if session.get("email") is None:
        print("not logged in")
        return False
    else:
        print("logged in")
        return True


def data_cleanse():
    con = open_database(DATABASE)
    # read the data from the database *
    query = 'SELECT * FROM Words'
    cur = con.cursor()
    cur.execute(query)
    # need a list of correct categories to compare the category to
    correct_cats = ['Actions', 'Animals', 'Clothing', 'Culture / Religion', 'Descriptive', 'Emotions', 'Food',
                    'Math / Number', 'Outdoors', 'People', 'School', 'Technology', 'Time']

    # acceptable level range to compare
    # capitalise first letter


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
def login():
    if is_logged_in():
        return redirect("/")
    if request.method == 'POST':
        email_user = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        print(email_user)
        query = "SElECT * FROM Users WHERE email = ?"
        con = open_database(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email_user, ))
        user_data = cur.fetchone()
        con.close()
        print(user_data)
        try:
            user_id = user_data[0]
            name = user_data[1]
            db_password = user_data[4]
        except IndexError:
            return redirect("/login?error-Email+invalid+or+password+incorrect")
        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer + "?error=Email+invalid+or+password+incorrect")
        session['email'] = email_user
        session['Id'] = user_id
        session['fname'] = name
        print(session)
        return redirect('/')
    return render_template('login.html')


@app.route('/logout')
def logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/?message=See+you+next+time!')


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
