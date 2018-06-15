from functools import wraps
from flask import abort
from app import db
from flask_login import UserMixin, current_user, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

'''
Articles, Divisions
'''


class Division(db.Model):
    __tablename__ = 'divisions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    articles = db.relationship('Article', backref='div', lazy='dynamic')

    def __repr__(self):
        return '<Division %r>' % self.name

    def __str__(self):
        return self.name

    @staticmethod
    def insert_divs():
        div_list = ['World', 'Entertainment', 'Technology', 'Sport']
        for div in div_list:
            cur_div = Division.query.filter_by(name=div).first()
            if cur_div is None:
                cur_div = Division(name=div)
                db.session.add(cur_div)
        db.session.commit()




class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    content = db.Column(db.Text, unique=True)
    upload_time = db.Column(db.String(64))
    uploaded_by = db.Column(db.String(64))
    div_name = db.Column(db.String(64))
    pic = db.Column(db.Text, default='https://www.cryptonetix.com/wp-content/uploads/2018/02/cryptonetix-default.jpg')
    div_id = db.Column(db.Integer, db.ForeignKey('divisions.id'))


    def __repr__(self):
        return '<Article %r>' % self.name




'''
Users, Roles
'''


class Permissions:
    monitor_articles = 1   # journalist
    monitor_divisions = 3   # moderator
    monitor_users = 5  # admin full control


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    permission = db.Column(db.Integer)

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        Roles = {'User': 2, 'Moderator': 4, 'Admin': 6}
        for role in Roles:
            cur_role = Role.query.filter_by(name=role).first()
            if cur_role is None:
                cur_role = Role(name=role)
                db.session.add(cur_role)
            cur_role.permission = Roles.get(role)
            db.session.commit()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, permission):
        return self.role is not None and (self.role.permission > permission)

    def is_administrator(self):
        return self.role is not None and (self.role.permission > Permissions.monitor_users)

    def is_moderator(self):
        return self.role is not None and (self.role.permission > Permissions.monitor_divisions)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permission):
        return False
    def is_administrator(self):
        return False


'''
Authentication decorators
'''

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(Permissions.monitor_users)(f)

