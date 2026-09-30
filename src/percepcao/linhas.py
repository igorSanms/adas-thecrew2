import cv2
import numpy as np

memoria = {
    "largura_faixa": 800,       
    "centro_suavizado": None   
}

def extrapolar_linha(pontos_linha, altura, y_minimo):
    if len(pontos_linha) == 0:
        return None
        
    pontos_linha = np.array(pontos_linha)
    m_medio = np.mean(pontos_linha[:, 0])
    b_medio = np.mean(pontos_linha[:, 1])
    
    y1 = altura
    y2 = y_minimo
    
    x1 = int((y1 - b_medio) / m_medio)
    x2 = int((y2 - b_medio) / m_medio)
    
    return (x1, y1, x2, y2)

def detectar_linhas_e_centro(mascara_bordas, frame_colorido):
    global memoria 
    
    frame_desenho = frame_colorido.copy()
    altura, largura = frame_desenho.shape[:2]
    y_horizonte = 600
    
    linhas = cv2.HoughLinesP(mascara_bordas, rho=1, theta=np.pi/180, 
                             threshold=50, minLineLength=50, maxLineGap=50)
    
    dados_esq = []
    dados_dir = []
    
    if linhas is not None:
        for linha in linhas:
            x1, y1, x2, y2 = linha.flatten()
            if x2 == x1: continue 
                
            inclinacao = (y2 - y1) / (x2 - x1)
            intercepto = y1 - (inclinacao * x1)
            
            if abs(inclinacao) < 0.6: continue
                
            if inclinacao < 0:
                dados_esq.append((inclinacao, intercepto))
            else:
                dados_dir.append((inclinacao, intercepto))

    linha_esq = extrapolar_linha(dados_esq, altura, y_horizonte)
    linha_dir = extrapolar_linha(dados_dir, altura, y_horizonte)
    
    centro_instantaneo = None
    
    if linha_esq is not None and linha_dir is not None:
        cv2.line(frame_desenho, (linha_esq[0], linha_esq[1]), (linha_esq[2], linha_esq[3]), (255, 0, 0), 5)
        cv2.line(frame_desenho, (linha_dir[0], linha_dir[1]), (linha_dir[2], linha_dir[3]), (0, 255, 0), 5)
        
        memoria["largura_faixa"] = linha_dir[0] - linha_esq[0]
        centro_instantaneo = int((linha_esq[0] + linha_dir[0]) / 2)
        
    elif linha_esq is not None:
        cv2.line(frame_desenho, (linha_esq[0], linha_esq[1]), (linha_esq[2], linha_esq[3]), (255, 0, 0), 5)
        centro_instantaneo = int(linha_esq[0] + (memoria["largura_faixa"] / 2))
        
    elif linha_dir is not None:
        cv2.line(frame_desenho, (linha_dir[0], linha_dir[1]), (linha_dir[2], linha_dir[3]), (0, 255, 0), 5)
        centro_instantaneo = int(linha_dir[0] - (memoria["largura_faixa"] / 2))

    if centro_instantaneo is not None:
        if memoria["centro_suavizado"] is None:
            memoria["centro_suavizado"] = centro_instantaneo
        else:
            alpha = 0.2 
            memoria["centro_suavizado"] = int((1 - alpha) * memoria["centro_suavizado"] + alpha * centro_instantaneo)

    centro_final = memoria["centro_suavizado"]
    centro_carro = largura // 2
    erro = 0 
    
    if centro_final is not None:
        erro = centro_carro - centro_final
        cv2.circle(frame_desenho, (centro_final, altura - 50), 10, (0, 0, 255), -1)
        cv2.circle(frame_desenho, (centro_carro, altura - 50), 10, (0, 255, 255), -1)
        cv2.line(frame_desenho, (centro_carro, altura - 50), (centro_final, altura - 50), (255, 255, 255), 2)
    
    return frame_desenho, erro