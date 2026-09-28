import cv2
import numpy as np

def aplicar_roi(frame):
    """
    Aplica uma máscara poligonal na imagem para focar apenas na estrada.
    """
    # Pega as dimensões da imagem (altura, largura, canais de cor)
    altura, largura = frame.shape[:2]
    
    # 1. Cria uma tela preta (tudo zero) com o mesmo tamanho da imagem original
    mascara = np.zeros_like(frame)
    
    # 2. Define os pontos do nosso trapézio (coordenadas X, Y)
    # Esses valores foram pensados para uma resolução de 1920x1080
    # Caso a câmera mude, esses pontos precisarão de ajuste.
    poligono = np.array([[
        (0, 820),             # Inferior esquerdo (quase na base)
        (946, 455),                   # Superior esquerdo (perto do horizonte)
        (992, 455),                  # Superior direito
        (largura, 820)        # Inferior direito
    ]], np.int32)
    
    # 3. Desenha um polígono branco (255, 255, 255) sobre a tela preta
    cv2.fillPoly(mascara, poligono, (255, 255, 255))
    
    # 4. Aplica a máscara na imagem original usando uma operação matemática "E" (AND)
    # Apenas onde a máscara for branca, a imagem original aparecerá.
    frame_cortado = cv2.bitwise_and(frame, mascara)
    
    return frame_cortado