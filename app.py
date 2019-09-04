from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
#from data import Articles #we made data.py ourselves for starting
from flask_mysqldb import MySQL
#wtforms is to add fields with validation. WTForms allows you to validate your forms on the server side
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt # to encrypt password
from functools import wraps # this is for flask decorators i.e. to check whether a user is logged in or not

# Configure application
app = Flask(__name__)


# Config MySQL: https://flask-mysql.readthedocs.io/en/latest/

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskblogdb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' # by default it returns tuple but we want dict

# init MySQL
mysql = MySQL(app)


# we have made a separete data.py file calles Articles from which we get Aritcles() - this was  just for start; later we pull form db
#Articles = Articles()

# make a route for our home page
# index
@app.route('/')
def index():
  return render_template('home.html')

#about
@app.route('/about')
def about():
  return render_template('about.html')

# articles
@app.route('/articles')
def articles():
  # create cursor
  cur = mysql.connection.cursor()
  # get articles
  result = cur.execute("SELECT * FROM articles")

  articles = cur.fetchall() # will fetch it all in dictinary form

  if result > 0:
    return render_template('articles.html', articles = articles)
  else:
    msg = 'NO Articles Found'
    return render_template('articles.html', msg=msg)

  # close connection
  cur.close()

# single article
@app.route('/article/<string:id>/')
def article(id):
  # create cursor
  cur = mysql.connection.cursor()

  # get article of specific id
  result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

  article = cur.fetchone()

  return render_template('article.html', id = id, article=article)

# go to wtforms documentation for reference to create a form class
# register form calss
class RegisterForm(Form):
  name = StringField('Name', [validators.Length(min=1, max=50)])
  username = StringField('Username', [validators.Length(min=4, max=25)])
  email = StringField('Email', [validators.Length(min=6, max=50)])
  password = PasswordField('Password', [
    validators.DataRequired(),
    validators.EqualTo('confirm', message='Passwords do not match')
  ])
  confirm = PasswordField('Confirm Password')

# user register
@app.route('/register', methods=['GET', 'POST'])
def register():
  #RegisterForm class defined above
  form = RegisterForm(request.form)

  if request.method == 'POST' and form.validate():
    # using wtforms here
    name = form.name.data
    email = form.email.data
    username = form.username.data
    password = sha256_crypt.encrypt(str(form.password.data))

    # create cursor to manipulate db and execute commands
    cur = mysql.connection.cursor()
   
    # %s is string replacement. Execute query
    cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

    # commit to DB
    mysql.connection.commit()
    
    # close the conneciton
    cur.close()

    flash('You are now registered and can log in', 'success')
    
    return redirect(url_for('login'))

  return render_template('register.html', form=form)
  

  
# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    # Get form fields
    # not using wtforms here as not needed
    username = request.form['username']
    password_candidate = request.form['password']

    # create a cursor
    cur = mysql.connection.cursor()

    # get user by username
    result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

    if result > 0:
      # get stored hash
      data = cur.fetchone() # fetch the first on it finds despite having many usernames that are same
      password = data['password']

      # compare the passwords
      if sha256_crypt.verify(password_candidate, password):
        # app.logger.info('PASSWORD MATCHED')
        # PASSED

        #creating sessions

        session['logged_in'] = True
        session['username'] = username

        flash('You are now logged in', 'success')
        return redirect(url_for('dashboard'))

      else:
        #app.logger.info('PASSWORD NOT MATCHED')
        error = 'Invalid login'
        return render_template('login.html', error=error)

      # close connection
      cur.close()

    else:
      #app.logger.info('NO USER')
      error = 'Username not found'
      return render_template('login.html', error=error)
    


  return render_template('login.html')

# check if usr logged in - flask decorators
def is_logged_in(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return f(*args, **kwargs)
    else:
      flash('Unauthorized, Please login', 'danger')
      return redirect(url_for('login'))
  
  return wrap

# logout
@app.route('/logout')
@is_logged_in
def logout():
  session.clear()
  flash('You are now logged out', 'success')

  return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in # this is the decorater created to prevent unauthorized login
def dashboard():
  # create cursor
  cur = mysql.connection.cursor()
  # get articles
  result = cur.execute("SELECT * FROM articles")

  articles = cur.fetchall() # will fetch it all in dictinary form

  if result > 0:
    return render_template('dashboard.html', articles = articles)
  else:
    msg = 'NO Articles Found'
    return render_template('dashboard.html', msg=msg)

  # close connection
  cur.close()

# article form class using wtforms
class ArticleForm(Form):
  title = StringField('Title', [validators.Length(min=1, max=200)])
  body = TextAreaField('Body', [validators.Length(min=30)])

# add article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
  # get form
  form = ArticleForm(request.form)
  if request.method == 'POST' and form.validate():
    title = form.title.data
    body = form.body.data

    # create cursor
    cur = mysql.connection.cursor()

    # execute
    cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, session['username']))

    # commit to db
    mysql.connection.commit()

    # close connection
    cur.close()
    
    flash('Article Created', 'success')

    return redirect(url_for('dashboard'))

  return render_template('add_article.html', form=form)

# edit article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_artilce(id):
  # before we edit form we need to fetch form form db
  # create cursor
  cur = mysql.connection.cursor()

  # get article by id
  result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

  article = cur.fetchone()

  # get form
  form = ArticleForm(request.form)

  # populate article form fields
  form.title.data = article['title']
  form.body.data = article['body']


  if request.method == 'POST' and form.validate():
    # here we are fetching data not from wtforms but from actual form being edited
    title = request.form['title']
    body = request.form['body']


    # create cursor
    cur = mysql.connection.cursor()

    # execute
    cur.execute("UPDATE articles SET title=%s, body=%s WHERE id=%s", (title, body, id))

    # commit to db
    mysql.connection.commit()

    # close connection
    cur.close()
    
    flash('Article Updated', 'success')

    return redirect(url_for('dashboard'))

  return render_template('edit_article.html', form=form)

# Delete Article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
  # create cursor
  cur = mysql.connection.cursor()

  # execute
  cur.execute("DELETE FROM articles WHERE id =%s", [id])

  # commit to db
  mysql.connection.commit()

  # close connection
  cur.close()

  flash('Article Deleted', 'success')

  return redirect(url_for('dashboard'))

# gonna run the server
if __name__ == '__main__':
  app.secret_key='secret123' # for login sessions
  app.run(debug=True) # have put debug=True, so we don't have to restart the server. After making any change, only a refresh of browser will updata
