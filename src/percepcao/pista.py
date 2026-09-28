import cv2
import numpy as np

def detectar_faixas_bordas(frame_roi):

    cinza = cv2.cvtColor(frame_roi, cv2.COLOR_BGR2GRAY)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

    cinza_contrastado = clahe.apply(cinza)
    
    desfoque = cv2.GaussianBlur(cinza_contrastado, (5, 5), 0)
    
    bordas = cv2.Canny(desfoque, 50, 150)
    
    return bordas