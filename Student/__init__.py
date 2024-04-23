from flask import Flask

def create_web():
    web = Flask(__name__)
    web.config['SECRET_KEY'] = 'ebcomment'

    from .views import views

    web.register_blueprint(views, url_prefix='/')

    return web