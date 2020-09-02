from . import db
from . import UserMixin

class Upload(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    upload_at = db.Column(db.DateTime())
    upload_by = db.Column(db.String(255))
    is_used = db.Column(db.Boolean)
