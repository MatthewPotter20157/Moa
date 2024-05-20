from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
from datetime import datetime

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

def is_teacher():
    if session.get("teacher") is None:
        print("not teacher")
        return False
    else:
        print("teacher")
        return True


@app.route('/')
def render_homepage():
    print(session)
    return render_template('home.html', logged_in=is_logged_in(), teacher=is_teacher())


@app.route('/dictionary', methods=['GET', 'POST'])
def dictionary():
    if request.method == 'POST':
        word_Id = request.form.get('Word_id')
        print(word_Id)
        query = 'DELETE FROM Word WHERE Word_id = ?'
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (word_Id,))
        con.commit()
        con.close()
        return redirect('/dictionary?error=Deleted')
    con = create_connection(DATABASE)
    query = "SELECT Word_Id, Maori, English, Category, Definition, Level, fname, Image, Date_Entry FROM Word w " \
            "INNER JOIN Users u ON w.User_ID = u.Id INNER JOIN Category c ON w.Cat_id = c.Id"
    cur = con.cursor()
    cur.execute(query)
    word_list = cur.fetchall()
    con.close()
    con = create_connection(DATABASE)
    query = "SELECT * FROM Category"
    cur = con.cursor()
    cur.execute(query)
    category = cur.fetchall()
    con.close()
    print(word_list)
    return render_template('menu.html', categories=category, words=word_list, logged_in=is_logged_in(), teacher=is_teacher())


@app.route('/category', methods=['GET', 'POST'])
def categories():
    con = create_connection(DATABASE)
    query = "SELECT * FROM Category"
    cur = con.cursor()
    cur.execute(query)
    category = cur.fetchall()
    con.close()
    if request.method == 'POST':
        category_1 = request.form.get('category')
        con = create_connection(DATABASE)
        query = "SELECT Maori, English, Category, Definition, Level, fname, Image, Date_Entry FROM Word w " \
                "INNER JOIN Users u ON w.User_ID = u.Id INNER JOIN Category c ON w.Cat_id = c.Id WHERE w.Category = ?"
        cur = con.cursor()
        cur.execute(query, (category_1,))
        words_list = cur.fetchall()
        print(words_list)
        con.close()
        return render_template('category.html', categories=category, words=words_list,
                               logged_in=is_logged_in(), teacher=is_teacher())
    return render_template('category.html', categories=category, words=[],
                           logged_in=is_logged_in(), teacher=is_teacher())


@app.route('/login', methods=['POST', 'GET'])
def login():
    if is_logged_in():
        return redirect("/")
    print("Logging in")
    if request.method == 'POST':
        email_user = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        print(email_user)
        query = "SElECT Id, fname, password,teacher FROM Users WHERE email = ?"
        con = open_database(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email_user, ))
        user_data = cur.fetchall()
        con.close()
        print(user_data)

        if user_data is None:
            return redirect("/login?error=Email+invalid+password+incorrect")

        try:
            user_id = user_data[0][0]
            name = user_data[0][1]
            db_password = user_data[0][2]
            teacher = user_data[0][3]

        except IndexError:
            return redirect("/login?error=Email+invalid+password+incorrect")

        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer + "?error=Email+invalid+or+password+incorrect")

        session['email'] = email_user
        session['Id'] = user_id
        session['fname'] = name
        session['teacher'] = teacher
        print(session)
        return redirect('/')
    return render_template('login.html', logged_in=is_logged_in(), teacher=is_teacher())


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
        teacher = request.form.get('teacher')

        if password_user != password2:
            print(f'password1: {password_user}, password2: {password2}')
            return redirect("/signup?error=Passwords+do+not+match")

        if len(password_user) < 8:
            return redirect("/signup?error=Password+must+be+at+least+8+letters")

        hashed_password = bcrypt.generate_password_hash(password_user)
        con = open_database(DATABASE)
        query = 'INSERT INTO Users (fname, lname, email, password, teacher) VALUES (?, ?, ?, ?, ?)'
        cur = con.cursor()
        try:
            cur.execute(query, (f_name, l_name, email_user, hashed_password, teacher))
            con.commit()
        except sqlite3.IntegrityError:
            con.close()
            return redirect("/signup?error=Email+is+all+ready+in+use")

    return render_template('signup.html', logged_in=is_logged_in(), teacher=is_teacher())


@app.route('/admin', methods=['POST', 'GET'])
def render_admin():
    if request.method == 'POST':
        print(request.form)
        maori = request.form.get('maori').capitalize().strip()
        english = request.form.get('english').capitalize().strip()
        category = request.form.get('category')
        definition = request.form.get('definition').capitalize()
        level = request.form.get('level')
        user_id = session.get('Id')
        image = 'noimage'
        date_entry = datetime.today().strftime("%d-%m-%Y")
        con = open_database(DATABASE)
        query = 'INSERT INTO Word (Maori, English, Definition, Level, Image, Cat_id, User_id, date_entry) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
        cur = con.cursor()
        try:
            cur.execute(query, (maori, english,  definition, level, image, category, user_id, date_entry))
            con.commit()
        except sqlite3.IntegrityError:
            con.close()
            return redirect("/admin?error=no")
    con = open_database(DATABASE)
    query = "SELECT * FROM Category"
    cur = con.cursor()
    cur.execute(query)
    category = cur.fetchall()
    con.close()
    print(category)
    return render_template('admin.html', categories=category,
                           logged_in=is_logged_in(), teacher=is_teacher())


@app.route('/edit_word', methods=['POST', 'GET'])
def edit_word():
    if request.method == 'POST':
        print(request.form)
        maori = request.form.get('maori').capitalize().strip()
        english = request.form.get('english').capitalize().strip()
        category = request.form.get('category').capitalize().strip()
        definition = request.form.get('definition').capitalize()
        level = request.form.get('level')
        user_id = session.get('Id')
        image = 'noimage'
        con = open_database(DATABASE)
        query = 'INSERT INTO Words (Maori, English, Definition, Level, Image, Cat_id, User_id ) VALUES (?, ?, ?, ?, ?, ?, ?)'
        cur = con.cursor()
        try:
            cur.execute(query, (maori, english,  definition, level, image, category, user_id))
            con.commit()
        except sqlite3.IntegrityError:
            con.close()
            return redirect("/admin?error=no")
        return render_template("edit_word.html", categories=category, logged_in=is_logged_in(), teacher=is_teacher())


if __name__ == '__main__':
    app.run()
