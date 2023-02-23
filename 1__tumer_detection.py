# -*- coding: utf-8 -*-
"""1__Tumer_Detection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Gm-os78kZA2BlxrO0vuP3-10bxpc2FOJ

## steps : 

1. read Data (excel file ) from google drive , images 
2. unzip images file
3. read images 
4. preparation
4. split data to  taring 80 % , testing 20%
5. normalization images
6. building model
7. compile model 
8. fit model 
9. test model
10. Plot the results
"""

from google.colab import drive
drive.mount('/content/drive')

import seaborn as sns; sns.set(color_codes=True)  # visualization tool
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import os
import statistics
import collections
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials
from datetime import datetime
from datetime import date
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import confusion_matrix
from sklearn import tree
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report,confusion_matrix
from IPython.display import display 
from sklearn.ensemble import AdaBoostClassifier
import keras
from keras.models import Sequential , Model
from keras.layers import (
                          Dense,
                          Add,
                          Conv2D,
                          MaxPool2D,
                          Flatten,
                          Dropout,
                          MaxPooling2D,
                          Input,
                          Conv2DTranspose,
                          Concatenate,
                          BatchNormalization,
                          UpSampling2D,
                          AveragePooling2D,
                          GlobalAveragePooling2D,
                          Activation,
                          ZeroPadding2D
                      )
from keras.preprocessing.image import ImageDataGenerator
#from keras.optimizers import Adam , SGD
from keras.layers.merge import concatenate
from keras.layers.advanced_activations import LeakyReLU
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, EarlyStopping
from keras import backend as K
from keras.utils.np_utils import to_categorical # convert to one-hot-encoding
from sklearn.metrics import classification_report,confusion_matrix
from PIL import Image
import tensorflow as tf
import glob
import random
import cv2
from random import shuffle
import itertools
import shutil
from tensorflow.keras.models import Model, load_model
import imutils
from tensorflow.keras import optimizers
import cv2 as cv
import seaborn as sns
from random import choices
from keras.applications.vgg16 import VGG16 
#from keras.applications.resnet50 import ResNet50
from keras.applications.resnet import ResNet50

from keras.initializers import glorot_uniform

!unzip sample_data/images_data.zip -d sample_data/

"""# Read Data """

auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)

patient_info = drive.CreateFile({'id':"1cWmJm6-MPhhDMxhkBnQzMnANjVofmdG_"})
patient_info.GetContentFile("patient_info.csv")
patient_info = pd.read_csv("patient_info.csv")

"""# Tumor Detection"""

patient_info["Tumor_label"]= patient_info["Tumor_Type"]
cleanup_nums = {
    "Tumor_label":{'Null':0  , "Benign":1 , 'Malignant':1 }
}
patient_info = patient_info.replace(cleanup_nums)
del cleanup_nums

patient_info.info()

patient_info.sample(5)

