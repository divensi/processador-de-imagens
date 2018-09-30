import sys
from PyQt5 import QtCore
from PyQt5.QtGui import QImage, QPixmap, QColor
import numpy as np
import cv2
import _thread
import copy

class Thread(QtCore.QThread):
  changePixmap = QtCore.pyqtSignal(object)
  changeLabel = QtCore.pyqtSignal(object)

  def run(self):
    cap = cv2.VideoCapture(0)

    while True:
      _, frame = cap.read()
      self.changePixmap.emit(frame)
