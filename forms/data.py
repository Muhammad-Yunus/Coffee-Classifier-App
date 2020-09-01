from models.inferences import Upload
from models import db
from . import BaseView, expose
from . import os, secrets 
from . import request
from . import url_for
from . import datetime
from . import current_user
import traceback


def save_image_fs(form_image):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    image_fn = random_hex + f_ext
    image_path = os.path.join('static/image-upload', image_fn)

    form_image.save(image_path)

    return image_fn

def insert_image(self):
    try:
        image_fn = save_image_fs(request.files['image_file'])
        form = Upload(name=image_fn, upload_at = datetime.now(), upload_by = current_user.first_name)
        db.session.add(form)
        db.session.commit()
        show_feedback = True
        feedback_type = "success"
        feedback_message = "Image uploaded successfully!"
    except Exception:
        print(traceback.print_exc())
        image_fn = None
        show_feedback = False
        feedback_type = "danger"
        feedback_message = "Upload fail!"
    return show_feedback, feedback_type, feedback_message, image_fn

def delete_image(self):
    upload_id = request.form['upload_id']
    form = Upload.query.get(upload_id)
    db.session.delete(form)
    db.session.commit()
    feedback_message = "Image " + form.name + " deleted successfully!"
    return True, "success", feedback_message, None

def query_image(page,per_page):
    tableRecords = Upload().query.order_by(Upload.id.desc()).paginate(page,per_page,error_out=False)
    min_page_show = tableRecords.page - 2 if tableRecords.page - 2 > 0 else 1
    max_page_show = min_page_show + 5 if min_page_show + 5 <= tableRecords.pages + 1 else tableRecords.pages + 1
    count = Upload().query.count()
    return tableRecords, min_page_show, max_page_show, count 

class Data(BaseView):
    @expose('/', methods=['GET','POST'])
    def index(self):
        page = request.args.get('page')
        page = int(1 if page == None else page)
        per_page = 8 # number of record per page
        if request.method == "POST" :
            if 'image_file' in request.files :
                show_feedback, feedback_type, feedback_message, image_fn = insert_image(self)
            if 'upload_id' in request.form :
                show_feedback, feedback_type, feedback_message, image_fn = delete_image(self)
            tableRecords, min_page_show, max_page_show, count = query_image(page,per_page)
            return self.render('admin/data.html', 
                    show_feedback = show_feedback,
                    feedback_type = feedback_type,
                    feedback_message = feedback_message,
                    image_fn = image_fn, 
                    tableRecords = tableRecords, 
                    min_page_show = min_page_show, 
                    max_page_show = max_page_show, 
                    count = count)
        else :
            tableRecords, min_page_show, max_page_show, count = query_image(page,per_page)
            return self.render('admin/data.html',
                    show_feedback = False,
                    feedback_type = "",
                    feedback_message = "",
                    image_fn = None, 
                    tableRecords = tableRecords, 
                    min_page_show = min_page_show, 
                    max_page_show = max_page_show, 
                    count = count)
    
