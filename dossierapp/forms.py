from re import RegexFlag
from tokenize import String
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,TextAreaField,SelectField,EmailField
from flask_wtf.file import FileField, FileRequired,FileAllowed
from wtforms.validators import DataRequired,Email,Length,EqualTo,Regexp,NumberRange,InputRequired,email_validator





class SignupForm(FlaskForm):
    fullname = StringField("Your Fullname:", validators = [DataRequired(message="All field is required")])
    email = StringField("Email:", validators = [Email('please enter a valid email'),DataRequired('all field is required')])
    password = PasswordField("Password:", validators = [DataRequired('All field is required'),Length(min = 8), Regexp('^(?=.*[a-z])(?=.*[A-Z](?=.*\\d)[a-zA-Z\\d]+$)')])
    confirm_password = PasswordField("Confirm Password:", validators =[DataRequired('all field is required'), EqualTo('regexp')])
    phone = StringField("Phone Number:", validators = [DataRequired('All field is required'), Length(max = 11)])
    dept = SelectField("Department:", choices = [('value 1', 'option1'), ('value 2', 'option 2'), ('value 3', 'option 3')])
    office = SelectField("Post:", choices = [('value 1', 'option1'), ('value 2', 'option 2'), ('value 3', 'option 3')])
    submit = SubmitField('Register')
