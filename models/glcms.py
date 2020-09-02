from . import db
from . import UserMixin

class Glcm(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    angel = db.Column(db.Integer)
    dissimilarity = db.Column(db.Float(6))
    correlation = db.Column(db.Float(6))
    homogeneity = db.Column(db.Float(6))
    contrast = db.Column(db.Float(6))
    ASM = db.Column(db.Float(6))
    energy = db.Column(db.Float(6))
    calc_at = db.Column(db.DateTime())
    calc_by = db.Column(db.String(255))
    Upload_Id = db.Column(db.Integer)