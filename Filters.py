"""Módulo responsável por aplicar os filtros do OpenCV"""
import cv2
import numpy as np

def apply_filters(image, filter_type, parameters):
    """Função para aplicar os filtros"""
    if filter_type == 'blur':
        image = cv2.blur(
            image, (parameters[1]['val']+3, parameters[1]['val']+3))

    elif filter_type == 'gaussianblur':
        image = cv2.GaussianBlur(image,
                                 (parameters[1]['val'] * 2 + 1,
                                  parameters[1]['val'] * 2 + 1),
                                 0,
                                 0)

    elif filter_type == 'medianblur':
        image = cv2.medianBlur(image, parameters[1]['val'] * 2 + 1)

    elif filter_type == 'negativo':
        img = cv2.split(image)
        for i, camada in enumerate(img):
            img[i] = cv2.subtract(255, camada)
        image = cv2.merge(img)

    elif filter_type == 'adaptivethreshold':
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.adaptiveThreshold(
            image,
            parameters[1]['val']*2+1,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            3,
            0)
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    elif filter_type == 'colorchange':
        if parameters[1]['val'] == cv2.COLOR_BGR2GRAY:
            image = cv2.cvtColor(image, parameters[1]['val'])
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        elif parameters[1]['val'] == cv2.COLOR_GRAY2BGR:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image = cv2.cvtColor(image, parameters[1]['val'])
        else:
            image = cv2.cvtColor(image, parameters[1]['val'])

    elif filter_type == 'inrange':
        image = cv2.inRange(
            image,
            (parameters[1]['val'], parameters[1]['val'], parameters[1]['val']),
            (parameters[2]['val'], parameters[2]['val'], parameters[2]['val']))
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    elif filter_type == 'erode':
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((3, 3), np.uint8)
        image = cv2.erode(image, kernel, iterations=parameters[1]['val'])
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    elif filter_type == 'dilate':
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((3, 3), np.uint8)
        image = cv2.dilate(image, kernel, iterations=parameters[1]['val'])
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    elif filter_type == 'canny':
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.Canny(image, parameters[1]['val'], parameters[2]['val'])
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    return image
