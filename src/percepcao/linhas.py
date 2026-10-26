import cv2
import numpy as np

memoria = {
    "largura_faixa": 800,
    "centro_suavizado": None,
    "esq_m": None, "esq_b": None,
    "dir_m": None, "dir_b": None
}

def suavizar_linha(novo_m, novo_b, lado):
    global memoria
    alpha = 0.5 
    chave_m = f"{lado}_m"
    chave_b = f"{lado}_b"
    
    if memoria[chave_m] is None:
        memoria[chave_m] = novo_m
        memoria[chave_b] = novo_b
        return novo_m, novo_b
        
    erro_inclinacao = abs(memoria[chave_m] - novo_m)
    if erro_inclinacao > 0.8:
        memoria[chave_m] = 0.95 * memoria[chave_m] + 0.05 * novo_m
        memoria[chave_b] = 0.95 * memoria[chave_b] + 0.05 * novo_b
        return memoria[chave_m], memoria[chave_b]
        
    memoria[chave_m] = (1 - alpha) * memoria[chave_m] + alpha * novo_m
    memoria[chave_b] = (1 - alpha) * memoria[chave_b] + alpha * novo_b
    return memoria[chave_m], memoria[chave_b]

def extrapolar_linha(pontos_linha, altura, y_minimo, lado):
    global memoria
    if len(pontos_linha) == 0:
        if memoria[f"{lado}_m"] is not None:
            m_final = memoria[f"{lado}_m"]
            b_final = memoria[f"{lado}_b"]
        else:
            return None
    else:
        pontos_linha = np.array(pontos_linha)
        m_bruto = np.mean(pontos_linha[:, 0])
        b_bruto = np.mean(pontos_linha[:, 1])
        m_final, b_final = suavizar_linha(m_bruto, b_bruto, lado)
    
    y1 = altura
    y2 = y_minimo
    x1 = int((y1 - b_final) / m_final)
    x2 = int((y2 - b_final) / m_final)
    return (x1, y1, x2, y2)

def calcular_x_na_mira(linha, y_mira):
    x1, y1, x2, y2 = linha
    if y2 == y1: return x1
    return int(x1 + (x2 - x1) * ((y_mira - y1) / (y2 - y1)))

def detectar_linhas_e_centro(mascara_bordas, frame_colorido):
    global memoria 
    
    frame_desenho = frame_colorido.copy()
    altura, largura = frame_desenho.shape[:2]
    y_horizonte = 600
    y_mira = altura - 250 
    
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
            x_base = int((altura - intercepto) / inclinacao)

            if 700 < x_base < 1200:
                continue 
            if inclinacao < 0:
                dados_esq.append((inclinacao, intercepto))
            else:
                dados_dir.append((inclinacao, intercepto))

    linha_esq = extrapolar_linha(dados_esq, altura, y_horizonte, "esq")
    linha_dir = extrapolar_linha(dados_dir, altura, y_horizonte, "dir")
    
    centro_instantaneo = None
    
    if linha_esq is not None and linha_dir is not None:
        cv2.line(frame_desenho, (linha_esq[0], linha_esq[1]), (linha_esq[2], linha_esq[3]), (255, 0, 0), 5)
        cv2.line(frame_desenho, (linha_dir[0], linha_dir[1]), (linha_dir[2], linha_dir[3]), (0, 255, 0), 5)
        
        x_mira_esq = calcular_x_na_mira(linha_esq, y_mira)
        x_mira_dir = calcular_x_na_mira(linha_dir, y_mira)
        
        memoria["largura_faixa"] = x_mira_dir - x_mira_esq
        centro_instantaneo = int((x_mira_esq + x_mira_dir) / 2)
        
    elif linha_esq is not None:
        cv2.line(frame_desenho, (linha_esq[0], linha_esq[1]), (linha_esq[2], linha_esq[3]), (255, 0, 0), 5)
        x_mira_esq = calcular_x_na_mira(linha_esq, y_mira)
        centro_instantaneo = int(x_mira_esq + (memoria["largura_faixa"] / 2))
        
    elif linha_dir is not None:
        cv2.line(frame_desenho, (linha_dir[0], linha_dir[1]), (linha_dir[2], linha_dir[3]), (0, 255, 0), 5)
        x_mira_dir = calcular_x_na_mira(linha_dir, y_mira)
        centro_instantaneo = int(x_mira_dir - (memoria["largura_faixa"] / 2))

    if centro_instantaneo is not None:
        if memoria["centro_suavizado"] is None:
            memoria["centro_suavizado"] = centro_instantaneo
        else:
            alpha_centro = 0.5 
            memoria["centro_suavizado"] = int((1 - alpha_centro) * memoria["centro_suavizado"] + alpha_centro * centro_instantaneo)

    centro_final = memoria["centro_suavizado"]
    centro_carro = largura // 2
    erro = 0 
    
    if centro_final is not None:
        erro = centro_final - centro_carro
        
        cv2.circle(frame_desenho, (centro_final, y_mira), 10, (0, 0, 255), -1)
        cv2.circle(frame_desenho, (centro_carro, y_mira), 10, (0, 255, 255), -1)
        cv2.line(frame_desenho, (centro_carro, y_mira), (centro_final, y_mira), (255, 255, 255), 2)
    
    return frame_desenho, erro