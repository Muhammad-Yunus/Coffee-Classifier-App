from . import db
from . import UserMixin

class MLModel(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    precision = db.Column(db.Float(6))
    recall = db.Column(db.Float(6))
    accuracy = db.Column(db.Float(6))
    train_sample = db.Column(db.Integer)
    validation_sample = db.Column(db.Integer)
    create_at = db.Column(db.DateTime())
    create_by = db.Column(db.String(255))

class ModelReport(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255))
    precision = db.Column(db.Float(6))
    recall = db.Column(db.Float(6))
    mlmodel_id = db.Column(db.Integer)

class TraingHistory(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    mlmodel_id = db.Column(db.Integer)
    name = db.Column(db.String(255))
    iteration = db.Column(db.Integer)
    value = db.Column(db.Float(6))