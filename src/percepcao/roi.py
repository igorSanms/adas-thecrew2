import cv2
import numpy as np

def aplicar_roi(frame):
    altura, largura = frame.shape[:2]
    mascara = np.zeros_like(frame)
    
    poligono = np.array([[
        (0, 820),
        (946, 455),
        (992, 455),
        (largura, 820)
    ]], np.int32)
    
    cor_preenchimento = (255, 255, 255) if len(frame.shape) == 3 else 255
    
    cv2.fillPoly(mascara, poligono, cor_preenchimento)
    frame_cortado = cv2.bitwise_and(frame, mascara)
    
    return frame_cortado