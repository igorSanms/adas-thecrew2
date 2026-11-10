import cv2

def analisar_risco_colisao(dados_veiculos, centro_pista, largura_faixa, frame_desenho):
    if centro_pista is None:
        return "SEM PISTA", 0, True, True, frame_desenho
        
    alerta_colisao = "LIVRE"
    maior_proximidade = 0 
    
    esquerda_livre = True
    direita_livre = True
    
    margem = largura_faixa / 5 
    limite_esq = centro_pista - margem
    limite_dir = centro_pista + margem

    for caixa in dados_veiculos:
        coords = caixa.xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
        
        centro_x_veiculo = (x1 + x2) / 2
        proximidade = y2
        
        posicao = "DESCONHECIDO"
        cor_caixa = (255, 255, 255) 
        
        if centro_x_veiculo < limite_esq:
            posicao = "ESQUERDA"
            cor_caixa = (255, 0, 0) 
            esquerda_livre = False
            
        elif centro_x_veiculo > limite_dir:
            posicao = "DIREITA"
            cor_caixa = (0, 255, 0)
            direita_livre = False
            
        else:
            if proximidade > maior_proximidade:
                maior_proximidade = proximidade 
                
            if proximidade > 550:
                posicao = "ALERTA COLISAO"
                alerta_colisao = "PERIGO A FRENTE"
                cor_caixa = (0, 0, 255) 
            elif proximidade > 350:
                posicao = "ACC: SEGUINDO"
                if alerta_colisao != "PERIGO A FRENTE": 
                    alerta_colisao = "SEGUINDO"
                cor_caixa = (0, 165, 255) 
            else:
                posicao = "FRENTE (LONGE)"
                cor_caixa = (0, 255, 255) 

        cv2.putText(frame_desenho, posicao, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, cor_caixa, 2)
        cv2.circle(frame_desenho, (int(centro_x_veiculo), proximidade), 5, cor_caixa, -1)
        
    return alerta_colisao, maior_proximidade, esquerda_livre, direita_livre, frame_desenho