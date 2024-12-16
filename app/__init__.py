from flask import Flask

def create_app():
    app = Flask(__name__)
    with app.app_context():
        from .routes import main

        # Register only the main blueprint
        app.register_blueprint(main)
    return app
