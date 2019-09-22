from flask import Flask
from config import Config
<<<<<<< Updated upstream
||||||| merged common ancestors
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
=======
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
>>>>>>> Stashed changes

app = Flask(__name__)
app.config.from_object(Config)
<<<<<<< Updated upstream
||||||| merged common ancestors
db = SQLAlchemy(app)
migrate = Migrate(app, db)
=======
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
>>>>>>> Stashed changes

from app import routes
