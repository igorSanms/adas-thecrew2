import cv2
import numpy as np

def aplicar_roi(frame):

    altura, largura = frame.shape[:2]

    mascara = np.zeros_like(frame)

    poligono = np.array([[
        (0, 820),             # Inferior esquerdo (quase na base)
        (946, 455),                   # Superior esquerdo (perto do horizonte)
        (992, 455),                  # Superior direito
        (largura, 820)        # Inferior direito
    ]], np.int32)
    

    cv2.fillPoly(mascara, poligono, (255, 255, 255))
    
    frame_cortado = cv2.bitwise_and(frame, mascara)
    
    return frame_cortado