# -*- coding: utf-8 -*-
import numpy as np
import dlib
from sklearn import cluster
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot

try:
    from .ui_correlation_tracking_widget import Ui_CorrelationTrackingWidget
except ImportError:
    from ui_correlation_tracking_widget import Ui_CorrelationTrackingWidget


class Widget(Ui_CorrelationTrackingWidget, QtWidgets.QWidget):
    reset = pyqtSignal()
    restart = pyqtSignal()

    def __init__(self, parent):
        super(Widget, self).__init__(parent)
        self.setupUi()
        self.estimator_init()

        self.img = None

    def setupUi(self):
        super(Widget, self).setupUi(self)

        self.resetButton.pressed.connect(self.reset_button_pressed)
        self.restartButton.pressed.connect(self.restart_button_pressed)
        self.nObjectsSpinBox.valueChanged.connect(self.n_objects_spinbox_value_changed)

    def estimator_init(self):
        self.k_means = None
        self.tracker = None

    def reset_estimator(self, kv):
        center_pos = kv['position']
        self.set_new_estimator(center_pos)

    def set_new_estimator(self, center_pos):
        windows = np.zeros(center_pos.shape)
        windows[:] = self.windowHeightSpinBox.value()
        windows[:,0] = self.windowWidthSpinBox.value()

        top_left = center_pos - windows/2
        bottom_right = center_pos + windows/2

        self.tracker = []

        for p, t, b in zip(center_pos, top_left, bottom_right):
            rect = dlib.drectangle(t[0], t[1], b[0], b[1])

            if self.img is not None:
                print("initinit!!!!!!!!!!!!!")
                tracker = dlib.correlation_tracker()
                tracker.start_track(self.img, rect)
                self.tracker.append(tracker)

    def get_name(self):
        return 'Correlation Tracking'

    def get_tracking_n(self):
        return self.nObjectsSpinBox.value()

    def get_attributes(self):
        return {'position':('x', 'y'), 'rect':False}

    def track(self, original_img, filtered_img):
        n_objects = self.nObjectsSpinBox.value()
        n_k_means = self.nKmeansSpinBox.value()
        self.img = original_img.copy()

        if self.k_means is None:
            self.k_means = cluster.KMeans(n_clusters=n_objects, max_iter=10000)
        elif n_k_means!=self.k_means.n_clusters:
            self.k_means = cluster.KMeans(n_clusters=n_k_means, max_iter=10000)

        if self.tracker is None:
            non_zero_pos = np.transpose(np.nonzero(filtered_img.T))
            center_pos = self.k_means.fit(non_zero_pos).cluster_centers_
            self.set_new_estimator(center_pos)
            res = center_pos
        else:
            try:
                res = []
                for tracker in self.tracker:
                    tracker.update(self.img)
                    p = tracker.get_position().dcenter()
                    res.append([p.x, p.y])
                res = np.array(res)
                print(res)
            except Warning:
                pass

        windows = np.zeros(res.shape)
        windows[:] = self.windowHeightSpinBox.value()
        windows[:,0] = self.windowWidthSpinBox.value()

        out = {
                'position': res,
                'rect': [
                    {
                        'topLeft': p-w/2.,
                        'bottomRight': p+w/2.
                        }
                    for p, w in zip(res, windows)
                    ]
                }

        return out

    @pyqtSlot()
    def reset_button_pressed(self):
        self.estimator_init()
        self.reset.emit()

    @pyqtSlot()
    def restart_button_pressed(self):
        self.restart.emit()

    @pyqtSlot(int)
    def n_objects_spinbox_value_changed(self, i):
        self.nKmeansSpinBox.setMinimum(i)
