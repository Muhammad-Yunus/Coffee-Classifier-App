#!venv/bin/python
import os

from flask import Flask, url_for, redirect, render_template, request, abort
from flask_security import Security, SQLAlchemyUserDatastore, login_required, current_user
from flask_security.utils import encrypt_password
import flask_admin
from flask_admin import helpers as admin_helpers
from flask_admin import BaseView, AdminIndexView, expose

from models import db
from models.roles import Role 
from models.users import User
from models.inferences import Inference
from models.uploads import Upload 
from models.glcms import Glcm

from forms.custom_view import MyModelView 
from forms.users import UserView
from forms.profile import Profile
from forms.home import MyHomeView
from forms.infrences import InferenceForm, RunInferenceForm
from forms.upload import UploadForm
from forms.glcm import GlcmForm

app = Flask(__name__)
app.config.from_pyfile('config.py')

db.init_app(app)
db.app = app

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Flask views
@app.route('/')
def index():
    return render_template('index.html')

admin = flask_admin.Admin(
    app,
    'Coffee Bean Classifier',
    base_template='user_info.html',
    template_mode='bootstrap3',
    index_view=MyHomeView(),
    category_icon_classes={
        'Home': 'glyphicon glyphicon-home',
    }
)


# Add model views
admin.add_view(MyModelView(Role, db.session, menu_icon_type='fa', menu_icon_value='fa-server', name="Roles"))
admin.add_view(UserView(User, db.session, menu_icon_type='fa', menu_icon_value='fa-users', name="Users"))
admin.add_view(Profile(name="Profile", endpoint='profile'))
admin.add_view(UploadForm(name="Upload", menu_icon_type='fa', menu_icon_value='fa-upload', endpoint='upload'))
admin.add_view(GlcmForm(name="GLCM", menu_icon_type='fa', menu_icon_value='fa-braille', endpoint='glcm'))
admin.add_view(RunInferenceForm(name="Run Inference", menu_icon_type='fa', menu_icon_value='fa-bar-chart', endpoint='run_inference'))
admin.add_view(InferenceForm(Inference, db.session, menu_icon_type='fa', menu_icon_value='fa-database', name="History"))

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

# @app.cli.command()
def build_sample_db():
    """
    Populate a small db with some example entries.
    """
    import string
    import random

    db.drop_all()
    db.create_all()

    with app.app_context():
        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.commit()

        test_user = user_datastore.create_user(
            first_name='Admin',
            email='admin',
            password=encrypt_password('admin'),
            roles=[user_role, super_user_role]
        )

        db.session.commit()
    return

if __name__ == '__main__':

    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])

    if not os.path.exists(database_path):
        build_sample_db()
    
    # Start app
    app.run(host='0.0.0.0', debug=True)