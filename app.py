from os import name
import re
from flask import Flask,render_template,flash,redirect,url_for, session,logging,request
from flask.templating import render_template_string
# from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps


app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mysql'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MySQL
mysql = MySQL(app)

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
    cur =mysql.connection.cursor()

    #Get Articles
    result = cur.execute("Select * from articles")
    
    articles = cur.fetchall()

    if result > 0:
        return render_template('articles.html',articles = articles)
    else:
        msg = "No Articles Found"
        return render_template('articles.html',msg = msg)
    #Close connection
    cur.close()

#Article
@app.route('/article/<string:id>/')
def article(id):
        #Create Cursor
    cur =mysql.connection.cursor()

    #Get Article
    result = cur.execute("Select * from articles where id=%s",[id])
    
    article = cur.fetchone()

    return render_template('article.html',article=article)
    #Close connection
    cur.close()


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

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name,email,username,password) VALUES(%s,%s,%s,%s)",(name,email,username,password))
        mysql.connection.commit()

        cur.close()
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
        
        cur = mysql.connection.cursor()
        result = cur.execute("Select * from users where username = %s",[username])

        if(result > 0):
            data = cur.fetchone()
            password = data['password']

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
            cur.close()
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
    cur =mysql.connection.cursor()

    #Get Articles
    result = cur.execute("Select * from articles")
    
    articles = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html',articles = articles)
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
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO articles(title,body,author) VALUES(%s,%s,%s)",(title,body,session['username']))

        mysql.connection.commit()

        cur.close()

        flash("Article Created","success")

        return redirect(url_for('dashboard'))
    return render_template('add_article.html',form=form )

#Edit Article
@app.route('/edit_article/<string:id>', methods = ['GET','POST'])
@is_logged_in
def edit_article(id):
    #Create Cursor
    cur = mysql.connection.cursor()

    #Get User by ID
    result = cur.execute("Select * from articles where id=%s",[id])

    article = cur.fetchone()

    #Get Form
    form = ArticleForm(request.form)
    #Popular Article form fields
    form.title.data = article['title']
    form.body.data = article['body']


    if request.method == "POST" and form.validate():
        title = request.form['title']
        body =request.form['body']

        #Create cursor
        cur = mysql.connection.cursor()

        cur.execute("UPDATE articles SET title = %s, body = %s WHERE id=%s",(title,body,id))

        mysql.connection.commit()

        cur.close()

        flash("Article Updated","success")

        return redirect(url_for('dashboard'))
    return render_template('edit_article.html',form=form )


#Delete Article
@app.route('/delete_article/<string:id>', methods = ['GET','POST'])
@is_logged_in
def delete_article(id):
    #Create cursor
    cur = mysql.connection.cursor()

    cur.execute("DELETE from articles where id=%s",[id])

    mysql.connection.commit()

    cur.close()

    flash("Article Deleted","success")

    return redirect(url_for('dashboard'))



if (__name__ == '__main__'):
    app.secret_key = "secret123"
    app.run(debug=True)


