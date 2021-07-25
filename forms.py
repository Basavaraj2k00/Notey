from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL,Email,Length
from flask_ckeditor import CKEditorField


class RegisterForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired('Please enter your email.'),Email("Please enter correct email address.")])
    password = PasswordField(label="Password", validators=[DataRequired('Please enter your password.'),Length(min=8, max=35,message="Password must be between 8 and 35 characters long")])
    name = StringField(label="Name", validators=[DataRequired('Please enter your name.')])
    submit = SubmitField("Sign Me Up!")

class LoginForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired('Please enter your email.'),Email("Please enter correct email address.")])
    password = PasswordField(label="Password", validators=[DataRequired('Please enter your password.'),Length(min=8, max=35,message="Password must be between 8 and 35 characters long")])
    submit = SubmitField("Let Me In!")