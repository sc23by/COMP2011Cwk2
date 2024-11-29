from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp, ValidationError

# Custom password validator
def strong_password(form, field):
    # Enforce strong passwords with uppercase, lowercase, and numbers
    password = field.data
    if not any(char.isupper() for char in password):
        raise ValidationError('Password needs at least one uppercase letter.')
    if not any(char.islower() for char in password):
        raise ValidationError('Password needs at least one lowercase letter.')
    if not any(char.isdigit() for char in password):
        raise ValidationError('Password needs at least one number.')
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters.')

class LoginForm(FlaskForm):
    # Login form with username and password
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=20, message="Username must be 3-20 characters.")
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    # Registration form for new users
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=20, message="Username must be 3-20 characters."),
        Regexp('^[A-Za-z0-9_]+$', message="Only letters, numbers, and underscores allowed.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        strong_password
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match.")
    ])
    submit = SubmitField('Register')

class PostForm(FlaskForm):
    # Form to create a new post
    content = TextAreaField('Write your post', validators=[
        DataRequired(), 
        Length(max=500, message="Post cannot exceed 500 characters.")
    ])
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    # Form to add comments
    content = TextAreaField('Write your comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')

class UpdateSettingsForm(FlaskForm):
    # Form to update username and password
    username = StringField('New Username', validators=[
        DataRequired(), 
        Length(min=2, max=20, message="Username must be 2-20 characters."),
        Regexp('^[A-Za-z0-9_]+$', message="Only letters, numbers, and underscores allowed.")
    ])
    password = PasswordField('New Password', validators=[
        DataRequired(),
        strong_password
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message="Passwords must match.")
    ])
    submit = SubmitField('Update Settings')
