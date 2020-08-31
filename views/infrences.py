from .custom_view import  MyModelView
from . import datetime

class InferenceView(MyModelView):
    column_searchable_list = ['model_name']
    column_filters = ['model_name']
    
    def on_model_change(self, form, Inference, is_created):

        if is_created:
            Inference.run_at = datetime.now()
            #Inference.run_by = current_user.first_name

    form_excluded_columns = ['run_at', 'run_by']
    


