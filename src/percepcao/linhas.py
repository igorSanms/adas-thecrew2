import cv2
import numpy as np

# Variável de memória para guardar informações entre um frame e o próximo
memoria = {
    "largura_faixa": 800,       # Um chute inicial que será corrigido no primeiro frame bom
    "centro_suavizado": None    # Onde guardamos a posição filtrada com EMA
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
    global memoria # Permite acessar e modificar a memória global
    
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
    
    # 1. Lógica de Memória da Largura da Faixa
    if linha_esq is not None and linha_dir is not None:
        cv2.line(frame_desenho, (linha_esq[0], linha_esq[1]), (linha_esq[2], linha_esq[3]), (255, 0, 0), 5)
        cv2.line(frame_desenho, (linha_dir[0], linha_dir[1]), (linha_dir[2], linha_dir[3]), (0, 255, 0), 5)
        
        # Atualiza a memória com a distância real entre as duas linhas na base da tela
        memoria["largura_faixa"] = linha_dir[0] - linha_esq[0]
        centro_instantaneo = int((linha_esq[0] + linha_dir[0]) / 2)
        
    elif linha_esq is not None:
        cv2.line(frame_desenho, (linha_esq[0], linha_esq[1]), (linha_esq[2], linha_esq[3]), (255, 0, 0), 5)
        # Usa a metade da última largura conhecida
        centro_instantaneo = int(linha_esq[0] + (memoria["largura_faixa"] / 2))
        
    elif linha_dir is not None:
        cv2.line(frame_desenho, (linha_dir[0], linha_dir[1]), (linha_dir[2], linha_dir[3]), (0, 255, 0), 5)
        # Usa a metade da última largura conhecida
        centro_instantaneo = int(linha_dir[0] - (memoria["largura_faixa"] / 2))

    # 2. Filtro de Média Móvel Exponencial (EMA)
    if centro_instantaneo is not None:
        if memoria["centro_suavizado"] is None:
            # Se for o primeiro frame, assume o valor direto
            memoria["centro_suavizado"] = centro_instantaneo
        else:
            # Mistura: 20% do novo valor (rápido o suficiente) + 80% do valor antigo (memória inercial)
            # Se quiser que o ponto fique ainda mais "pesado" e lento, diminua o alpha para 0.1
            alpha = 0.2 
            memoria["centro_suavizado"] = int((1 - alpha) * memoria["centro_suavizado"] + alpha * centro_instantaneo)

    # 3. Cálculo de Erro com o Centro Filtrado
    centro_final = memoria["centro_suavizado"]
    centro_carro = largura // 2
    erro = 0 
    
    if centro_final is not None:
        erro = centro_carro - centro_final
        # Desenha os indicadores com o centro final estabilizado
        cv2.circle(frame_desenho, (centro_final, altura - 50), 10, (0, 0, 255), -1)
        cv2.circle(frame_desenho, (centro_carro, altura - 50), 10, (0, 255, 255), -1)
        cv2.line(frame_desenho, (centro_carro, altura - 50), (centro_final, altura - 50), (255, 255, 255), 2)
    
    return frame_desenho, erro