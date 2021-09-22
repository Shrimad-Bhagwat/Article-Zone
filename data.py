"""
This is a backup file
"""

from os import name
import re
import sqlite3
from flask import Flask,render_template,flash,redirect,url_for, session,logging,request
from flask.templating import render_template_string
# from data import Articles
# from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps
# from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///articles.db'

#Initialize database
# db = SQLAlchemy(app)


#---------------------------------------------------------------------------
con = sqlite3.connect("articlezone.db")  
# print("Database opened successfully") 
# con.execute("create table if not exists articles (id INTEGER PRIMARY KEY AUTOINCREMENT, title varchar(255) NOT NULL, author varchar(100),body text, create_date CURRENT_TIMESTAMP)")  

# con.execute("create table if not exists users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, name varchar(100), email varchar(100), username varchar(30), password varchar(100),register_date CURRENT_TIMESTAMP )")
#---------------------------------------------------------------------------


# cur = con.cursor()
# cur.execute("insert into articles values('1','Article 1','shrimad','This is Article 1','2021-09-22')")
# con.close()

# Config MySQL
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'mysql'
# app.config['MYSQL_DB'] = 'myflaskapp'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MySQL
# mysql = MySQL(app)

# Articles = Articles()

#Index
@app.route('/')
def index():
    return render_template('home.html')

#About
@app.route('/about')
def about():
    return render_template('about.html')

#Articles
@app.route('/articles')
def articles():
    #Create Cursor
    # cur =mysql.connection.cursor()
    con = sqlite3.connect("articlezone.db") 

    #Get Articles
    cur = con.cursor()
    result = cur.execute("Select * from articles")
    articles_list = cur.fetchall()
    list_articles = []
    dict={}
    article_keys = ['id','title','author','content','time']
    
    for tuple in articles_list:
        for key,value in enumerate(article_keys):
            dict[value]=tuple[key]
        list_articles.append(dict)  
        dict={}  
            
            
    # print("----------Result----------")
    # print(list_articles)
    # print("----------Result----------")
    if result:
        return render_template('articles.html',articles = list_articles)
    else:
        msg = "No Articles Found"
        return render_template('articles.html',msg = msg)
    #Close connection
    con.close()

#Article
@app.route('/article/<string:id>/')
def article(id):
        #Create Cursor
    con = sqlite3.connect("articlezone.db") 

    #Get Article
    id = int(id)
    cur = con.cursor()
    result = cur.execute("Select * from articles where id=?",[id])
    article_values = list(cur.fetchone())
    article_keys = ['id','title','author','content','time']
    article={}
    for key,value in enumerate(article_keys):
            article[value]=article_values[key]




    # print("----------Result----------")
    # print(article)
    # print("----------Result----------")
    #Close connection
    con.close()
    return render_template('article.html',article=article)


#Register Form
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1,max=50)])
    username = StringField('Username', [validators.Length(min=4,max=25)])
    email = StringField('Email', [validators.Length(min=6,max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm',message = "Password do not match!")])
    confirm = PasswordField('Confirm Password')

#User Register
@app.route('/register', methods = ['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        con = sqlite3.connect("articlezone.db") 
        query = "INSERT INTO users(name,email,username,password) VALUES(?,?,?,?)"
        data = (name,email,username,password)
        con.execute(query,data)
        con.commit()

        con.close()
        flash("You are now Registered!","success")
        return redirect(url_for('login'))
    return render_template('register.html',form = form)

# User Login
@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']
        
        con = sqlite3.connect("articlezone.db") 
        cur = con.cursor()
        result = cur.execute("Select * from users where username = ?",[username])

        if(result):
            data = list(cur.fetchone())
            print("-------\n---\n-----\n--------------")
            print(data)
            password = data[4]

            if(sha256_crypt.verify(password_candidate,password)):
                # app.logger.info('PASSWORD MATCHED')
                session['logged_in'] = True
                session['username'] = username

                flash("You are now Logged in","success")
                return redirect(url_for('dashboard'))
            else:
                error = "Password not matched"
                return render_template('login.html',error=error)
                # app.logger.info('PASSWORD NOT MATCHED')
            con.close()
        else:
            error = "Username not found"
            return render_template('login.html',error=error)
            # app.logger.info('No User')
    return render_template('login.html')
 
# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorised, Please Login!", "danger")
            return redirect(url_for('login'))
    return wrap
#Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now Logged Out' , "success")
    return redirect(url_for('login'))
 
#Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    #Create Cursor
    con = sqlite3.connect("articlezone.db") 
    cur = con.cursor()
    #Get Articles
    cur = con.cursor()
    result = cur.execute("Select * from articles")
    articles_list = cur.fetchall()
    list_articles = []
    dict={}
    article_keys = ['id','title','author','content','time']
    
    for tuple in articles_list:
        for key,value in enumerate(article_keys):
            dict[value]=tuple[key]
        list_articles.append(dict)  
        dict={}  
            
    if result:
        return render_template('dashboard.html',articles = list_articles)
    else:
        msg = "No Articles Found"
        return render_template('dashboard.html',msg = msg)
    #Close connection
    cur.close()

#Article Form
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1,max=200)])
    body = TextAreaField('Body', [validators.Length(min=10)])
   
#Add Article
@app.route('/add_article', methods = ['GET','POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        body = form.body.data

        #Create cursor
        con = sqlite3.connect("articlezone.db") 
        cur = con.cursor()
        print(session['username'])
        data = (title,body,session['username'])
        cur.execute("INSERT INTO articles(title,body,author) VALUES(?,?,?)",data)
        con.commit()

        con.close()

        flash("Article Created","success")

        return redirect(url_for('dashboard'))
    return render_template('add_article.html',form=form )

#Edit Article
@app.route('/edit_article/<string:id>', methods = ['GET','POST'])
@is_logged_in
def edit_article(id):
    #Create Cursor
    con = sqlite3.connect("articlezone.db") 
    cur = con.cursor()
    #Get User by ID
    cur.execute("Select * from articles where id=?",[id])
    article_values = list(cur.fetchone())
    article_keys = ['id','title','author','content','time']
    article={}
    for key,value in enumerate(article_keys):
            article[value]=article_values[key]



    #Get Form
    form = ArticleForm(request.form)
    #Popular Article form fields
    form.title.data = article['title']
    form.body.data = article['content']


    if request.method == "POST" and form.validate():
        title = request.form['title']
        body =request.form['body']

        #Create cursor
        con = sqlite3.connect("articlezone.db") 
        cur = con.cursor()
        cur.execute("UPDATE articles SET title = ?, body = ? WHERE id=?",(title,body,id))

        # mysql.connection.commit()
        con.commit()
        con.close()

        flash("Article Updated","success")

        return redirect(url_for('dashboard'))
    return render_template('edit_article.html',form=form )


#Delete Article
@app.route('/delete_article/<string:id>', methods = ['GET','POST'])
@is_logged_in
def delete_article(id):
    #Create cursor
    con = sqlite3.connect("articlezone.db") 
    cur = con.cursor()
    cur.execute("DELETE from articles where id=?",[id])
    con.commit()
    # mysql.connection.commit()

    con.close()

    flash("Article Deleted","success")

    return redirect(url_for('dashboard'))



if (__name__ == '__main__'):
    app.secret_key = "secret123"
    app.run(debug=True)