def crop_contour(image, plot=False):
    
    # Convert the image to grayscale, and blur it slightly
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Threshold the image, then perform a series of erosions +
    # dilations to remove any small regions of noise
    thresh = cv2.threshold(gray, 45, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.erode(thresh, None, iterations=2)
    thresh = cv2.dilate(thresh, None, iterations=2)

    # Find contours in thresholded image, then grab the largest one
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    c = max(cnts, key=cv2.contourArea)
  
    # Find the extreme points
    extLeft = tuple(c[c[:, :, 0].argmin()][0])
    extRight = tuple(c[c[:, :, 0].argmax()][0])
    extTop = tuple(c[c[:, :, 1].argmin()][0])
    extBot = tuple(c[c[:, :, 1].argmax()][0])
    
    # crop new image out of the original image using the four extreme points (left, right, top, bottom)
    new_image = image[extTop[1]:extBot[1], extLeft[0]:extRight[0]]            

    if plot:
        plt.figure()

        plt.subplot(1, 2, 1)
        plt.imshow(image)
        
        plt.tick_params(axis='both', which='both', 
                        top=False, bottom=False, left=False, right=False,
                        labelbottom=False, labeltop=False, labelleft=False, labelright=False)
        
        plt.title('Original Image')
        plt.subplot(1, 2, 2)
        plt.imshow(new_image)

        plt.tick_params(axis='both', which='both', 
                        top=False, bottom=False, left=False, right=False,
                        labelbottom=False, labeltop=False, labelleft=False, labelright=False)
        plt.title('Cropped Image')
        plt.show()

    return new_image

labels = {0:"Normal" , 1:"Tumor"}

def get_data (data_dir , target ):
    X = list()
    y=list()
    img_size = 256
    for index, row in patient_info.iterrows():
        path = os.path.join(data_dir, str (row['Patient_Num']))
        label = row[target]
        for img in os.listdir(path):
            try:
                img_arr = cv2.imread(os.path.join(path, img))[...,::-1] 
                resized_arr = cv2.resize(img_arr, (img_size, img_size)) # Reshaping images to preferred size   
                
                X.append(resized_arr)
                y.append(label)
            except Exception as e:
                print(e , row['Patient_Num'] )
    return X , y

X , y  = get_data("sample_data/Dalia_Data/", target = "Tumor_label")

dict(zip(list(y),[list(y).count(i) for i in list(y)]))

plt.figure(figsize = (5,5))
plt.imshow(X[20])
plt.title(labels[y[20]])
plt.show()

plt.figure(figsize = (5,5))
plt.imshow(X[6000])
plt.title(labels[y[6000]])
plt.show()

x_train, x_test, y_train , y_test = train_test_split(X, y, test_size = 0.20)
x_train, x_val , y_train , y_val = train_test_split(x_train, y_train , test_size = 0.20)

print ("Number images for training : {}".format(len (x_train)) , dict(zip(list(y_train),[list(y_train).count(i) for i in list(y_train)])) )
print ("Number images for testing : {}".format(len (x_test)), dict(zip(list(y_test),[list(y_test).count(i) for i in list(y_test)])) )
print ("Number images for Validation : {}".format(len (x_val)) ,  dict(zip(list(y_val),[list(y_val).count(i) for i in list(y_val)])) )

def data_prepare (X , y , folder_name , labels ) :
    path = "sample_data/{}".format(folder_name)
    os.mkdir(path)
    # create folder for labels 
    for key , value in labels.items()  : 
        path = "sample_data/{}/{}".format(folder_name,value)
        os.mkdir(path)

    if len (X) != len (y) : 
      print ("error size data X and y is not equal")
      return 

    for index , value in enumerate(y) : 
      im = Image.fromarray(X[index])
      path = "sample_data/{}/{}/{}.jpeg".format(folder_name,labels[value],str(index))
      im.save(path)
    return

data_prepare (X=x_train ,y=y_train ,folder_name="train", labels=labels )
data_prepare (X=x_test ,y=y_test ,folder_name="test", labels=labels )
data_prepare (X=x_val ,y=y_val ,folder_name="validation", labels=labels )

## Genration Images 

train_datagen = ImageDataGenerator(shear_range = 0.2,
                                   zoom_range = 0.2,
                                   horizontal_flip = True)

validation_datagen = ImageDataGenerator()

training_set = train_datagen.flow_from_directory('/content/sample_data/train',
                                                 target_size = (224, 224),
                                                 batch_size = 32,
                                                 class_mode = 'sparse')

validation_set = validation_datagen.flow_from_directory('/content/sample_data/validation',
                                            target_size = (224,224),
                                            batch_size = 32,
                                            class_mode = 'sparse')

"""# my model"""

class AccuracyStopping(keras.callbacks.Callback):
    def __init__(self, acc_threshold):
        super(AccuracyStopping, self).__init__()
        self._acc_threshold = acc_threshold

    def on_epoch_end(self, batch, logs={}):
        train_acc = logs.get('accuracy')
        print(train_acc)
        value=1-train_acc
        print(value)
        self.model.stop_training = value <= self._acc_threshold

acc_callback = AccuracyStopping(0.02)

def get_Model():
    modelName= Sequential()
    modelName.add(BatchNormalization(input_shape = (224,224,3)))
    modelName.add(Conv2D(32, (3, 3), input_shape = (224, 224, 3), activation = 'relu'))
    modelName.add(MaxPooling2D(pool_size = (2, 2)))
    modelName.add(Dropout(0.25))
    modelName.add(Flatten())
    modelName.add(Dense(units = 128, activation = 'relu'))
    modelName.add(Dense(units = 2, activation = 'softmax'))
    return modelName

x=get_Model()

x.compile(
    optimizer='adam' , 
    loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), 
    metrics=['accuracy']    )

history = x.fit(    
          training_set,
          steps_per_epoch = (5376 /32),
          epochs=50, 
          validation_data=validation_set,
          validation_steps = (1344/32)
                          )

x.summary()

print('Training Set Clases : ', training_set.class_indices )
print("=="*10)
print('Validation Set Clases : ' , validation_set.class_indices )

loss,accuracy=x.evaluate(validation_set)
print (f"Test Loss     = {loss}")
print (f"Test Accuracy = {accuracy}")

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

