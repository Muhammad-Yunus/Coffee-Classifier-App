from . import np 
from . import cv2 
from . import keras
from . import K
import os

from skimage.feature import greycomatrix, greycoprops

def calc_glcm_core(filename, dists=[5], agls=[0, np.pi/4, np.pi/2, 3*np.pi/4], lvl=256, sym=True, norm=True):
    img = cv2.imread(filename)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)        
    h, w = gray.shape
    ymin, ymax, xmin, xmax = h//3, h*2//3, w//3, w*2//3
    crop = gray[ymin:ymax, xmin:xmax]
    
    resize = cv2.resize(crop, (0,0), fx=0.5, fy=0.5)
    cv2.imwrite(filename, resize)
    props = ['dissimilarity', 'correlation', 'homogeneity', 'contrast', 'ASM', 'energy']
    glcm = greycomatrix(resize, 
                        distances=dists, 
                        angles=agls, 
                        levels=lvl,
                        symmetric=sym, 
                        normed=norm)
    out = {}
    for name in props:
        out[name] = greycoprops(glcm, name)[0]

    feature = {}
    for i, angel in enumerate(["0", "45", "90", "135"]):
        feature[angel] = {}
        for name in props:
            feature[angel][name] = out[name][i] 
    print(feature)
    return feature

class Predictor():
    def __init__(self):
        self.model = keras.models.load_model('core_ml/model_coffee_bean.h5', 
                                            custom_objects={'recall':self.recall, 'precision':self.precision})

    def recall(self, y_true, y_pred):
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
        recall = true_positives / (possible_positives + K.epsilon())
        return recall

    def precision(self, y_true, y_pred):
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
        precision = true_positives / (predicted_positives + K.epsilon())
        return precision

    def decimal_scaling(self, data):
        data = np.array(data, dtype=np.float32)
        c = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1]) # result decimal_scaling in training phase
        return data/(10**c)


    def predict_coffe_core(self, X):
        X = np.reshape(X, (1,24))
        X = self.decimal_scaling(X)
        print(X)
        
        label_map = ['Dark Coffee', 'Extra Dark Coffee', 'Light Coffee', 'Medium Coffee']

        y_pred = self.model.predict(X)
        y_pred = [int(y*1000)/10.0 for y in y_pred[0]]

        idx = np.argmax(y_pred)
        confidence = np.max(y_pred)
        coffe_name = label_map[idx]

        dist = {}
        for y, l in zip(y_pred, label_map):
            dist[l] = y

        return dist , coffe_name, confidence