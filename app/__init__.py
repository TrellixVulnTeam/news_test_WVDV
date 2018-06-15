from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from config import config
from flask_login.login_manager import LoginManager


bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'page.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    with app.app_context():
        db.init_app(app)

    from app.main import page as page_blueprint
    app.register_blueprint(page_blueprint)

    login_manager.init_app(app)

    from app.models import User
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)

    @app.context_processor
    def inject_divisions():
        from app.models import Division, Article
        from random import randint
        div_list = list()  # list contains all the divisions
        for div in Division.query.order_by(Division.id).all():
            div_list.append(div.name)

        editors_picks = dict()
        total_articles = list()
        for div in div_list:
            for article in Division.query.filter_by(name=div).first().articles:
                total_articles.append(article)
            editors_picks[div] = list()
            for i in range(4):
                article = total_articles[randint(0, len(total_articles)-1)]
                while article in editors_picks[div]:
                    article = total_articles[randint(0, len(total_articles)-1)]
                editors_picks[div].append(article)
                total_articles.remove(article)

        editors_picks['Home'] = list()
        for i in range(4):
            total_articles = Article.query.count()
            article = Article.query.get(randint(0, total_articles))
            while article in editors_picks['Home']:
                article = Article.query.get(randint(0, total_articles))
            editors_picks['Home'].append(article)
        breaking_news = Article.query.get(randint(0, total_articles))

        main_posts = list()
        for i in range(3):
            total_articles = Article.query.count()
            article = Article.query.get(randint(0, total_articles))
            while article in main_posts:
                article = Article.query.get(randint(0, total_articles))
            main_posts.append(article)

        return dict(div_list=div_list, main_posts=main_posts, editors_picks=editors_picks, breaking_news=breaking_news)

    return app