plt.figure(figsize=(15, 15))

fig, ax = plt.subplots(figsize = (15 ,15) , dpi=80,)
ax.set_facecolor('#ffffff')
ax.xaxis.label.set_color('#000000')
ax.yaxis.label.set_color('#000000')
ax.tick_params(axis='x', colors='#000000' )  
ax.tick_params(axis='y', colors='#000000')
ax.spines['left'].set_color('#000000')  
ax.spines['bottom'].set_color('#000000')

plt.subplot(2, 2, 1)
plt.plot( acc, label='Training Accuracy')
plt.plot( val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(2, 2, 2)
plt.plot( loss, label='Training Loss')
plt.plot( val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

from keras.preprocessing import image
color=['#ff6600','#1976D2'] 

path='/content/sample_data/test/Normal'
l_Normal =[]

filelist= [file for file in os.listdir(path) if file.endswith('.jpeg')]
y_Normal =[0]*len(filelist)
print ("Number of images for Normal :" , len (filelist))

for img in filelist:
  test_image = image.load_img(os.path.join(path, img),target_size = (224, 224))
  test_image = image.img_to_array(test_image)
  test_image = np.expand_dims(test_image, axis = 0)
  l_Normal.append(test_image)

l_Normal_result=[]
for i in range(len(l_Normal)):
  xx = x.predict(l_Normal[i])
  xx = np.round(xx).astype(int)
  l_Normal_result.append(xx[0][1])

l_Normal_draw=[]
for i in range(len(l_Normal_result)):
    if (l_Normal_result[i]== 0):
        l_Normal_draw.append("Normal")
    else :
        l_Normal_draw.append("Tumor")

display('==='*10)
display(dict(zip(list(l_Normal_draw),[list(l_Normal_draw).count(i) for i in list(l_Normal_draw)])))
display('==='*10)

res = dict(zip(list(l_Normal_draw),[list(l_Normal_draw).count(i) for i in list(l_Normal_draw)]))
labels = ['Normal','Tumor']

fig, ax = plt.subplots(figsize = (9 , 6) , dpi=80,)
ax.set_facecolor('#ffffff')
ax.xaxis.label.set_color('#000000')
ax.yaxis.label.set_color('#000000')
ax.tick_params(axis='x', colors='#000000' )  
ax.tick_params(axis='y', colors='#000000')
ax.spines['left'].set_color('#000000')        # setting up Y-axis tick color to red
ax.spines['bottom'].set_color('#000000')
plt.bar( labels , res.values() ,width = 0.7,  color=[ '#ff6600', '#1976D2'] ,  align='center' , zorder=1)
plt.xlabel('Label')
plt.title('Tumer Detection Normal label')
plt.show()


sns.set_style('darkgrid')
sns.countplot(l_Normal_draw)
plt.show()

from keras.preprocessing import image

path='/content/sample_data/test/Tumor'
l_Tumor=[]

filelist= [file for file in os.listdir(path) if file.endswith('.jpeg')]
y_Tumor =[1]*len(filelist)
print ("Number of images for Tumor :" , len (filelist))

for img in filelist:
  test_image = image.load_img(os.path.join(path, img),target_size = (224, 224))
  test_image = image.img_to_array(test_image)
  test_image = np.expand_dims(test_image, axis = 0)
  l_Tumor.append(test_image)

l_Tumor_result=[]
for i in range(len(l_Tumor)):
  #xx = x.predict_classes(l_Tumor[i]
  xx = x.predict(l_Tumor[i])
  xx = np.round(xx).astype(int)
  l_Tumor_result.append(xx[0][1])

l_Tumor_draw=[]
for i in range(len(l_Tumor_result)):
    if (l_Tumor_result[i]== 0):
        l_Tumor_draw.append("Normal")
    else :
        l_Tumor_draw.append("Tumor")

display('==='*10)
display(dict(zip(list(l_Tumor_draw),[list(l_Tumor_draw).count(i) for i in list(l_Tumor_draw)])))
display('==='*10)

sns.set_style('darkgrid')
sns.countplot(l_Tumor_draw)
plt.show()

from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve, auc

print('Training Set Clases')
print(training_set.class_indices)
print('Testing Set Clases')
print(validation_set.class_indices)
print("======"*10)
print('\nConfusion Matrix')
print('Classification Report')
target_names = ['Normal', 'Tumor']

y_labels  = y_Normal +y_Tumor
x_results = l_Normal_result + l_Tumor_result
print(classification_report( y_labels , x_results , target_names=target_names))

x.save('/content/drive/MyDrive/Tumer_classification/best_model.h5')

"""# VGG16"""

datagen = ImageDataGenerator(rescale=1/255,
                             rotation_range=20,
                             horizontal_flip=True,
                             height_shift_range=0.1,
                             width_shift_range=0.1,
                             shear_range=0.1,
                             brightness_range=[0.3, 1.5],
                             validation_split=0.2
                            )

train_gen= datagen.flow_from_directory('/content/sample_data/train',
                                       target_size=(224,224),
                                       class_mode='binary',
                                       subset='training'
                                      )
val_gen = datagen.flow_from_directory( '/content/sample_data/validation',
                                       target_size=(224,224),
                                       class_mode='binary',
                                       subset='validation'
                                      )

vgg_model=VGG16(weights='imagenet',input_shape=(224,224,3),include_top=False)
model=keras.Sequential()
for layer in vgg_model.layers:
    model.add(layer)
for layer in model.layers:
    layer.trainable=False

model.add(Flatten())
model.add(Dropout(0.4))
model.add(Dense(256,activation='relu'))
model.add(Dense(1,activation='sigmoid'))

model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=['accuracy']
             )

stop = EarlyStopping(
    monitor='val_accuracy', 
    mode='max',
    patience=6
)

checkpoint= ModelCheckpoint(
    filepath='./',
    save_weights_only=True,
    monitor='val_accuracy',
    mode='max',
    save_best_only=True)
history=model.fit(train_gen,validation_data=val_gen,epochs=50,callbacks=[stop,checkpoint])

print('Training Set Clases : ', training_set.class_indices )
print("=="*10)
print('Validation Set Clases : ' , validation_set.class_indices )

loss,accuracy=model.evaluate(validation_set)
print (f"Test Loss     = {loss}")
print (f"Test Accuracy = {accuracy}")

plt.plot(history.history['loss'],label='train loss')
plt.plot(history.history['val_loss'],label='validation loss')
plt.legend()

from keras.preprocessing import image

path='/content/sample_data/test/Normal'
l_Normal =[]

filelist= [file for file in os.listdir(path) if file.endswith('.jpeg')]
y_Normal =[0]*len(filelist)
print ("Number of images for Normal :" , len (filelist))

for img in filelist:
  test_image = image.load_img(os.path.join(path, img),target_size = (224, 224))
  test_image = image.img_to_array(test_image)
  test_image = np.expand_dims(test_image, axis = 0)
  l_Normal.append(test_image)

l_Normal_result=[]
for i in range(len(l_Normal)):
  xx = model.predict(l_Normal[i])
  xx = np.round(xx).astype(int)
  l_Normal_result.append(xx[0][0])


l_Normal_draw=[]
for i in range(len(l_Normal_result)):
    if (l_Normal_result[i] == 0):
        l_Normal_draw.append("Normal")
    else :
        l_Normal_draw.append("Tumor")

display('==='*10)
display(dict(zip(list(l_Normal_draw),[list(l_Normal_draw).count(i) for i in list(l_Normal_draw)])))
display('==='*10)

sns.set_style('darkgrid')
sns.countplot(l_Normal_draw)
plt.show()

from keras.preprocessing import image

path='/content/sample_data/test/Tumor'
l_Tumor=[]

filelist= [file for file in os.listdir(path) if file.endswith('.jpeg')]
y_Tumor =[1]*len(filelist)
print ("Number of images for Tumor :" , len (filelist))

for img in filelist:
  test_image = image.load_img(os.path.join(path, img),target_size = (224, 224))
  test_image = image.img_to_array(test_image)
  test_image = np.expand_dims(test_image, axis = 0)
  l_Tumor.append(test_image)

l_Tumor_result=[]
for i in range(len(l_Tumor)):
  xx= model.predict(l_Tumor[i])
  xx = np.round(xx).astype(int)
  l_Tumor_result.append(xx[0][0])

l_Tumor_draw=[]
for i in range(len(l_Tumor_result)):
    if (l_Tumor_result[i]== 0):
        l_Tumor_draw.append("Normal")
    else :
        l_Tumor_draw.append("Tumor")

display('==='*10)
display(dict(zip(list(l_Tumor_draw),[list(l_Tumor_draw).count(i) for i in list(l_Tumor_draw)])))
display('==='*10)

sns.set_style('darkgrid')
sns.countplot(l_Tumor_draw)
plt.show()

from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve, auc

print('Training Set Clases')
print(training_set.class_indices)
print('Testing Set Clases')
print(validation_set.class_indices)
print("======"*10)
print('\nConfusion Matrix')
print('Classification Report')
target_names = ['Normal', 'Tumor']

y_labels  = y_Normal +y_Tumor
x_results = l_Normal_result + l_Tumor_result

# x_results_new = list()
# for i in x_results :
#   x_results_new.append(i[0][0])

print(classification_report( y_labels , x_results , target_names=target_names))

"""# ResNet50"""

#add RESNet Model as a layer in ou model as we use in the structure above 

stop = EarlyStopping(
    monitor='val_accuracy', 
    mode='max',
    patience=6
)

base_model_2 = Sequential()
base_model_2.add(ResNet50(include_top=False, weights='imagenet', pooling='max'))
base_model_2.add(Dropout(0.25))
base_model_2.add(Flatten())
base_model_2.add(Dense(units = 128, activation = 'relu'))
base_model_2.add(Dense(2, activation='softmax'))


base_model_2.compile(
    optimizer='adam' , 
    loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), 
    metrics=['accuracy']    )

