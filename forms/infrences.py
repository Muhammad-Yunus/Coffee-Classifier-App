from models import db
from models import or_
from models.inferences import Inference
from models.uploads import Upload
from models.glcms import Glcm
from .custom_view import  MyModelView
from . import BaseView, expose 
from . import request, send_file
from . import datetime
from . import current_user
from . import np
from . import os
import ast
import csv

class InferenceForm(BaseView):
    @expose("/", methods = ["GET", "POST"])
    def index(self):
        page = request.args.get('page')
        page = int(1 if page == None else page)
        per_page = 10

        table_search = ""
        search_key = "%%"

        if request.method == "POST" :
            if 'table_search' in request.form : 
                table_search = request.form["table_search"]
                search_key = "%{}%".format(table_search)

        tableRecords = db.session.query(
                                Upload, Inference
                                ).filter(
                                    Upload.id == Inference.Upload_Id
                                ).filter(
                                    or_(
                                        Upload.name.like(search_key),
                                        Inference.result_label.like(search_key)
                                    )
                                ).paginate(page,per_page,error_out=False)
        min_page_show = tableRecords.page - 2 if tableRecords.page - 2 > 0 else 1
        max_page_show = min_page_show + 5 if min_page_show + 5 <= tableRecords.pages + 1 else tableRecords.pages + 1
        count = db.session.query(
                                Upload, Inference
                                ).filter(
                                    Upload.id == Inference.Upload_Id
                                ).filter(
                                    or_(
                                        Upload.name.like(search_key),
                                        Inference.result_label.like(search_key)
                                    )
                                ).count()

        return self.render('admin/inference.html',
                        tableRecords=tableRecords,                
                        min_page_show = min_page_show, 
                        max_page_show = max_page_show, 
                        count = count,
                        table_search = table_search) 
                
    @expose("/download/<filename>")
    def download(self, filename):
        tableRecords = db.session.query(
                                Upload, Inference
                                ).filter(
                                    Upload.id == Inference.Upload_Id
                                ).all()

        root_path = os.path.dirname(os.path.dirname(__file__))
        csv_path = os.path.join(root_path, 'static/csv-download', filename)
        outfile = open(csv_path, 'w+')
        outcsv = csv.writer(outfile)
        # dump column titles (optional)
        outfile.write( ('%20s, %20s, %11s, %20s, %10s') % ('Image', 'Result Label', 'Confidence', 'Run At', 'Run By\n'))
        for record in tableRecords:
            outfile.write(('%20s, %20s, %11s, %20s, %10s') % (record.Upload.name, record.Inference.result_label , str(record.Inference.confidence), record.Inference.run_at.strftime("%m/%d/%Y %H:%M:%S"), record.Inference.run_by + '\n'))

        outfile.close()
        response = send_file(csv_path, attachment_filename=filename, as_attachment=True, mimetype='text/csv')
        return response

    @expose("/image_download/<filename>")
    def image_download(self, filename):
        root_path = os.path.dirname(os.path.dirname(__file__))
        image_path = os.path.join(root_path, 'static/image-upload', filename)
        response = send_file(image_path, attachment_filename=filename, as_attachment=True)
        return response
    
    @expose("/glcm_download/<filename>")
    def glcm_download(self, filename):
        image_name = filename.replace(".csv", "").replace("GLCM_Image_", "")
        form = Upload().query.filter(Upload.name == image_name).first()
        tableRecords = Glcm().query.filter(Glcm.Upload_Id == form.id).all()

        root_path = os.path.dirname(os.path.dirname(__file__))
        csv_path = os.path.join(root_path, 'static/csv-download', filename)
        outfile = open(csv_path, 'w+')
        outcsv = csv.writer(outfile)
        # dump column titles (optional)
        outfile.write( ('%20s, %15s, %15s, %15s, %15s, %15s, %15s, %15s') % ('Image', 'Angel', 'Dissimilarity', 'Correlation', 'Homogeneity', 'Contrast', 'ASM', 'Energy\n'))
        for record in tableRecords:
            outfile.write(('%20s, %15s, %15s, %15s, %15s, %15s, %15s, %15s') % (form.name, str(record.angel) , str(record.dissimilarity), str(record.correlation), str(record.homogeneity), str(record.contrast), str(record.ASM), str(record.energy) + '\n'))

        outfile.close()
        response = send_file(csv_path, attachment_filename=filename, as_attachment=True, mimetype='text/csv')
        return response




#################################################################################################################

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
        return self.render('admin/run_inference.html',
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
        return self.render('admin/run_inference.html',
                    show_feedback = x['show_feedback'],
                    feedback_type = x['feedback_type'],
                    feedback_message = x['feedback_message'],
                    glcmRecords = glcmRecords,
                    selectedImage = selectedImage, 
                    result_dict = ast.literal_eval(formInference.result_dict),
                    result_label = formInference.result_label, 
                    confidence = formInference.confidence)