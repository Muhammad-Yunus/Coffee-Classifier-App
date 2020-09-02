from models import db
from models.inferences import Inference
from models.uploads import Upload
from models.glcms import Glcm
from .custom_view import  MyModelView
from . import BaseView, expose 
from . import request
from . import datetime
from . import current_user
from . import np
import ast

class InferenceForm(MyModelView):
    column_exclude_list = ['result_dict']
    def on_model_change(self, form, Inference, is_created):

        if is_created:
            Inference.run_at = datetime.now()
            #Inference.run_by = current_user.first_name

    form_excluded_columns = ['run_at', 'run_by']
    
def query_glcm(upload_id):
    tableRecords = Glcm().query.filter(Glcm.Upload_Id == upload_id)
    print("[INFO] query glcm ...", type(tableRecords))
    selectedImage = None
    form = Upload.query.get(upload_id)
    if form != None:
        selectedImage = form.name
    return tableRecords,  selectedImage

def run_inference(upload_id):
    inference = {
        "Dark Coffee" : 95,
        "Light Coffee" : 14,
        "Medium Coffee" : 15,
        "Medium Dark Coffee" : 21,
        "result" : "Dark Coffee"
    }
    return inference, inference['result'], inference[inference['result']]

def insert_inference(data):
    form = Inference(Upload_Id = data['upload_id'], 
                    result_dict = data['result_dict'], 
                    result_label = data['result_label'], 
                    confidence=data['confidence'], 
                    run_at=datetime.now(), 
                    run_by=current_user.first_name)
    db.session.add(form)
    db.session.commit()

    feedback_message = "Inference data created successfully!"
    return True, "success", feedback_message, form.id

def select_inference(inference_id):
    form = Inference().query.get(inference_id)
    return form

def init(upload_id, inference_id):
    upload_id = int(0 if upload_id == None else upload_id)
    inference_id = int(0 if inference_id == None else inference_id)

    return { 'inference_id' : inference_id,
             'upload_id' : upload_id,
             'show_feedback' : False, 
             'feedback_type' : "", 
             'feedback_message' : "", 
             'image_fn' : None
            }
            
class RunInferenceForm(BaseView):

    @expose("/")
    def index(self):
        x = init(request.args.get('upload_id'), request.args.get('inference_id'))

        formInference = select_inference(x['inference_id'])
        if formInference is not None :
            x['upload_id'] = formInference.Upload_Id
            result_dict, result_label, confidence = \
                ast.literal_eval(formInference.result_dict), formInference.result_label, formInference.confidence
        else :
            result_dict, result_label, confidence = None, None, None
        glcmRecords, selectedImage = query_glcm(x['upload_id'])
        return self.render('admin/inference.html',
                    show_feedback = x['show_feedback'],
                    feedback_type = x['feedback_type'],
                    feedback_message = x['feedback_message'],
                    glcmRecords = glcmRecords,
                    selectedImage = selectedImage, 
                    result_dict = result_dict,
                    result_label = result_label, 
                    confidence = confidence)

    @expose("/run")
    def run(self):
        x = init(request.args.get('upload_id'), request.args.get('inference_id'))

        formInference = select_inference(x['inference_id'])
        if formInference == None :
            result_dict, result_label, confidence = run_inference(x['upload_id'])
            data = {
                'upload_id': x['upload_id'],
                'result_dict': str(result_dict),
                'result_label': result_label,
                'confidence': confidence
            }
            x['show_feedback'], x['feedback_type'], x['feedback_message'], x['inference_id'] = insert_inference(data)
            formInference = select_inference(x['inference_id'])

        glcmRecords, selectedImage = query_glcm(x['upload_id'])
        return self.render('admin/inference.html',
                    show_feedback = x['show_feedback'],
                    feedback_type = x['feedback_type'],
                    feedback_message = x['feedback_message'],
                    glcmRecords = glcmRecords,
                    selectedImage = selectedImage, 
                    result_dict = ast.literal_eval(formInference.result_dict),
                    result_label = formInference.result_label, 
                    confidence = formInference.confidence)