import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_socketio import SocketIO, join_room, leave_room, send
from wtform_fields import *
from models import *

# Configure app
app = Flask(__name__)
app.secret_key = 'replace later'

# Configure database
ENV = 'dev'

if ENV == 'dev':
    # app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:arrehman@123@localhost/chatworld'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://jtcgcxsmzwayup' \
                                            ':0bf449db2c77caf257956f36454db3a8c4e087034ad7e89cf3e7b83eee1bb23d@ec2-34' \
                                            '-233-226-84.compute-1.amazonaws.com:5432/d713o8v1ovp9rp '
# Initialize connection to database
db = SQLAlchemy(app)

# Initialize flask socketIO
socketio = SocketIO(app, manage_session=False)

db.create_all()
db.session.commit()

# Configure flask login
login = LoginManager()
login.init_app(app)

# Predefined rooms for chat
ROOMS = ["lounge", "news", "games", "coding"]

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/', methods=['GET', 'POST'])
def index():
    reg_form = RegistrationForm()

    # Update database if validation success
    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data

        # Hashed Password
        hashed_pswd = pbkdf2_sha256.hash(password)

        # Add user to database
        user = User(username=username, password=hashed_pswd)
        db.session.add(user)
        db.session.commit()
        flash('Registered successfully. Please Login.', 'success')
        return redirect(url_for('login'))

    return render_template('index.html', form=reg_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login Form"""
    login_form = LoginForm()

    # Allow login if validation success
    if login_form.validate_on_submit():
        user_object = User.query.filter_by(username=login_form.username.data).first()
        login_user(user_object)
        return redirect(url_for('chat'))

    # If user requests GET
    return render_template('login.html', form=login_form)


@app.route('/chat', methods=['GET', 'POST'])
@app.route("/chat", methods=['GET', 'POST'])
def chat():
    if not current_user.is_authenticated:
        flash('Please login', 'danger')
        return redirect(url_for('login'))

    return render_template("chat.html", username=current_user.username, rooms=ROOMS)


@app.route("/logout", methods=['GET'])
def logout():

    # Logout user
    logout_user()
    flash('You have logged out successfully', 'success')
    return redirect(url_for('login'))


# Message is one of the pre-defined event among Connect, Disconnect, Message, JSON.
@socketio.on('message')
def message(data):
    print("Ithe Allo.")
    print(data)
    send(data)
    # emit specifies the event bucket we want to send data to.
    emit('some-event', 'This is a custom event message.')


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@socketio.on('incoming-msg')
def on_message(data):
    """Broadcast messages"""

    msg = data["msg"]
    username = data["username"]
    room = data["room"]
    # Set timestamp
    time_stamp = time.strftime('%b-%d %I:%M%p', time.localtime())
    send({"username": username, "msg": msg, "time_stamp": time_stamp}, room=room)


@socketio.on('join')
def on_join(data):
    """User joins a room"""

    username = data["username"]
    room = data["room"]
    join_room(room)

    # Broadcast that new user has joined
    send({"msg": username + " has joined the " + room + " room."}, room=room)


@socketio.on('leave')
def on_leave(data):
    """User leaves a room"""

    username = data['username']
    room = data['room']
    leave_room(room)
    send({"msg": username + " has left the room"}, room=room)


if __name__ == "__main__":
    socketio.run(app, debug=True)
