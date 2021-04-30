# -*- coding:utf-8 -*-
from sys import is_finalizing
from keras.preprocessing.image import ImageDataGenerator
from classifiers import KerasClassifier
from model.model import *

class CifarModel(CNNModel):
    def __init__(self, param):
        super(CifarModel, self).__init__(param)

    def init(self, data):
        self.input_shape = data.x_train.shape[1:]
        self.min_ = data.min_
        self.max_ = data.max_

    def set_learning_phase(self, learning_phase):
        K.set_learning_phase(learning_phase)

    def init_model(self):
        K.set_learning_phase(1)
        model = Sequential()
        model.add(
            Conv2D(64, (3, 3), activation='relu', input_shape=self.input_shape, name='block1_conv1', padding='same'))
        model.add(Conv2D(64, (3, 3), activation='relu', name='block1_conv2', padding='same'))
        model.add(MaxPooling2D(pool_size=(2, 2), name='block1_pool1'))
        model.add(Dropout(0.25, name='dropout_1'))
        model.add(Conv2D(128, (3, 3), activation='relu', name='block2_conv1', padding='same'))
        model.add(Conv2D(128, (3, 3), activation='relu', name='block2_conv2', padding='same'))
        model.add(MaxPooling2D(pool_size=(2, 2), name='block2_pool1'))
        model.add(Dropout(0.25, name='dropout_2'))
        model.add(Conv2D(128, (3, 3), activation='relu', name='block3_conv1', padding='same'))
        model.add(Conv2D(128, (3, 3), activation='relu', name='block3_conv2', padding='same'))
        model.add(Conv2D(128, (3, 3), activation='relu', name='block3_conv3', padding='same'))
        model.add(Conv2D(128, (3, 3), activation='relu', name='block3_conv4', padding='same'))
        model.add(MaxPooling2D(pool_size=(2, 2), name='block3_pool1'))
        model.add(Dropout(0.25, name='dropout_3'))
        model.add(Flatten(name='flatten1'))
        model.add(Dense(1024, activation='relu', name='dense_1'))
        model.add(Dropout(0.5, name='dropout_4'))
        model.add(Dense(1024, activation='relu', name='dense_2'))
        model.add(Dropout(0.5, name='dropout_5'))
        model.add(Dense(self.param.get_conf('num_classes'), activation=None, name='predictions'))
        model.add(Activation('softmax', name='softmax_output'))

        model.compile(loss='categorical_crossentropy', optimizer='Adadelta', metrics=['accuracy'])

        self.classifier = KerasClassifier(clip_values=(self.min_, self.max_), model=model, param=self.param)

    def train(self, data, nb_epochs=None):
        # default
        # nb_epochs=20
        # batch_size=128
        self.classifier.get_model().compile(loss='categorical_crossentropy', optimizer='Adadelta', metrics=['accuracy'])
        if nb_epochs is None:
            nb_epochs = self.param.get_conf('train_epoch')
        # if isinstance(data, Data):

        datagen = ImageDataGenerator(
            featurewise_center=False,  # set input mean to 0 over the dataset
            samplewise_center=False,  # set each sample mean to 0
            featurewise_std_normalization=False,  # divide inputs by std of the dataset
            samplewise_std_normalization=False,  # divide each input by its std
            zca_whitening=False,  # apply ZCA whitening
            zca_epsilon=1e-06,  # epsilon for ZCA whitening
            rotation_range=0,  # randomly rotate images in the range (degrees, 0 to 180)
            # randomly shift images horizontally (fraction of total width)
            width_shift_range=0.1,
            # randomly shift images vertically (fraction of total height)
            height_shift_range=0.1,
            shear_range=0.,  # set range for random shear
            zoom_range=0.,  # set range for random zoom
            channel_shift_range=0.,  # set range for random channel shifts
            # set mode for filling points outside the input boundaries
            fill_mode='nearest',
            cval=0.,  # value used for fill_mode = "constant"
            horizontal_flip=True,  # randomly flip images
            # validation_split=0.0
            )
        # Fit the model on the batches generated by datagen.flow().
        self.classifier.get_model().fit_generator(datagen.flow(data.x_train, data.y_train, batch_size=128),
                                                epochs=nb_epochs,
                                                steps_per_epoch=data.x_train.shape[0] / 128,
                                                validation_data=(data.x_test, data.y_test),
                                                validation_steps=data.x_train.shape[0] / 128,
                                                workers=4)


    def predict_instance(self, x):
        return self.classifier.predict(x)[0]

    def get_input_shape(self):
        return self.input_shape

    def set_input_shape(self, input_shape):
        self.input_shape = input_shape

    def get_classifier(self):
        return self.classifier

    def set_classifier(self, classifier):
        self.classifier = classifier

    def get_input_tensor(self):
        return self.classifier.get_input_tensor()

    def get_output_tensor(self):
        return self.classifier.get_output_tensor()

    def get_output_bef_softmax(self):
        return self.classifier.get_output_bef_softmax()

    def get_dense_tensor(self):
        return self.classifier.get_model().get_layer('dense_2').output
