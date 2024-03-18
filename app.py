from flask import Flask, render_template, request, redirect
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

DATABASE = "C:/Users/20157/OneDrive - Wellington College/13 DT/Project/Dictionary.db"


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
def menu():
    con = create_connection(DATABASE)
    query = "SELECT Maori, English, Category, Level, Definition FROM Words"
    cur = con.cursor()
    cur.execute(query)
    word_list = cur.fetchall()
    con.close()
    print(word_list)
    return render_template('menu.html', words=word_list)


@app.route('/login', methods=['POST', 'GET'])
def render_login_page():
    return render_template('login.html')


if __name__ == '__main__':
    app.run()
