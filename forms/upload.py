from models.uploads import Upload
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
    root_path = os.path.dirname(os.path.dirname(__file__))
    image_path = os.path.join(root_path, 'static/image-upload', image_fn)

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

def delete_image(upload_id):
    form = Upload().query.get(upload_id)
    db.session.delete(form)
    db.session.commit()
    feedback_message = "Image " + form.name + " deleted successfully!"
    return True, "success", feedback_message, None

def query_image(page,per_page, search_key="%%"):
    tableRecords = Upload().query.filter(Upload.name.like(search_key)).order_by(Upload.id.desc()).paginate(page,per_page,error_out=False)
    min_page_show = tableRecords.page - 2 if tableRecords.page - 2 > 0 else 1
    max_page_show = min_page_show + 5 if min_page_show + 5 <= tableRecords.pages + 1 else tableRecords.pages + 1
    count = Upload().query.filter(Upload.name.like(search_key)).count()
    return tableRecords, min_page_show, max_page_show, count
    
def image_name(upload_id):
    form = Upload().query.get(upload_id)
    image_fn = None
    if form != None:
        image_fn = form.name
    return image_fn


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

class UploadForm(BaseView):
    @expose('/', methods=['GET','POST'])
    def index(self):
        x = init(request.args.get('upload_id'), request.args.get('page'))

        if request.method == "POST" :
            if 'image_file' in request.files :
                x['show_feedback'], x['feedback_type'], x['feedback_message'] , x['image_fn'] = insert_image(self)
            if 'table_search' in request.form : 
                x['table_search'] = request.form["table_search"]
                x['search_key']  = "%{}%".format(x['table_search'])
            
            tableRecords, min_page_show, max_page_show, count = query_image(x['page'],x['per_page'], x['search_key'])
            return self.render('admin/upload.html', 
                    show_feedback = x['show_feedback'],
                    feedback_type = x['feedback_type'],
                    feedback_message = x['feedback_message'],
                    image_fn = x['image_fn'], 
                    tableRecords = tableRecords, 
                    min_page_show = min_page_show, 
                    max_page_show = max_page_show, 
                    count = count,
                    table_search = x['table_search'])

        else :
            tableRecords, min_page_show, max_page_show, count = query_image(x['page'],x['per_page'],x['search_key'])
            x['image_fn'] = image_name(x['upload_id'])
            return self.render('admin/upload.html', 
                    show_feedback = x['show_feedback'],
                    feedback_type = x['feedback_type'],
                    feedback_message = x['feedback_message'],
                    image_fn = x['image_fn'], 
                    tableRecords = tableRecords, 
                    min_page_show = min_page_show, 
                    max_page_show = max_page_show, 
                    count = count,
                    table_search = x['table_search'])

    @expose("/delete")
    def delete(self):
        x = init(request.args.get('upload_id'), request.args.get('page'))
        x['show_feedback'], x['feedback_type'], x['feedback_message'], x['image_fn'] = delete_image(x['upload_id'])
        tableRecords, min_page_show, max_page_show, count = query_image(x['page'],x['per_page'],x['search_key'])
        return self.render('admin/upload.html', 
                show_feedback = x['show_feedback'],
                feedback_type = x['feedback_type'],
                feedback_message = x['feedback_message'],
                image_fn = x['image_fn'], 
                tableRecords = tableRecords, 
                min_page_show = min_page_show, 
                max_page_show = max_page_show, 
                count = count,
                table_search = x['table_search'])   
    
