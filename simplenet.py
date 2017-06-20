# -*- coding: utf-8 -*-
import h5py
import sys
import numpy as np
import os

from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, ZeroPadding2D, Dense, Dropout
from keras.layers.core import Flatten
from keras.layers.normalization import BatchNormalization
from keras.layers.advanced_activations import LeakyReLU
from keras.optimizers import SGD
from keras.initializers import RandomNormal

from lesion_extraction_2d.lesion_extractor_2d import get_train_data
from utils.auc_callback import AucHistory
from utils.generator_from_config import get_generator
from data_visualization.adc_lesion_values import apply_window

from sklearn.cross_validation import train_test_split

def get_model(configuration='baseline'):
    AUGMENTATION_CONFIGURATION = configuration

    ## Model
    model = Sequential()
    model.add(Conv2D(32, (3, 3), kernel_initializer='he_normal', bias_initializer=RandomNormal(mean=0.1), input_shape=(16, 16, 3)))
    model.add(LeakyReLU())
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(64, (2, 2), kernel_initializer='he_normal', bias_initializer=RandomNormal(mean=0.1)))
    model.add(LeakyReLU())
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(64, (2, 2), kernel_initializer='he_normal', bias_initializer=RandomNormal(mean=0.1)))
    model.add(LeakyReLU())
    model.add(BatchNormalization())
    model.add(Conv2D(64, (2, 2), kernel_initializer='he_normal', bias_initializer=RandomNormal(mean=0.1)))
    model.add(LeakyReLU())
    model.add(BatchNormalization())

    model.add(Conv2D(64, (1, 1), kernel_initializer='he_normal', bias_initializer=RandomNormal(mean=0.1)))
    model.add(LeakyReLU())
    model.add(BatchNormalization())

    model.add(Conv2D(1, (1, 1), activation='sigmoid'))
    model.add(Flatten())

    # model = Sequential()
    # model.add(ZeroPadding2D((1,1),input_shape=(16, 16, 3)))
    # model.add(Conv2D(64, 3, 3, activation='relu'))
    # model.add(ZeroPadding2D((1,1)))
    # model.add(Conv2D(64, 3, 3, activation='relu'))
    # model.add(MaxPooling2D((2,2), strides=(2,2)))
    #
    # model.add(ZeroPadding2D((1,1)))
    # model.add(Conv2D(128, 3, 3, activation='relu'))
    # model.add(ZeroPadding2D((1,1)))
    # model.add(Conv2D(128, 3, 3, activation='relu'))
    # model.add(MaxPooling2D((2,2), strides=(2,2)))
    #
    # model.add(ZeroPadding2D((1,1)))
    # model.add(Conv2D(256, 3, 3, activation='relu'))
    # model.add(ZeroPadding2D((1,1)))
    # model.add(Conv2D(256, 3, 3, activation='relu'))
    # model.add(ZeroPadding2D((1,1)))
    # model.add(Conv2D(256, 3, 3, activation='relu'))
    # model.add(MaxPooling2D((2,2), strides=(2,2)))
    #
    # model.add(ZeroPadding2D((1,1)))
    # model.add(Conv2D(512, 3, 3, activation='relu'))
    # model.add(ZeroPadding2D((1,1)))
    # model.add(Conv2D(512, 3, 3, activation='relu'))
    # model.add(ZeroPadding2D((1,1)))
    # model.add(Conv2D(512, 3, 3, activation='relu'))
    # model.add(MaxPooling2D((2,2), strides=(2,2)))
    #
    # model.add(ZeroPadding2D((1,1)))
    # model.add(Conv2D(512, 3, 3, activation='relu'))
    # model.add(ZeroPadding2D((1,1)))
    # model.add(Conv2D(512, 3, 3, activation='relu'))
    # model.add(ZeroPadding2D((1,1)))
    # model.add(Conv2D(512, 3, 3, activation='relu'))
    # #model.add(MaxPooling2D((2,2), strides=(2,2)))
    #
    # model.add(Flatten())
    # model.add(Dense(4096, activation='relu'))
    # model.add(Dropout(0.5))
    # model.add(Dense(4096, activation='relu'))
    # model.add(Dropout(0.5))
    # model.add(Dense(1, activation='sigmoid'))

    # For a binary classification problem
    sgd = SGD(lr=0.0005, momentum=0.9)
    model.compile(optimizer=sgd, loss='binary_crossentropy', metrics=['accuracy'])

    ## Data
    h5_file_location = os.path.join('C:\\Users\\Jeftha\\stack\\Rommel\\ISMI\\data', 'prostatex-train.hdf5')
    h5_file = h5py.File(h5_file_location, 'r')
    
    train_data_list, train_labels_list, attr = get_train_data(h5_file, ['ADC', 't2_tse_tra', 't2_tse_sag'], size_px=16, size_mm=32)
    print(train_data_list.shape)

    for lesion in train_data_list:
        lesion[:, :, 0] = apply_window(lesion[:, :, 0], window=(500, 1100))

    train_data, val_data, train_labels, val_labels = train_test_split(train_data_list, train_labels_list, test_size=0.33)

    # train_data = np.expand_dims(train_data, axis=-1)
    # val_data = np.expand_dims(val_data, axis=-1)
    train_labels = np.expand_dims(train_labels, axis=-1)
    val_labels = np.expand_dims(val_labels, axis=-1)

    ## Stuff for training
    generator = get_generator(configuration=AUGMENTATION_CONFIGURATION)

    train_generator = generator.flow(train_data, train_labels)  #, save_to_dir="/nfs/home4/schellev/augmented_images")
    batch_size = 128
    steps_per_epoch = len(train_labels_list) // batch_size

    auc_history = AucHistory(train_data, train_labels, val_data, val_labels, output_graph_name=AUGMENTATION_CONFIGURATION)
    model.fit_generator(train_generator, steps_per_epoch, epochs=100, verbose=1, callbacks=[auc_history], max_q_size=50, workers=8)

    return model

if __name__ == "__main__":
    m = get_model()
