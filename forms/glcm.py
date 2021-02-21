from core_ml.main import calc_glcm_core

from models import db
from models.glcms import Glcm
from models.uploads import Upload
from models.inferences  import Inference
from . import BaseView, expose 
from . import request
from . import datetime
from . import current_user
from . import np
import os

def query_upload(page,per_page, search_key="%%"):
    tableRecords = Upload().query.filter(Upload.name.like(search_key)) \
                    .filter(Upload.is_used) \
                    .order_by(Upload.id.desc()).paginate(page,per_page,error_out=False)
    min_page_show = tableRecords.page - 2 if tableRecords.page - 2 > 0 else 1
    max_page_show = min_page_show + 5 if min_page_show + 5 <= tableRecords.pages + 1 else tableRecords.pages + 1
    count = Upload().query.filter(Upload.name.like(search_key)) \
                    .filter(Upload.is_used).count()

    print("[INFO] tableRecords count ", count)
    return tableRecords, min_page_show, max_page_show, count 

def query_glcm(upload_id):
    tableRecords = Glcm().query.filter(Glcm.Upload_Id == upload_id)
    print("[INFO] query glcm ...", type(tableRecords))
    selectedImage = None
    form = Upload.query.get(upload_id)
    if form != None:
        selectedImage = form.name
    return tableRecords,  selectedImage

def delete_glcm(upload_id):
    tableRecords = Glcm().query.filter(Glcm.Upload_Id == upload_id)
    for record in tableRecords:
        db.session.delete(record)
        db.session.commit()

    form = Upload.query.get(upload_id)
    form.is_used = False
    db.session.add(form)
    db.session.commit()
    feedback_message = "GLCM generated from image " + form.name + " deleted successfully!"
    return True, "success", feedback_message

def calc_glcm(upload_id):
    form = Upload.query.get(upload_id)
    print("[INFO] clac glcm starting...", upload_id, form.name)
    features = calc_glcm_core("static/image-upload/" + form.name)
    records = [Glcm(
                angel=int(angel), 
                dissimilarity = features[angel]['dissimilarity'],
                correlation = features[angel]['correlation'],
                homogeneity = features[angel]['homogeneity'],
                contrast = features[angel]['contrast'],
                ASM = features[angel]['ASM'],
                energy = features[angel]['energy'],
                calc_at = datetime.now(),
                calc_by = current_user.first_name,
                Upload_Id = upload_id
                ) for angel in features]     

    #insert to GLCM table
    for record in records:
        db.session.add(record)
        db.session.commit()

    
    form.is_used = True
    db.session.commit()
    
    feedback_message = "GLCM generated from image " + form.name + " created successfully!"
    return True, "success", feedback_message 

def init(upload_id, page):
    upload_id = int(0 if upload_id == None else upload_id)
    page = int(1 if page == None else page)

    return { 'upload_id' : upload_id,
             'page' : page,
             'per_page' : 8,
             'table_search' : "",
             'search_key' : "%%",
             'show_feedback' : False, 
             'feedback_type' : "", 
             'feedback_message' : "", 
             'image_fn' : None
            }

def has_inference(upload_id):
    count = Inference().query.filter(Inference.Upload_Id == upload_id).count()
    print ("[INFO] Inference count : ", count)
    return True if count > 0 else False

class GlcmForm(BaseView):
    @expose('/', methods=['GET','POST'])
    def index(self): 
        x = init(request.args.get('upload_id'), request.args.get('page'))
        
        if request.method == "POST" :
            if 'table_search' in request.form : 
                x['table_search'] = request.form["table_search"]
                x['search_key']  = "%{}%".format(x['table_search'])
            
        tableRecords, min_page_show, max_page_show, count = query_upload(x['page'],x['per_page'], x['search_key'])
        glcmRecords, selectedImage = query_glcm(x['upload_id'])
        return self.render('admin/glcm.html', 
                    show_feedback = x['show_feedback'],
                    feedback_type = x['feedback_type'],
                    feedback_message = x['feedback_message'],
                    glcmRecords = glcmRecords,
                    selectedImage = selectedImage,
                    tableRecords = tableRecords, 
                    min_page_show = min_page_show, 
                    max_page_show = max_page_show, 
                    count = count,
                    table_search = x['table_search'],
                    has_inference = has_inference(x['upload_id']))
    
    @expose('/delete')
    def delete(self):
        x = init(request.args.get('upload_id'), request.args.get('page'))
        
        # delete GLCM by upload_id
        x['show_feedback'], x['feedback_type'], x['feedback_message'] = delete_glcm(x['upload_id'])

        tableRecords, min_page_show, max_page_show, count = query_upload(x['page'],x['per_page'], x['search_key'])
        glcmRecords, selectedImage = query_glcm(x['upload_id'])
        return self.render('admin/glcm.html', 
                    show_feedback = x['show_feedback'],
                    feedback_type = x['feedback_type'],
                    feedback_message = x['feedback_message'],
                    glcmRecords = glcmRecords,
                    selectedImage = selectedImage,
                    tableRecords = tableRecords, 
                    min_page_show = min_page_show, 
                    max_page_show = max_page_show, 
                    count = count,
                    table_search = x['table_search'],
                    has_inference = has_inference(x['upload_id']))

    @expose('/calc')
    def calc(self):
        x = init(request.args.get('upload_id'), request.args.get('page'))
        recalc = request.args.get('recalc') 
        recalc = int(1 if recalc == None else recalc)

        if recalc == 1 :
            x['show_feedback'], x['feedback_type'], x['feedback_message'] = delete_glcm(x['upload_id'])

        # calc GLCM by upload_id
        records, __ = query_glcm(x['upload_id'])
        if records.first() == None :
            x['show_feedback'], x['feedback_type'], x['feedback_message'] = calc_glcm(x['upload_id'])

        tableRecords, min_page_show, max_page_show, count = query_upload(x['page'],x['per_page'], x['search_key'])
        glcmRecords, selectedImage = query_glcm(x['upload_id'])
        return self.render('admin/glcm.html', 
                    show_feedback = x['show_feedback'],
                    feedback_type = x['feedback_type'],
                    feedback_message = x['feedback_message'],
                    glcmRecords = glcmRecords,
                    selectedImage = selectedImage,
                    tableRecords = tableRecords, 
                    min_page_show = min_page_show, 
                    max_page_show = max_page_show, 
                    count = count,
                    table_search = x['table_search'],
                    has_inference = has_inference(x['upload_id']))