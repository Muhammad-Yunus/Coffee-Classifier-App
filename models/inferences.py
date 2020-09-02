from . import db
from . import UserMixin

class Inference(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    Upload_Id = db.Column(db.Integer)
    result_dict = db.Column(db.String(500))
    result_label = db.Column(db.String(255))
    confidence = db.Column(db.String(255))
    run_at = db.Column(db.DateTime())
    run_by = db.Column(db.String(255))

    def __str__(self):
        return self.email
