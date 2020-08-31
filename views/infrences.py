from .custom_view import  MyModelView
from . import datetime
from . import current_user

class InferenceView(MyModelView):
    column_searchable_list = ['email', 'first_name', 'last_name']
    column_filters = ['email', 'first_name', 'last_name']
    column_exclude_list = ['password']

    column_labels = dict(first_name='First Name',
                        last_name='Last Name'
                        )
    
    def on_model_change(self, form, Inference, is_created):

        if is_created:
            Inference.run_at = datetime.now()
            Inference.run_by = current_user.first_name

    form_excluded_columns = ['run_at']
    


