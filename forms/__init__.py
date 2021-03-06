from flask_admin.contrib import sqla
from flask_admin import BaseView, AdminIndexView, expose
from flask import request, url_for, send_file
from flask_wtf.file import FileField, FileAllowed
from flask_security.utils import encrypt_password
from flask_security import current_user
from datetime import datetime
import os
import secrets
import numpy as np
import pandas as pd


from core_ml.main import Predictor

predictor = Predictor()