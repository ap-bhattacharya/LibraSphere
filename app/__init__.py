from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/book_manager'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'your_secret_key'

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import and register blueprints
    from app.controllers.auth_controller import auth_blueprint
    from app.controllers.book_controller import book_blueprint
    from app.controllers.user_controller import user_blueprint

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    print("Registered auth_blueprint at /auth")

    app.register_blueprint(book_blueprint, url_prefix='/books')
    print("Registered book_blueprint at /books")

    app.register_blueprint(user_blueprint, url_prefix='/users')
    print("Registered user_blueprint at /users")

    return app
