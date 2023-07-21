from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import views
from controls import *
import os
from models import db, Users, Review

# set up flask
application = Flask(__name__)
# database Path
STATIC_PATH = os.path.join(os.path.dirname(__file__), 'static')

# specify the directory where you want to save uploaded files
application.config['UPLOAD_FOLDER'] = os.path.join(STATIC_PATH, 'images_post')
application.config['SECRET_KEY'] = SECRET_KEY
application.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

# database PostgreSQL connect
application.config["SQLALCHEMY_DATABASE_URI"] = KEYS_DB
db.init_app(application)


class UserView(ModelView):
    """hide password"""
    column_formatters = {
        'password': lambda v, c, m, p: '*' * 8  # m is the model instance
    }


admin = Admin(application, name='My Travel Admin', url="/myadminlink", template_mode='bootstrap3')
admin.add_view(UserView(Users, db.session))
admin.add_view(ModelView(Review, db.session))

# initialization views
views.init(application)

# create table
with application.app_context():
    db.create_all()

if __name__ == '__main__':
    application.run(port=5000, debug=False)
