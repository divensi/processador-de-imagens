"""Dialogo para previsão da aplicação de filtros"""
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QImage, QPixmap

from filters import apply_filters

class FilterDialog(QtWidgets.QDialog):
    """Classe do diálogo"""
    def __init__(self, image=None, filtros=None):
        super(FilterDialog, self).__init__()

        self.filtros = filtros
        self.image = image
        self.original = image

        uic.loadUi('dialog.ui', self)

        self.init_ui()
        self.mostrar_imagem()

    def init_ui(self):
        """Método de inicialização"""
        if 1 in self.filtros['params']:
            self.sldExample.valueChanged.connect(self.slider_parametro_1)
            self.lblExample.setText(self.filtros['params'][1]['name'])
            self.sldExample.setEnabled(True)

        if 2 in self.filtros['params']:
            self.sldExample_2.valueChanged.connect(self.slider_parametro_2)
            self.lblExample_2.setText(self.filtros['params'][2]['name'])
            self.sldExample_2.setEnabled(True)

        if 3 in self.filtros['params']:
            self.sldExample_3.valueChanged.connect(self.slider_parametro_3)
            self.lblExample_3.setText(self.filtros['params'][3]['name'])
            self.sldExample_3.setEnabled(True)

    def slider_parametro_1(self):
        """Método do slider 1"""
        size = self.sldExample.value()
        self.filtros['params'][1]['val'] = size
        self.mostrar_imagem()

    def slider_parametro_2(self):
        """Método do slider 2"""
        size = self.sldExample_2.value()
        self.filtros['params'][2]['val'] = size
        self.mostrar_imagem()

    def slider_parametro_3(self):
        """Método do slider 3"""
        size = self.sldExample_3.value()
        self.filtros['params'][3]['val'] = size
        self.mostrar_imagem()

    def mostrar_imagem(self):
        """Método para previsão da imagem"""
        self.image = apply_filters(
            self.original, self.filtros['filter_type'], self.filtros['params'])
        size = self.image.shape
        step = self.image.size / size[0]

        qformat = QImage.Format_RGBA8888 if size[2] == 4 else QImage.Format_RGB888
        img = QImage(self.image, size[1], size[0], step, qformat).rgbSwapped()
        self.lblImage.setPixmap(QPixmap.fromImage(img))

    def exec_(self):
        """Método de retorno do diálogo"""
        super(FilterDialog, self).exec_()
        return self.filtros
