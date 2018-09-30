"""Arquivo principal do projeto"""
# python3
# coding=utf-8
import sys
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtGui import QImage, QPixmap, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QAbstractItemView
import numpy as np
import cv2
from matplotlib import pyplot as plt

from main_dialog import FilterDialog
from video_thread import Thread
from filters import apply_filters

class ApplicationWindow(QtWidgets.QMainWindow):
    """Clase da Janela principal"""

    def __init__(self):
        super(ApplicationWindow, self).__init__()

        uic.loadUi('main_window.ui', self)
        self.image = None
        self.original = None
        self.rodar_video = False
        self.video_thread = None
        self.image_sp = None
        self.init_ui()
        self.abrir_imagem()

    def init_ui(self):
        """Método que inicializa a interface"""
        self.btnVideo.clicked.connect(self.start_video)
        self.btnEffBlur.clicked.connect(self.open_dialog_blur)
        self.btnEffGaussBlur.clicked.connect(self.open_dialog_gaussianblur)
        self.btnEffMedBlur.clicked.connect(self.open_dialog_medianblur)
        self.btnInRange.clicked.connect(self.open_dialog_inrange)
        self.btnErode.clicked.connect(self.open_dialog_erode)
        self.btnDilate.clicked.connect(self.open_dialog_dilate)
        self.btnCanny.clicked.connect(self.open_dialog_canny)
        self.btnNegativo.clicked.connect(self.negativo)
        self.btnAdaptThresh.clicked.connect(
            self.open_dialog_adaptive_threshold)
        self.actionAbrir.triggered.connect(self.abrir_imagem)
        self.actionSalvar.triggered.connect(self.salvar_imagem)
        self.btnHist.clicked.connect(self.histograma)

        self.list_model = QStandardItemModel(self.listEffects)
        self.listEffects.setModel(self.list_model)
        self.list_model.itemChanged.connect(self.update_image)

        self.listEffects.setAcceptDrops(True)
        self.listEffects.setDragEnabled(True)
        self.listEffects.setDragDropMode(QAbstractItemView.InternalMove)
        self.listEffects.setDefaultDropAction(Qt.MoveAction)
        self.listEffects.setDropIndicatorShown(True)

        self.comboBox_2.addItem("BGR    ▶️    RGB", cv2.COLOR_BGR2RGB)
        self.comboBox_2.addItem("BGR    ▶️    HSV", cv2.COLOR_BGR2HSV)
        self.comboBox_2.addItem("BGR    ▶️    XYZ", cv2.COLOR_BGR2XYZ)
        self.comboBox_2.addItem("BGR    ▶️ GRAY", cv2.COLOR_BGR2GRAY)
        self.comboBox_2.addItem("BGR    ▶️    LAB", cv2.COLOR_BGR2LAB)
        self.comboBox_2.addItem("BGR    ▶️    LUV", cv2.COLOR_BGR2LUV)
        self.comboBox_2.addItem("RGB    ▶️    BGR", cv2.COLOR_RGB2BGR)
        self.comboBox_2.addItem("HSV    ▶️    BGR", cv2.COLOR_HSV2BGR)
        self.comboBox_2.addItem("GRAY ▶️    BGR", cv2.COLOR_GRAY2BGR)
        self.comboBox_2.addItem("LAB    ▶️    BGR", cv2.COLOR_LAB2BGR)
        self.comboBox_2.addItem("LUV    ▶️    BGR", cv2.COLOR_LUV2BGR)

        self.comboBox_2.currentIndexChanged.connect(self.change_image_color)

    def abrir_imagem(self):
        """Método que exibe diálogo para abrir a imagem"""
        filename, _ = QFileDialog.getOpenFileName(
            self, 'Buscar Imagem', '.', 'Image Files (*.png *.jpg *.jpeg *.bmp)')
        if filename:
            self.image = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
            with open(filename, "rb") as file:
                data = np.array(bytearray(file.read()))

                self.image = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
                self.original = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
                self.mostrar_imagem()

    def salvar_imagem(self):
        """Método que exibe diálogo para salvar a imagem"""
        filename, _ = QFileDialog.getSaveFileName(
            self, 'Salvar Imagem', '.', 'Image Files (*.png *.jpg *.jpeg *.bmp)')
        if filename:
            cv2.imwrite(filename, self.image)

    def mouse_move_event(self, ev):
        """Método que exibe diálogo para controlar o movimento do mouse"""
        pos = None
        if self.tabWidget.currentIndex() == 0:
            pos = self.lblImg.mapFrom(self.centralwidget, self.lblImg.pos())
        elif self.tabWidget.currentIndex() == 1:
            pos = self.lblImgLayer0.mapFrom(
                self.centralwidget, self.lblImgLayer0.pos())
        elif self.tabWidget.currentIndex() == 2:
            pos = self.lblImgLayer1.mapFrom(
                self.centralwidget, self.lblImgLayer1.pos())
        elif self.tabWidget.currentIndex() == 3:
            pos = self.lblImgLayer2.mapFrom(
                self.centralwidget, self.lblImgLayer2.pos())

        x = ev.localPos().x() + pos.x() - 10
        y = ev.localPos().y() + pos.y() - 38

        self.lblPos.setText("{}x{}".format(x, y))
        return super().mouse_move_event(ev)

    def mostrar_imagem(self):
        """Método responsável por exibir a imagem nas abas"""
        size = self.image.shape
        step = self.image.size / size[0]
        qformat = QImage.Format_Indexed8

        self.image_sp = cv2.split(self.image)

        if len(size) == 3:
            qformat = QImage.Format_RGBA8888 if size[2] == 4 else QImage.Format_RGB888

        img = QImage(self.image, size[1], size[0], step, qformat).rgbSwapped()
        img_split_0 = QImage(
            self.image_sp[0], size[1], size[0], step/3, QImage.Format_Indexed8)
        img_split_1 = QImage(
            self.image_sp[1], size[1], size[0], step/3, QImage.Format_Indexed8)
        img_split_2 = QImage(
            self.image_sp[2], size[1], size[0], step/3, QImage.Format_Indexed8)

        self.lblImg.setPixmap(QPixmap.fromImage(img))
        self.lblImgLayer0.setPixmap(QPixmap.fromImage(img_split_0))
        self.lblImgLayer1.setPixmap(QPixmap.fromImage(img_split_1))
        self.lblImgLayer2.setPixmap(QPixmap.fromImage(img_split_2))

    def histograma(self):
        """Método que gera o histograma"""
        if self.image is not None:
            img = self.image
            color = ('b', 'g', 'r')
            for i, col in enumerate(color):
                histr = cv2.calcHist([img], [i], None, [256], [0, 256])
                plt.plot(histr, color=col)
                plt.xlim([0, 256])
            plt.show()

    def update_image(self):
        """Método que atualiza a imagem"""
        self.image = self.original

        for i in range(self.list_model.rowCount()):
            if self.list_model.item(i).checkState():
                filtros = self.list_model.item(i).data()
                self.image = apply_filters(self.image,
                                           filtros['filter_type'], filtros['params'])

        self.mostrar_imagem()

    def open_dialog_blur(self):
        """Método responsável por exibir diálogo para Blur"""
        filtros = {
            "filter_type": "blur",
            "params": {
                1: {"name": "Kernel", "val": 3}
            }
        }
        value = FilterDialog(self.image, filtros).exec_()
        if value:
            self.add_lista_filtros(
                "Blur Kernel={}".format(filtros['params'][1]['val']), value)

    def open_dialog_gaussianblur(self):
        """Método responsável por exibir diálogo para Blur Gaussiano"""
        filtros = {
            "filter_type": "gaussianblur",
            "params": {
                1: {"name": "Kernel", "val": 3}
            }
        }
        value = FilterDialog(self.image, filtros).exec_()
        if value:
            self.add_lista_filtros("Gaussian Blur Kernel={}".format(
                filtros['params'][1]['val']), value)

    def open_dialog_medianblur(self):
        """Método responsável por exibir diálogo para Blur Mediano"""

        filtros = {
            "filter_type": "medianblur",
            "params": {
                1: {"name": "Kernel", "val": 3}
            }
        }
        value = FilterDialog(self.image, filtros).exec_()
        if value:
            self.add_lista_filtros("Median Blur Kernel={}".format(
                filtros['params'][1]['val']), value)

    def open_dialog_adaptive_threshold(self):
        """Método responsável por exibir diálogo para Threshold Adaptativo"""

        filtros = {
            "filter_type": "adaptivethreshold",
            "params": {
                1: {"name": "Kernel", "val": 3}
            }
        }
        value = FilterDialog(self.image, filtros).exec_()
        if value:
            self.add_lista_filtros("Threshold Adaptativo de {}".format(
                filtros['params'][1]['val']), value)

    def open_dialog_inrange(self):
        """Método responsável por exibir diálogo para Inrange"""
        filtros = {
            "filter_type": "inrange",
            "params": {
                1: {"name": "Inicial", "val": 0},
                2: {"name": "Final", "val": 255}
            }
        }
        value = FilterDialog(self.image, filtros).exec_()
        if value:
            self.add_lista_filtros("In Range Entre {} e {}".format(
                filtros['params'][1]['val'],
                filtros['params'][2]['val']), value)

    def open_dialog_erode(self):
        """Método responsável por exibir diálogo para Erode"""

        filtros = {
            "filter_type": "erode",
            "params": {
                1: {"name": "Kernel", "val": 0}
            }
        }
        value = FilterDialog(self.image, filtros).exec_()
        if value:
            self.add_lista_filtros("Erode de {}".format(
                filtros['params'][1]['val']), value)

    def open_dialog_dilate(self):
        """Método responsável por exibir diálogo para Dilate"""
        filtros = {
            "filter_type": "dilate",
            "params": {
                1: {"name": "Kernel", "val": 0}
            }
        }
        value = FilterDialog(self.image, filtros).exec_()
        if value:
            self.add_lista_filtros("Dilate de {}".format(
                filtros['params'][1]['val']), value)

    def open_dialog_canny(self):
        """Método responsável por exibir diálogo para Canny"""
        filtros = {
            "filter_type": "canny",
            "params": {
                1: {"name": "Inicial", "val": 100},
                2: {"name": "Final", "val": 200}
            }
        }
        value = FilterDialog(self.image, filtros).exec_()
        if value:
            self.add_lista_filtros("Canny Entre {} e {}".format(
                filtros['params'][1]['val'],
                filtros['params'][2]['val']), value)

    def negativo(self):
        """Método responsável por aplicar negativo"""
        filtros = {
            "filter_type": "negativo",
            "params": {}
        }
        self.add_lista_filtros("negativo", filtros)

    def change_image_color(self):
        """Método responsável por alterar a cor da imagem"""
        filtros = {
            "filter_type": "colorchange",
            "params": {
                1: {"name": "Cor", "val": self.comboBox_2.currentData()}
            }
        }
        self.add_lista_filtros("Mudanca de Cor {}".format(
            self.comboBox_2.currentText()), filtros)

    def add_lista_filtros(self, name, filtros):
        """Método que adiciona o filtro selecionado na lista"""
        item = QStandardItem(name)
        item.setData(filtros)
        item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsSelectable
                      | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
                      | Qt.ItemIsEnabled)
        item.setCheckState(Qt.Checked)
        self.list_model.appendRow(item)

        self.update_image()

    def start_video(self):
        """Método que inicializa o vídeo"""
        if not self.rodar_video:
            self.rodar_video = True
            self.video_thread = Thread(self)
            self.video_thread.changePixmap.connect(self.set_image)
            self.video_thread.start()
        else:
            self.rodar_video = False
            self.video_thread.quit()

    def stop_video(self):
        """Método que para o vídeo"""
        pass

    @QtCore.pyqtSlot(object)
    def set_image(self, image):
        """Método que atualiza os frames do vídeo"""
        if image.any():
            self.original = image
            self.update_image()
        # self.mostrar_imagem()

def main():
    """Inicializador da aplicação"""
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    app.exec_()

if __name__ == "__main__":
    main()
