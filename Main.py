# python3
# coding=utf-8

from PyQt5 import QtWidgets, uic
import sys
from PyQt5.QtGui import QImage, QPixmap, QColor, QStandardItemModel, QStandardItem
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, \
  QApplication, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, \
  QFileDialog, QColorDialog, QListWidget, QListWidgetItem, QAbstractItemView
import numpy as np
import cv2
import _thread
from matplotlib import pyplot as plt
import copy
from MainDialog import PopUpDLG

from VideoThread import Thread

from Filters import applyFilters

class ApplicationWindow(QtWidgets.QMainWindow):
  def __init__(self):
    super(ApplicationWindow, self).__init__()

    uic.loadUi('MainWindow.ui', self)
    self.image = None
    self.original = None

    self.rodarVideo = False
    self.VideoThread = None

    self.initUi()

    self.abrirImagem()

  def initUi(self):
    self.btnVideo.clicked.connect(self.startVideo)
    self.btnEffBlur.clicked.connect(self.open_dialog_blur)
    self.btnEffGaussBlur.clicked.connect(self.open_dialog_gaussianblur)
    self.btnEffMedBlur.clicked.connect(self.open_dialog_medianblur)
    self.btnInRange.clicked.connect(self.open_dialog_inrange)
    self.btnErode.clicked.connect(self.open_dialog_erode)
    self.btnDilate.clicked.connect(self.open_dialog_dilate)
    self.btnCanny.clicked.connect(self.open_dialog_canny)
    self.btnNegativo.clicked.connect(self.negativo)
    self.btnAdaptThresh.clicked.connect(self.open_dialog_adaptive_threshold)
    self.actionAbrir.triggered.connect(self.abrirImagem)
    self.actionSalvar.triggered.connect(self.salvarImagem)
    self.btnHist.clicked.connect(self.histograma)

    self.listModel = QStandardItemModel(self.listEffects)
    self.listEffects.setModel(self.listModel)
    self.listModel.itemChanged.connect(self.updateImage)

    self.listEffects.setAcceptDrops(True)
    self.listEffects.setDragEnabled(True)
    self.listEffects.setDragDropMode(QAbstractItemView.InternalMove)
    self.listEffects.setDefaultDropAction(Qt.MoveAction)
    self.listEffects.setDropIndicatorShown(True)

    self.comboBox_2.addItem("BGR  ▶️  RGB", cv2.COLOR_BGR2RGB)
    self.comboBox_2.addItem("BGR  ▶️  HSV", cv2.COLOR_BGR2HSV)
    self.comboBox_2.addItem("BGR  ▶️  XYZ", cv2.COLOR_BGR2XYZ)
    self.comboBox_2.addItem("BGR  ▶️ GRAY", cv2.COLOR_BGR2GRAY)
    self.comboBox_2.addItem("BGR  ▶️  LAB", cv2.COLOR_BGR2LAB)
    self.comboBox_2.addItem("BGR  ▶️  LUV", cv2.COLOR_BGR2LUV)
    self.comboBox_2.addItem("RGB  ▶️  BGR", cv2.COLOR_RGB2BGR)
    self.comboBox_2.addItem("HSV  ▶️  BGR", cv2.COLOR_HSV2BGR)
    self.comboBox_2.addItem("GRAY ▶️  BGR", cv2.COLOR_GRAY2BGR)
    self.comboBox_2.addItem("LAB  ▶️  BGR", cv2.COLOR_LAB2BGR)
    self.comboBox_2.addItem("LUV  ▶️  BGR", cv2.COLOR_LUV2BGR)

    self.comboBox_2.currentIndexChanged.connect(self.changeImageColor)

  def colorDialog(self):
    color = QColorDialog.getColor()
    self.lblPos.setStyleSheet('color: {}'.format(color.name()))

  def abrirImagem(self):
    filename, _ = QFileDialog.getOpenFileName(
      self, 'Buscar Imagem', '.', 'Image Files (*.png *.jpg *.jpeg *.bmp)')
    if filename:
      self.image = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
      with open(filename, "rb") as file:
        data = np.array(bytearray(file.read()))

        self.image = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
        self.original = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
        self.mostrarImagem()

  def salvarImagem(self):
    filename, _ = QFileDialog.getSaveFileName(
      self, 'Salvar Imagem', '.', 'Image Files (*.png *.jpg *.jpeg *.bmp)')
    if filename:
      cv2.imwrite(filename, self.image)

  def mouseMoveEvent(self, ev):
    pos = None
    if self.tabWidget.currentIndex() == 0:
      pos = self.lblImg.mapFrom(self.centralwidget, self.lblImg.pos())
    elif self.tabWidget.currentIndex() == 1:
      pos = self.lblImgLayer0.mapFrom(self.centralwidget, self.lblImgLayer0.pos())
    elif self.tabWidget.currentIndex() == 2:
      pos = self.lblImgLayer1.mapFrom(self.centralwidget, self.lblImgLayer1.pos())
    elif self.tabWidget.currentIndex() == 3:
      pos = self.lblImgLayer2.mapFrom(self.centralwidget, self.lblImgLayer2.pos())

    x = ev.localPos().x() + pos.x() - 10
    y = ev.localPos().y() + pos.y() - 38

    self.lblPos.setText("{}x{}".format(x, y))
    return super().mouseMoveEvent(ev)

  def mostrarImagem(self):
    size = self.image.shape
    step = self.image.size / size[0]
    qformat = QImage.Format_Indexed8

    self.imageSp = cv2.split(self.image)

    if len(size) == 3:
      qformat = QImage.Format_RGBA8888 if size[2] == 4 else QImage.Format_RGB888

    img = QImage(self.image, size[1], size[0], step, qformat).rgbSwapped()
    imgSp0 = QImage(self.imageSp[0], size[1], size[0], step/3, QImage.Format_Indexed8)
    imgSp1 = QImage(self.imageSp[1], size[1], size[0], step/3, QImage.Format_Indexed8)
    imgSp2 = QImage(self.imageSp[2], size[1], size[0], step/3, QImage.Format_Indexed8)
    
    self.lblImg.setPixmap(QPixmap.fromImage(img))
    self.lblImgLayer0.setPixmap(QPixmap.fromImage(imgSp0))
    self.lblImgLayer1.setPixmap(QPixmap.fromImage(imgSp1))
    self.lblImgLayer2.setPixmap(QPixmap.fromImage(imgSp2))

  def histograma(self):
    if self.image is not None:
      img = self.image
      color = ('b', 'g', 'r')
      for i, col in enumerate(color):
        histr = cv2.calcHist([img], [i], None, [256], [0, 256])
        plt.plot(histr, color=col)
        plt.xlim([0, 256])
      plt.show()

  def updateImage(self):
    self.image = self.original

    for i in range(self.listModel.rowCount()):
      if self.listModel.item(i).checkState():
        filter = self.listModel.item(i).data()
        self.image = applyFilters(self.image, filter['filterType'], filter['params'])
    
    self.mostrarImagem()

  def open_dialog_blur(self):
    filter = {
      "filterType": "blur",
      "params": {
        1: { "name": "Kernel", "val": 3 }
      }
    }
    value = PopUpDLG(self.image, filter).exec_()
    if value: self.addItemToList("Blur Kernel={}".format(filter['params'][1]['val']), value)

  def open_dialog_gaussianblur(self):
    filter = {
      "filterType": "gaussianblur",
      "params": {
        1: { "name": "Kernel", "val": 3 }
      }
    }
    value = PopUpDLG(self.image, filter).exec_()
    if value: self.addItemToList("Gaussian Blur Kernel={}".format(
      filter['params'][1]['val']), value) 

  def open_dialog_medianblur(self):
    filter = {
      "filterType": "medianblur",
      "params": {
        1: { "name": "Kernel", "val": 3 }
      }
    }
    value = PopUpDLG(self.image, filter).exec_()
    if value: self.addItemToList("Median Blur Kernel={}".format(
      filter['params'][1]['val']), value) 

  def open_dialog_adaptive_threshold(self):
    filter = {
      "filterType": "adaptivethreshold",
      "params": {
        1: { "name": "Kernel", "val": 3 }
      }
    }
    value = PopUpDLG(self.image, filter).exec_()
    if value: self.addItemToList("Threshold Adaptativo de {}".format(
      filter['params'][1]['val']), value) 

  def open_dialog_inrange(self):
    filter = {
      "filterType": "inrange",
      "params": {
        1: { "name": "Inicial", "val": 0 },
        2: { "name": "Final", "val": 255 }
      }
    }
    value = PopUpDLG(self.image, filter).exec_()
    if value: self.addItemToList("In Range Entre {} e {}".format(
      filter['params'][1]['val'],
      filter['params'][2]['val']), value)

  def open_dialog_erode(self):
    filter = {
      "filterType": "erode",
      "params": {
        1: { "name": "Kernel", "val": 0 }
      }
    }
    value = PopUpDLG(self.image, filter).exec_()
    if value: self.addItemToList("Erode de {}".format(
      filter['params'][1]['val']), value) 

  def open_dialog_dilate(self):
    filter = {
      "filterType": "dilate",
      "params": {
        1: { "name": "Kernel", "val": 0 }
      }
    }
    value = PopUpDLG(self.image, filter).exec_()
    if value: self.addItemToList("Dilate de {}".format(
      filter['params'][1]['val']), value) 

  def open_dialog_canny(self):
    filter = {
      "filterType": "canny",
      "params": {
        1: { "name": "Inicial", "val": 100 },
        2: { "name": "Final", "val": 200 }
      }
    }
    value = PopUpDLG(self.image, filter).exec_()
    if value: self.addItemToList("Canny Entre {} e {}".format(
      filter['params'][1]['val'],
      filter['params'][2]['val']), value)

  def negativo(self):
    filter = {
      "filterType": "negativo",
      "params": {}
    }
    self.addItemToList("negativo", filter)

  def changeImageColor(self):
    filter = {
      "filterType": "colorchange",
      "params": {
        1: { "name": "Cor", "val": self.comboBox_2.currentData() }
      }
    }
    self.addItemToList("Mudanca de Cor {}".format(
      self.comboBox_2.currentText()), filter)

  def addItemToList(self, name, filter):
    item = QStandardItem(name)
    item.setData(filter)
    item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsSelectable 
      | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsEnabled)
    item.setCheckState(Qt.Checked)
    self.listModel.appendRow(item)

    self.updateImage()

  def startVideo(self):
    if not self.rodarVideo:
      self.rodarVideo = True
      self.VideoThread = Thread(self)
      self.VideoThread.changePixmap.connect(self.setImage)
      self.VideoThread.start()
    else:
      self.rodarVideo = False
      self.VideoThread.quit()

  def stopVideo(self):
    pass

  @QtCore.pyqtSlot(object)
  def setImage(self, image):
    if image.any():
      self.original = image
      self.updateImage()
    # self.mostrarImagem()

def main():
  app = QtWidgets.QApplication(sys.argv)
  application = ApplicationWindow()
  application.show()
  app.exec_()

if __name__ == "__main__":
  main()
