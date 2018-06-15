from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from app import db
from ..models import Division, Article, permission_required, admin_required, Permissions,  Role
from .forms import AddForm, DivForm, User, LoginForm, SignupForm, EditUserForm
from flask_login import login_required, login_user, logout_user, current_user
from random import randint

from . import page

'''
Frontend
'''


@page.route('/')
def home():
    latest_posts = Article.query.order_by(Article.id.desc())[0:4]
    popular_posts = Article.query.order_by(Article.id)[0:3]   # oldest posts for now
    return render_template('frontend/abc.html', latest_posts=latest_posts, popular_posts=popular_posts)


@page.route('/single_page/<id>')
def single_page(id):
    news = Article.query.filter_by(id=id).first_or_404()
    return render_template('frontend/image-post.html', news=news)


@page.route('/<div>')
def division(div):
    div_list = list()  # list contains all the divisions
    for div in Division.query.order_by(Division.id).all():
        div_list.append(div.name)
    if div not in div_list:
        return render_template('404.html')
    division = Division.query.filter_by(name=div).first()
    latest_posts = Article.query.filter_by(div=division).order_by(Article.id.desc()).all()[0:8]
    if latest_posts:
        return render_template('frontend/category.html', latest_posts=latest_posts, div_name=div)
    return render_template('frontend/category.html', message="There has not been any article yet!")


'''
Backend
'''


@page.route('/add', methods=['GET', 'POST'])
@login_required
@permission_required(Permissions.monitor_articles)
def add():
    form = AddForm()
    my_query = Division.query.all()
    form.division.query = my_query
    if form.validate_on_submit():
        pic = None
        division_name = form.division.data
        article_name = form.article.data
        content = form.content.data
        if form.pic.data is not '':
            pic = form.pic.data

        division = Division.query.filter_by(name=division_name).first()
        article = Article.query.filter_by(name=article_name).first()
        if article!=None:
            flash("This article has already been existing.%s")
            return redirect(url_for('page.add'))
        article = Article(name=article_name, div=division, uploaded_by=current_user.username, div_name=division_name,
                          content=content, upload_time=datetime.now().strftime('%H:%M | %d-%m-%Y'))
        if pic is not None:
            article.pic = pic
        db.session.add(article)
        flash("Article %s added successfully!" % article_name)
        return redirect(url_for('page.monitor'))
    # divs = list()  # list contains drop down choices for the form(s) below
    # for div in Division.query.order_by(Division.id).all():
    #     divs.append((div.name, div.name))
    # form.division.data = divs
    return render_template('add.html', form=form)


