from . import BaseView, expose
from . import request
from models.users import User
from models import db

class Profile(BaseView):
    @expose('/')
    def index(self):
        user_id = request.args.get('user_id')
        if user_id != None:
            profileData = User.query.filter_by(id=user_id).first()
            profileData.last_name = '' if profileData.last_name == None else profileData.last_name
            return self.render('admin/profile.html', profileData = profileData, show_feedback_success = False)
        else :
            return self.render('admin/about.html')
    def is_visible(self):
        return False
    
    @expose('/', methods=('GET', 'POST'))
    def on_model_change(self):
        id_ = request.args.get('user_id')

        if id_ != None:
            user_id = request.form['id']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            active = True if request.form['active'] == 'on' else False
            UserUpdate = None
            UserSave = None
            UserUpdate = User.query.filter_by(id=user_id).first()
            UserUpdate.first_name = first_name
            UserUpdate.last_name = last_name
            UserUpdate.email = email
            UserUpdate.active = active

            db.session.merge(UserUpdate)

            db.session.flush()
            db.session.refresh(UserUpdate)
            user_id = UserUpdate.id

            db.session.commit()
            return self.render('admin/profile.html', 
                profileData = (UserUpdate if UserUpdate is not None else UserSave), 
                show_feedback_success = True)
        else :
            return self.render('admin/about.html')
        