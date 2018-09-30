import cv2
import numpy as np

def applyFilters(image, filterType, parameters):
  if   filterType == 'blur':
    image = cv2.blur(image, (parameters[1]['val']+3, parameters[1]['val']+3))

  elif filterType == 'gaussianblur':
    image = cv2.GaussianBlur(image, (parameters[1]['val'] * 2 + 1, parameters[1]['val'] * 2 + 1), 0, 0)

  elif filterType == 'medianblur':
    image = cv2.medianBlur(image, parameters[1]['val'] * 2 + 1)

  elif filterType == 'negativo':
    img = cv2.split(image)
    for i, camada in enumerate(img):
      img[i] = cv2.subtract(255, camada)
    image = cv2.merge(img)

  elif filterType == 'adaptivethreshold':
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.adaptiveThreshold(
      image, 
      parameters[1]['val']*2+1, 
      cv2.ADAPTIVE_THRESH_MEAN_C, 
      cv2.THRESH_BINARY, 
      3, 
      0)
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

  elif filterType == 'colorchange':
    if parameters[1]['val'] == cv2.COLOR_BGR2GRAY:
      image = cv2.cvtColor(image, parameters[1]['val'])
      image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    elif parameters[1]['val'] == cv2.COLOR_GRAY2BGR:
      image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
      image = cv2.cvtColor(image, parameters[1]['val'])
    else:
      image = cv2.cvtColor(image, parameters[1]['val'])

  elif filterType == 'inrange':
    image = cv2.inRange(
      image, 
      (parameters[1]['val'], parameters[1]['val'], parameters[1]['val']), 
      (parameters[2]['val'], parameters[2]['val'], parameters[2]['val']))
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
  
  elif filterType == 'erode':
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((3, 3), np.uint8)
    image = cv2.erode(image, kernel, iterations=parameters[1]['val'])
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

  elif filterType == 'dilate':
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((3, 3), np.uint8)
    image = cv2.dilate(image, kernel, iterations=parameters[1]['val'])
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

  elif filterType == 'canny':
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.Canny(image, parameters[1]['val'], parameters[2]['val'])
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

  return image