@page.route('/delete/<id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permissions.monitor_articles)
def delete(id):
    article = Article.query.filter_by(id=id).first_or_404()
    article_name=article.name
    db.session.delete(article)
    flash("Article %s deleted successfully!"%article_name)
    return redirect(url_for('page.monitor'))


@page.route('/monitor')
@login_required
@permission_required(Permissions.monitor_articles)
def monitor():
    div_list = list()  # list contains all the divisions
    divs = list()  # list contains drop down choices for the form(s) below
    for div in Division.query.order_by(Division.id).all():
        div_list.append(div.name)
    divs = dict()   # a list of lists of articles of a division
    for div in div_list:
        a_division = Division.query.filter_by(name=div).first()
        articles = Article.query.filter_by(div=a_division).all()
        if articles:
            divs[div] = articles
        else:
            divs[div] = list()
    return render_template('monitor.html', divs=divs)


@page.route('/adddiv', methods=['GET', 'POST'])
@login_required
@permission_required(Permissions.monitor_divisions)
def add_div():
    form = DivForm()
    if form.validate_on_submit():
        div=form.name.data
        if Division.query.filter_by(name=div).first():
            flash('This division is existing already!')
            return redirect(url_for('page.add_div'))
        new_div=Division(name=div)
        db.session.add(new_div)
        flash('Category %s added successfully!' %div)
        return redirect(url_for('page.div_monitor'))
    return render_template('backend/add_div.html', form=form)


@page.route('/editdiv/<id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permissions.monitor_divisions)
def edit_div(id):
    div = Division.query.get_or_404(id)
    form = DivForm()
    if form.validate_on_submit():
        div = Division.query.get(id)
        div.name = form.name.data
        return redirect(url_for('page.edit_div', id=id))
    else:
        form.name.data=div.name
    num_of_articles=div.articles.count()
    return render_template('backend/edit_div.html', form=form, name=form.name.data, num_of_articles=num_of_articles)


@page.route('/deletediv/<name>', methods=['GET', 'POST'])
@login_required
@permission_required(Permissions.monitor_divisions)
def delete_div(name):
    div = Division.query.filter_by(name=name).first_or_404()
    div_name = div.name
    for article in div.articles.all():
        db.session.delete(article)
    db.session.delete(div)
    flash("Category %s deleted successfully!" % div_name)
    return redirect(url_for('page.div_monitor'))


@page.route('/divmonitor')
@login_required
@permission_required(Permissions.monitor_divisions)
def div_monitor():
    divs = Division.query.all()
    num_articles = dict()
    div_list = list()  # list contains all the divisions
    for div in Division.query.order_by(Division.id).all():
        div_list.append(div.name)
    for div in div_list:
        num = Division.query.filter_by(name=div).first().articles.count()
        num_articles[div] = num
    return render_template('backend/div_monitor.html', divs=divs, num_articles=num_articles )


@page.route('/div_layout/<id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permissions.monitor_divisions)
def div_layout(id):
    div = Division.query.get_or_404(id)
    pass


@page.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permissions.monitor_articles)
def edit(id):
    form = AddForm()
    my_query = Division.query.all()
    form.division.query = my_query
    article = Article.query.filter_by(id=id).first_or_404()
    if form.validate_on_submit():
        article.name = form.article.data
        division = Division.query.filter_by(name=form.division.data).first()
        article.div = division
        article.div_name = form.division.data
        article.content = form.content.data
        if form.pic.data is not None and form.pic.data is not '':
            article.pic = form.pic.data
        flash("Article edited successfully!")
        return redirect(url_for('page.edit', id=id))
    else:
        form.article.data=article.name
        form.division.data=article.div
        form.content.data=article.content
        form.pic.data = article.pic
    return render_template('edit.html', form=form, name=article.name, id=article.id)


@page.route('/test')
def test():
    return "Hello World"


@page.app_errorhandler(404)
def file_not_found(e):
    return render_template('404.html'), 404


@page.route('/users_monitor')
@login_required
@admin_required
def users_monitor():
    roles = Role.query.all()
    users = dict()
    roles_list = list()
    for role in roles:
        users[role.name] = User.query.filter_by(role=role).all()
        roles_list.append(role.name)
    return render_template('backend/users_monitor.html', roles_list=roles_list, users=users)


@page.route('/add_user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        role = Role.query.filter_by(name=form.role_name.data).first()
        password = form.password.data
        new_user = User(username=username, role=role, password=password)
        db.session.add(new_user)
        flash("User %s registered successfully!" % username)
        return redirect(url_for('page.users_monitor'))
    return render_template('backend/add_user.html', form=form)


@page.route('/edit_user/<id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    form = EditUserForm()
    user = User.query.get_or_404(id)
    if form.validate_on_submit():
        role = Role.query.filter_by(name=form.role_name.data)
        user.role = role
        return redirect(url_for('page.edit_user'))
    form.role_name.data = user.role.name
    return render_template('backend/edit_user.html', form=form, user=user)


@page.route('/delete_user/<id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    username = user.username
    db.session.delete(user)
    flash("User %s deleted successfully!" % username)
    return redirect(url_for('page.users_monitor'))



@page.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('page.monitor'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)


@page.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.")
    return redirect(url_for('page.login'))


