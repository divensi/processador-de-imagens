import sys

from PyQt5 import QtWidgets, uic

from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, \
  QApplication, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, \
  QFileDialog, QColorDialog, QListWidgetItem
import numpy as np
import cv2
import _thread
from matplotlib import pyplot as plt
import copy

from Filters import applyFilters

class PopUpDLG(QtWidgets.QDialog):
  def __init__(self, image = None, filter = None):
    super(PopUpDLG, self).__init__()
    
    self.filter = filter
    self.image = image
    self.original = image

    uic.loadUi('Dialog.ui', self)
    
    self.initUi()
    self.mostrarImagem()

  def initUi(self):
    if (1 in self.filter['params']):
      self.sldExample.valueChanged.connect(self.sliderParametro1)
      self.lblExample.setText(self.filter['params'][1]['name'])
      self.sldExample.setEnabled(True)

    if (2 in self.filter['params']):
      self.sldExample_2.valueChanged.connect(self.sliderParametro2)
      self.lblExample_2.setText(self.filter['params'][2]['name'])
      self.sldExample_2.setEnabled(True)

    if (3 in self.filter['params']):
      self.sldExample_3.valueChanged.connect(self.sliderParametro3)
      self.lblExample_3.setText(self.filter['params'][3]['name'])
      self.sldExample_3.setEnabled(True)

  def sliderParametro1(self):
    size = self.sldExample.value()
    self.filter['params'][1]['val'] = size
    self.mostrarImagem()

  def sliderParametro2(self):
    size = self.sldExample_2.value()
    self.filter['params'][2]['val'] = size
    self.mostrarImagem()

  def sliderParametro3(self):
    size = self.sldExample_3.value()
    self.filter['params'][3]['val'] = size
    self.mostrarImagem()

  def setImage(self, image):
    self.image = image

  def mostrarImagem(self):
    self.image = applyFilters(self.original, self.filter['filterType'], self.filter['params'])
    size = self.image.shape
    step = self.image.size / size[0]

    qformat = QImage.Format_RGBA8888 if size[2] == 4 else QImage.Format_RGB888
    img = QImage(self.image, size[1], size[0], step, qformat).rgbSwapped()
    self.lblImage.setPixmap(QPixmap.fromImage(img))

  def exec_(self):
    super(PopUpDLG, self).exec_()
    return self.filter
