from flask_wtf import FlaskForm
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError
from models import User


# Since we are calling this function from LoginFrom, form will be passed as login.
# Since we are calling this function from Password, field will be passed as password.
def InvalidCredentials(form, field):
    """Username and Password Checker"""
    username_entered = form.username.data
    password_entered = field.data

    # Check credentials are valid
    user_object = User.query.filter_by(username=form.username.data).first()
    if user_object is None:
        raise ValidationError("Username or Password is incorrect.")
    elif not pbkdf2_sha256.verify(password_entered, user_object.password):
        raise ValidationError("Username or Password is incorrect.")


class RegistrationForm(FlaskForm):
    """Registration Form"""

    username = StringField('username_label', validators=[InputRequired(message="Username is required !!"),
                                                         Length(min=4, max=25, message="Username must be between"
                                                                                       "4 to 25 characters.")])
    password = PasswordField('password_label', validators=[InputRequired(message="Password is required !!"),
                                                           Length(min=4, max=25, message="Password must be between"
                                                                                         "4 to 25 characters.")])
    confirm_pswd = PasswordField('confirm_pswd_label', validators=[InputRequired(message="Password is required !!"),
                                                                   EqualTo('password',
                                                                           message="Password must match !")])
    submit_btn = SubmitField('Create')

    def validate_username(self, username):
        user_object = User.query.filter_by(username=username.data).first()
        if user_object:
            raise ValidationError("Username already exists. Please select another username.")


class LoginForm(FlaskForm):
    """Login Form"""
    username = StringField('username_label', validators=[InputRequired(message="Username is required.")])
    password = PasswordField('password_label',
                             validators=[InputRequired(message="Password is required !!"), InvalidCredentials])
    submit_btn = SubmitField('Create')
