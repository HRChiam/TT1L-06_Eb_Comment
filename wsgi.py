from .app import app as _app

def create_app(config_name):
    #Create the app instance
    app = _app
    #Configure the app
    app.config.from_object(config_name)
    return app
