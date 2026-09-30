import cv2

def analisar_risco_colisao(dados_veiculos, centro_pista, largura_faixa, frame_desenho):

    if centro_pista is None:
        return "SEM PISTA", frame_desenho
        
    alerta_colisao = "LIVRE"
    
    margem = largura_faixa / 2
    limite_esq = centro_pista - margem
    limite_dir = centro_pista + margem

    for caixa in dados_veiculos:
        coords = caixa.xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
        
        centro_x_veiculo = (x1 + x2) / 2        
   
        proximidade = y2
        
        posicao = "DESCONHECIDO"
        cor_caixa = (255, 255, 255) # Branco padrão
        
        if centro_x_veiculo < limite_esq:
            posicao = "ESQUERDA"
            cor_caixa = (255, 0, 0) # Azul para carros na esquerda
            
        elif centro_x_veiculo > limite_dir:
            posicao = "DIREITA"
            cor_caixa = (0, 255, 0) # Verde para carros na direita
            
        else:
            posicao = "FRENTE"
            if proximidade > 550:
                posicao = "ALERTA COLISAO"
                alerta_colisao = "PERIGO A FRENTE"
                cor_caixa = (0, 0, 255) 
            else:
                posicao = "FRENTE (LONGE)"
                cor_caixa = (0, 255, 255) 
        cv2.putText(frame_desenho, posicao, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, cor_caixa, 2)
        cv2.circle(frame_desenho, (int(centro_x_veiculo), proximidade), 5, cor_caixa, -1)
        
    return alerta_colisao, frame_desenho