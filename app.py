#!/usr/local/python/3.4/bin/python
# -*- coding: utf-8 -*-
from flask import Flask
from flask import flash, redirect, url_for, session, request, logging
from flask import render_template as template
from wtforms import Form, SelectField, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import os, requests
from datetime import datetime


#conneting database
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = 'sqlite:///' + os.path.join(basedir, 'db', 'gutenberg.sqlite3')

#Flaskアプリケーションクラスのインスタンスを新規生成
app = Flask(__name__)

#アプリケーションの設定を追加
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

#Flaskアプリケーションを新規で生成する関数を定義
def create_app():
	app = Flask(__name__)
	app.config['SQLALCHEMY_DATABASE_URI'] = db_path
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	app.config['SQLALCHEMY_ECHO'] = False
	db.init_app(app)
	return app

#SQLSlchemyクラスのインスタンスを新規生成
db = SQLAlchemy(app)


#テーブルに相当するクラスを設定
class Users(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	password = db.Column(db.String(20), unique=True, nullable=False)
	created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
	updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

	def __repr__(self):
		return '<Users %r>' % self.username

class Books(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	url = db.Column(db.String(49), unique=True, nullable=False)
	title = db.Column(db.String(99), unique=False, nullable=False)
	author = db.Column(db.String(99), unique=False, nullable=True)
	body = db.Column(db.Text, unique=False, nullable=False)
	created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
	updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

	def __repr__(self):
		return '<Articles %r>' % self.title

# Register Form Class
class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	username = StringField('Username', [validators.Length(min=4, max=25)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Passwords do not match')
	])
	confirm = PasswordField('Confirm Password')

# Book Form Class
class BookForm(Form):
	url = StringField('Url', [validators.Length(min=1, max=200)])
	title = StringField('Title', [validators.Length(min=1, max=200)])
	author = StringField('Author', [validators.Length(min=1, max=200)])
	body = TextAreaField('Body', [validators.Length(min=30)])

#routing
@app.route('/')
@app.route('/home')
def index():
	return template("index.html")

@app.route('/works')
def works():
	return template("works.html")

@app.route('/gutenberg')
def gutenberg():

	book_results = Books.query.all()

	if book_results:
		return template('gutenberg.html', books=book_results)
	else:
		msg = 'No Books Found'
		return template('gutenberg.html', msg=msg)


@app.route('/translated/<string:book_id>', methods = ['GET', 'POST'])
def translated(book_id):

	result = Books.query.filter_by(id=book_id).first()

	if result:
		return template('translated.html', result=result)
	else:
		msg = 'No Books Found'
		return template('translated.html', msg=msg)


@app.route('/12rulesforlife')
def twelverulesforlife():
	return template('12rulesforlife.html')

@app.route('/shecomesfirst')
def shecomesfirst():
	return template('shecomesfirst.html')

@app.route('/nyt_bestsellers')
def nyt_bestsellers():
	url1 = "https://api.nytimes.com/svc/books/v3/lists/current/science.json"
	api_key = "***"
	query1 = {"api-key": api_key}
	res1 = requests.get(url1, params=query1)

	res_dict1= res1.json()
	books_list1 = res_dict1["results"]["books"]

	url2 = "https://api.nytimes.com/svc/books/v3/reviews.json"
	isbn = '9780062316097'
	query2 = {"api-key": api_key, "isbn": isbn}
	res2 = requests.get(url2, params=query2)

	res_dict2= res2.json()
	# review = 

	return template('nyt_bestsellers.html',books_list=books_list1, )

#login
@app.route('/login', methods = ['GET', 'POST'])
def login():
	if request.method == 'POST':
		#get form fields
		username = request.form['username']
		password_candidate = request.form['password']

		result = Users.query.filter_by(username=username).first()
		
		if result:
			if sha256_crypt.verify(password_candidate, result.password):
				session['logged_in'] = True
				session['username'] = username

				flash('You are now logged in', 'success')
				return redirect(url_for('dashboard'))

			else:
				error = 'Invalid Login'
				return template('login.html', error=error)

		else:
			error = 'Username Not Found'
			return template('login.html', error=error)

	return template("login.html")


def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
 			return f(*args, **kwargs)
		else:
			flash('Unauthorized, Please login', 'danger')
			return redirect(url_for('login'))
	return wrap


@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('You are now logged out', 'success')
	return redirect(url_for('login'))


@app.route('/dashboard')
@is_logged_in
def dashboard():

	book_results = Books.query.all()
	
	if book_results:
		return template('dashboard.html', books=book_results)
	else:
		msg = 'No Books Found'
		return template('dashboard.html', msg=msg)


# Add Book
@app.route('/add_book', methods=['GET', 'POST'])
@is_logged_in
def add_book():
	form = BookForm(request.form)
	if request.method == 'POST' and form.validate():
		url = form.url.data
		title = form.title.data
		author = form.author.data
		body = form.body.data

		result = Books(url=url, title=title, author=author, body=body)
		db.session.add(result)
		db.session.commit()

		flash('Book Created', 'success')

		return redirect(url_for('dashboard'))

	return template('add_book.html', form=form)


# Edit Book
@app.route('/edit_book/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_book(id):
    
	result = Books.query.filter_by(id=id).first()

	# Get form
	form = BookForm(request.form)

	# Populate article form fields
	form.url.data = result.url
	form.title.data = result.title
	form.author.data = result.author
	form.body.data = result.body

	if request.method == 'POST' and form.validate():
		url = request.form['url']
		title = request.form['title']
		author = request.form['author']
		body = request.form['body']

        # Execute
		book = Books.query.filter_by(id=id).first()
		book.url = url
		book.title = title
		book.author = author
		book.body = body

		db.session.add(book)
		db.session.commit()

		flash('Book Updated', 'success')

		return redirect(url_for('dashboard'))

	return template('edit_book.html', form=form)


# Delete Article
@app.route('/delete_book/<string:id>', methods=['POST'])
@is_logged_in
def delete_book(id):

	result = Books.query.filter_by(id=id).first()

	db.session.delete(result)
	db.session.commit()

	flash('Book Deleted', 'success')

	return redirect(url_for('dashboard'))


#サーバーの起動
if __name__ == '__main__':
	app.secret_key = 'himitsu'
	app.run(debug=True)