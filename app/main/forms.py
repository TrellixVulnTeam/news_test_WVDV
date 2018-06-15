from flask_wtf import Form
from wtforms import StringField, SubmitField, SelectField, TextAreaField, BooleanField, PasswordField, ValidationError
from wtforms.validators import Required, Length, EqualTo, Regexp
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from ..models import Division, User


'''
Forms
'''
def create_div_list():
    divs = list()       # list contains drop down choices for the form(s) below
    for div in Division.query.order_by(Division.id).all():
        divs.append((div.name, div.name))


class AddForm(Form):  # used for both add/edit article
    division = QuerySelectField(label="Division: ", validators=[Required()])
    article = StringField("Title: ", validators=[Required()])
    pic = StringField("Link of the profile picture: ")
    content = TextAreaField("Content: ")
    submit = SubmitField("Submit")


class SearchArticle(Form):
    name = StringField(label='')


class DivForm(Form):
    name = StringField(label='Name:', validators=[Required()])
    submit = SubmitField('Submit')


class LoginForm(Form):
    username = StringField('Username: ', validators=[Required(), Length(1, 64)])
    password = PasswordField('Password: ', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                                         'Username must have only letters, '
                                                                                         'numbers, dots or underscores')])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class SignupForm(Form):
    role_choices = [('User', 'User'), ('Moderator', 'Moderator'), ('Admin', 'Administrator')]

    username = StringField('Username: ', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                          'Username must have only letters, '
                                                                          'numbers, dots or underscores')])
    role_name = SelectField('Role: ', choices=role_choices)
    password = PasswordField('Password: ', validators=[Required()])
    retype_password = PasswordField('Retype password: ', validators=[Required(),
                                                                     EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('This username has already been taken.')


class EditUserForm(Form):
    role_choices = [('User', 'User'), ('Moderator', 'Moderator'), ('Admin', 'Administrator')]

    role_name = SelectField('Role: ', choices=role_choices)

    submit = SubmitField('Save')




