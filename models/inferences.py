from . import db
from . import roles_users
from . import UserMixin

class Inference(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(255))
    result_class = db.Column(db.String(255))
    result_label = db.Column(db.String(255), unique=True)
    confidence = db.Column(db.String(255))
    run_at = db.Column(db.DateTime())
    run_by = db.Column(db.String(255))

    def __str__(self):
        return self.email