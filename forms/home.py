from models import db
from models.inferences import Inference
from models.uploads import Upload
from models.glcms import Glcm
from models.ml_model import MLModel, ModelReport, TrainigHistory
from . import AdminIndexView, expose 
from . import request
from . import datetime
from . import current_user
from . import os

# Home views
class MyHomeView(AdminIndexView):

    def is_visible(self):
        # This view won't appear in the menu structure
        return False

    @expose('/')
    def index(self):
        uploaded_image = Upload().query.count()
        generated_glcm = Glcm().query.count()
        inference_result = Inference().query.count()
        model = MLModel().query.count()

        card = {
            'uploaded_image' : uploaded_image,
            'generated_glcm' : generated_glcm,
            'inference_result' : inference_result,
            'model' : 1
        }
        return self.render('admin/home.html',
                            card = card)