base_model_2.summary()

history=base_model_2.fit(training_set,validation_data=validation_set,epochs=50,callbacks=[stop])

print('Training Set Clases : ', training_set.class_indices )
print("=="*10)
print('Validation Set Clases : ' , validation_set.class_indices )

loss,accuracy=base_model_2.evaluate(validation_set)
print (f"Test Loss     = {loss}")
print (f"Test Accuracy = {accuracy}")

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

plt.figure(figsize=(15, 15))
plt.subplot(2, 2, 1)
plt.plot( acc, label='Training Accuracy')
plt.plot( val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(2, 2, 2)
plt.plot( loss, label='Training Loss')
plt.plot( val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

from keras.preprocessing import image

path='/content/sample_data/test/Normal'
l_Normal =[]

filelist= [file for file in os.listdir(path) if file.endswith('.jpeg')]
y_Normal =[0]*len(filelist)
print ("Number of images for Normal :" , len (filelist))

for img in filelist:
  test_image = image.load_img(os.path.join(path, img),target_size = (224, 224))
  test_image = image.img_to_array(test_image)
  test_image = np.expand_dims(test_image, axis = 0)
  l_Normal.append(test_image)

l_Normal_result=[]
for i in range(len(l_Normal)):
  xx= base_model_2.predict(l_Normal[i])
  xx = np.round(xx).astype(int)
  l_Normal_result.append(xx[0][1])


l_Normal_draw=[]
for i in range(len(l_Normal_result)):
    if (l_Normal_result[i] == 0):
        l_Normal_draw.append("Normal")
    else :
        l_Normal_draw.append("Tumor")

display('==='*10)
display(dict(zip(list(l_Normal_draw),[list(l_Normal_draw).count(i) for i in list(l_Normal_draw)])))
display('==='*10)

sns.set_style('darkgrid')
sns.countplot(l_Normal_draw)
plt.show()

xx

from keras.preprocessing import image

path='/content/sample_data/test/Tumor'
l_Tumor=[]

filelist= [file for file in os.listdir(path) if file.endswith('.jpeg')]
y_Tumor =[1]*len(filelist)
print ("Number of images for Tumor :" , len (filelist))

for img in filelist:
  test_image = image.load_img(os.path.join(path, img),target_size = (224, 224))
  test_image = image.img_to_array(test_image)
  test_image = np.expand_dims(test_image, axis = 0)
  l_Tumor.append(test_image)

l_Tumor_result=[]
for i in range(len(l_Tumor)):
  xx= base_model_2.predict(l_Tumor[i])
  xx = np.round(xx).astype(int)
  l_Tumor_result.append(xx[0][1])

l_Tumor_draw=[]
for i in range(len(l_Tumor_result)):
    if (l_Tumor_result[i]== 0):
        l_Tumor_draw.append("Normal")
    else :
        l_Tumor_draw.append("Tumor")

display('==='*10)
display(dict(zip(list(l_Tumor_draw),[list(l_Tumor_draw).count(i) for i in list(l_Tumor_draw)])))
display('==='*10)

sns.set_style('darkgrid')
sns.countplot(l_Tumor_draw)
plt.show()

from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve, auc

print('Training Set Clases')
print(training_set.class_indices)
print('Testing Set Clases')
print(validation_set.class_indices)
print("======"*10)
print('\nConfusion Matrix')
print('Classification Report')
target_names = ['Normal', 'Tumor']

y_labels  = y_Normal +y_Tumor
x_results = l_Normal_result + l_Tumor_result
print(classification_report( y_labels , x_results , target_names=target_names))