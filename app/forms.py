from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class UploadForm(FlaskForm):
    photo = FileField('Upload Image', validators=[
        FileRequired('Image is Required.'),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only images (.jpg, .jpeg, .png) are allowed!')
    ])
    submit = SubmitField('Upload')