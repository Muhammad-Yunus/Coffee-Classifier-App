from models import db
from models.ml_model import MLModel, ModelReport, TrainigHistory
from . import BaseView, expose 
from . import request
from . import datetime
from . import current_user
from . import os
from . import pd

class MLModelForm(BaseView):
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

        tableRecords = MLModel().query \
                                .filter(
                                    MLModel.name.like(search_key)
                                ).paginate(
                                    page,per_page,error_out=False
                                )
        min_page_show = tableRecords.page - 2 if tableRecords.page - 2 > 0 else 1
        max_page_show = min_page_show + 5 if min_page_show + 5 <= tableRecords.pages + 1 else tableRecords.pages + 1
        count = MLModel().query \
                        .filter(
                            MLModel.name.like(search_key)
                        ).count()
        return self.render('admin/ml_model.html',
                        tableRecords=tableRecords,                
                        min_page_show = min_page_show, 
                        max_page_show = max_page_show, 
                        count = count,
                        table_search = table_search) 



    def save_model_binary(form_binary):
        bin_fn = datetime.now().strftime("%m%d%Y_%H%M%S_") + form_binary.filename
        root_path = os.path.dirname(os.path.dirname(__file__))
        bin_path = os.path.join(root_path, 'static/model-upload', bin_fn)

        form_binary.save(bin_path)

        return bin_fn

    def save_report_csv(form_csv):
        csv_fn = datetime.now().strftime("%m%d%Y_%H%M%S_") + form_csv.filename
        root_path = os.path.dirname(os.path.dirname(__file__))
        csv_path = os.path.join(root_path, 'static/model-upload', csv_fn)

        form_binary.save(csv_path)

        return csv_path

    def read_report(csv_fn):
        root_path = os.path.dirname(os.path.dirname(__file__))
        csv_path = os.path.join(root_path, 'static/model-upload', csv_fn)
        # read csv using pandas
        df = pd.read_csv(csv_path)   
        df = pd.read_csv("report_coffee_bean.csv")
        macro_avg_dict = dict(df.loc[df.iloc[:,0] == "macro avg"])
        accuracy_dict = dict(df.loc[df.iloc[:,0] == "accuracy"])

        return macro_avg_dict['precision'], macro_avg_dict['recall'], accuracy_dict['support'], macro_avg_dict['support']

    def insert_or_update_model(name, binary_name, csv_name, model_id):

        precision, recall, accuracy, validation = read_report(csv_name)

        form = MLModel().query.get(model_id)

        form.name = name
        form.model_filename = binary_name
        form.report_filename = csv_name
        form.precision = precision
        form.recall = recall
        form.accuracy = accuracy
        form.validation_sample = validation


        if not form.id :
            create_at = datetime.now(), 
            create_by = current_user.first_name

        db.session.delete(form)
        db.session.commit()
        return form

    @expose("/detail/<model_id>", methods=['GET','POST'])
    def detail(self, model_id):
        model_id = int(0 if model_id == None else model_id)

        if request.method == "POST" :
            binary_name = save_model_binary(request.files['model_file'])
            csv_name = save_report_csv(request.files['report_file'])
            form = insert_or_update_model(request.form['name'], binary_name, csv_name, model_id)
        else :
            form = MLModel().query.get(model_id)

        return self.render('admin/ml_model_detail.html',
                        form=form)