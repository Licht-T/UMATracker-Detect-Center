# -*- coding: utf-8 -*-
import numpy as np
from sklearn import cluster
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot

try:
    from .ui_group_tracker_widget import Ui_group_tracker_widget
except ImportError:
    from ui_group_tracker_widget import Ui_group_tracker_widget

try:
    from .group_tracker import GroupTrackerGMM
except ImportError:
    from group_tracker import GroupTrackerGMM

class Widget(Ui_group_tracker_widget, QtWidgets.QWidget):
    reset = pyqtSignal()
    restart = pyqtSignal()

    def __init__(self, parent):
        super(Widget, self).__init__(parent)
        self.setupUi()
        self.estimator_init()

    def setupUi(self):
        super(Widget, self).setupUi(self)

        self.resetButton.pressed.connect(self.reset_button_pressed)
        self.restartButton.pressed.connect(self.restart_button_pressed)
        self.nObjectsSpinBox.valueChanged.connect(self.n_objects_spinbox_value_changed)

    def estimator_init(self):
        self.gmm = None

    def reset_estimator(self, points):
        if hasattr(self, 'gmm'):
            self.gmm.means_ = points

    def get_name(self):
        return 'Group Tracker GMM'

    def track(self, original_img, filtered_img):
        n_objects = self.nObjectsSpinBox.value()
        n_k_means = self.nKmeansSpinBox.value()

        non_zero_pos = np.transpose(np.nonzero(filtered_img.T))

        if self.gmm is None:
            self.gmm = GroupTrackerGMM(n_components=n_objects, covariance_type='full', n_iter=2000)

        self.gmm._fit(non_zero_pos, n_k_means=n_k_means)
        res = self.gmm.means_

        out = []
        for p in res:
            out.append({'position': p})

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
