
from flask import Flask, render_template, session, request, jsonify
from flask_login import LoginManager, UserMixin
from flask_session import Session
from flask import redirect, flash
#import flask_socketio
from flask_socketio import SocketIO

from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import validators


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import desc
from flask_wtf import FlaskForm
from flask import Flask

from flask_login import logout_user
from flask_login import current_user, login_user

import os
import sqlite3

#project_dir = os.path.dirname(os.path.abspath(__file__))
#database_file = "sqlite:///{}".format(os.path.join(project_dir, "user_message_23.db"))

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = '123445667'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///user_message_24.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

socketio = SocketIO(app)
db = SQLAlchemy(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = password
        #generate_password_hash(password)

    def check_password(self, password):
        print(self.password_hash)
        print(password)
        if (self.password_hash == password):
            return(True)
        return(False)
        #return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class UserMessage(db.Model):

    index = db.Column(db.Integer, nullable= False, primary_key=True)
    user = db.Column(db.String(80), nullable=False)
    message = db.Column(db.String(80), nullable=False)

    def __init__(self, user, message):
        self.user = user
        self.message = message
        super(UserMessage,self).__init__()

    def __repr__(self):
        return "<User: {}, Message: {}>".format(self.user, self.message)


class Links(db.Model):
    index = db.Column(db.Integer, nullable= False, primary_key=True)
    link = db.Column(db.String(100), nullable = False)
    original = db.Column(db.String(200), nullable = False)

    def __init__(self, link, original):
        self.link = link
        self.original = original
        super(Links,self).__init__()

class Hotel(db.Model):
    index = db.Column(db.Integer, nullable= False, primary_key=True)
    message = db.Column(db.String(200), nullable = False)

    def __init__(self, message):
        self.message= message
        super(Hotel, self).__init__()

class Flight(db.Model):
    index = db.Column(db.Integer, nullable= False, primary_key=True)
    message= db.Column(db.String(200), nullable = False)

    def __init__(self, message):
        self.message = message
        super(Flight,self).__init__()

class Activity(db.Model):
    index = db.Column(db.Integer, nullable= False, primary_key=True)
    message= db.Column(db.String(200), nullable = False)
    def __init__(self, message):
        self.message = message
        super(Activity,self).__init__()

class Food(db.Model):
    index = db.Column(db.Integer, nullable= False, primary_key=True)
    message= db.Column(db.String(200), nullable = False)

    def __init__(self, message):
        self.message = message
        super(Food,self).__init__()


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

@app.route('/user_<name>')
def userPage(name):
    user_messages = UserMessage.query.filter_by(user=name).all()
    return(render_template('message-page.html', messages = user_messages, name = name))


@app.route('/landing')
def homepage():
    return render_template('landingpage.html')

@app.route('/logout')
def logout():
    logout_user()
    return render_template('homepage.html', current_user = current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if (current_user.is_authenticated):
        print('is authenticated')
        return(redirect('/'))
    form = LoginForm()
    if (form.validate_on_submit()):
        print(form.username.data)
        user = User.query.filter_by(username=form.username.data).first()
        print('user value:')
        print(user)
        if (user is None or not user.check_password(form.password.data)):
            flash('Invalid username or password')
            print('didnt match')
            return(redirect('/login'))
        user.authenticated = True
        db.session.add(user)
        db.session.commit()
        print('authenticated?')
        login_user(user, remember=True)
        print('logged in')
        print('matched')
        return(redirect('/'))
    return(render_template('login.html', title='Sign In', form=form))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect('/login')
    return render_template('register.html', title='Register', form=form)

@app.route('/')
def sessions():
    #parseChatData()
    #return render_template('homepage.html', current_user = current_user)
    return render_template('homepage.html', current_user = current_user, history = UserMessage.query.all(), links = Links.query.all(), hotel= Hotel.query.all(), flight=Flight.query.all(), activity = Activity.query.all(), food = Food.query.all())

@app.route('/category-update', methods=['GET', 'POST'])
def categoryUpdate():

    if (request.form['type'] == 'hotel'):
        print('in hotel')
        entry = Hotel(message=request.form['message'])
    elif (request.form['type'] == 'flight'):
        print('in flight')
        entry = Flight(message=request.form['message'])
    elif (request.form['type'] == 'food'):
        entry = Food(message=request.form['message'])
    else:
        print('in activity')
        entry = Activity(message=request.form['message'])

    db.session.add(entry)
    db.session.commit()

    return render_template('homepage.html', current_user = current_user, history = UserMessage.query.all(), links = Links.query.all(), hotel= Hotel.query.all(), flight=Flight.query.all(), activity = Activity.query.all(), food = Food.query.all())


def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@app.route('/message_<index>')
def movieProfile(message):
    item = UserMessage.query.get(message)
    #need to repopulate databse with correct Path
    link = 'static/' + movie_actor_map[title][1]
    return render_template('message-page.html', user = item.username, message = item.message)

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):

    print('received my event: ' + str(json))
    #add log to the database
    print(current_user.username)
    #print(json['message'])
    print(json)
    print('printing message')

    user_message = UserMessage(user=current_user.username, message=json['message'])
    db.session.add(user_message)
    db.session.commit()

    socketio.emit('my response', json, callback=messageReceived, broadcast = True)


@socketio.on('category update')
def handle_my_category_update(json, methods=['GET', 'POST']):

    id = json['id']

    print(json)
    if (not json['need_recent_msg']):
        print('in regular message');
        search = UserMessage.query.filter_by(index=id).first()

    else:

        search = db.session.query(UserMessage).order_by(desc(UserMessage.index)).first()
        print(search.message)

    json['message'] = search.message
    print('new json is')
    print(json)

    socketio.emit('category response', json, callback=messageReceived, broadcast = True)


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    global conn
    try:
        conn = sqlite3.connect(db_file)
        conn.close()
    except Error as e:
        print(e)

if __name__ == '__main__':
    create_connection("C:\\sqlite\db\user_message_24.db")
    console.log('created connection')
    db.create_all()
    #db.session.commit()
    #print('about to run')
    socketio.run(app, DEBUG=True)
