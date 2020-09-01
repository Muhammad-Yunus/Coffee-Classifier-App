from .custom_view import  MyModelView
from . import encrypt_password
from . import datetime

class UserView(MyModelView):
    column_searchable_list = ['email', 'first_name', 'last_name']
    column_filters = ['email', 'first_name', 'last_name']
    column_exclude_list = ['password']

    column_labels = dict(first_name='First Name',
                        last_name='Last Name'
                        )
    
    def on_model_change(self, form, User, is_created):
        if form.password.data is not None:
            User.password = encrypt_password(form.password.data)
        else:
           del form.password

        if is_created:
            User.confirmed_at = datetime.now()


    def on_form_prefill(self, form, id):
        form.password.data = '' 
        # form.confirmed_at.render_kw = {'readonly': True}   
    
    form_widget_args = {
        'password': {
            'type': 'password'
        }
    }
    form_excluded_columns = ['confirmed_at']
    # form_columns = ['email', 'first_name', 'last_name', 'roles']

    # # column_details_exclude_list = column_exclude_list
    # # column_details_list = ['email', 'first_name', 'last_name', 'roles']
    


