import cv2
import time
from captura.tela import Capturador
from percepcao.roi import aplicar_roi
from percepcao.pista import detectar_faixas_bordas
from percepcao.linhas import detectar_linhas_e_centro, memoria 
from percepcao.veiculos import DetectorVeiculos
from percepcao.risco import analisar_risco_colisao
from controle.veiculo import ControladorVirtual

def desenhar_hud(frame_display, fps, estado_sistema, alerta, esq_livre, dir_livre):
    fonte = cv2.FONT_HERSHEY_SIMPLEX
    cv2.rectangle(frame_display, (10, 10), (450, 210), (0, 0, 0), -1)
    
    if estado_sistema == "CRUZEIRO": cor_sistema = (0, 255, 0)
    elif "TROCANDO" in estado_sistema: cor_sistema = (255, 0, 255)
    elif estado_sistema == "EMERGENCIA": cor_sistema = (0, 0, 255)
    elif estado_sistema == "ACC (SEGUINDO)": cor_sistema = (0, 165, 255)
    else: cor_sistema = (255, 255, 255)
    
    sensores = f"Esq: {'LIVRE' if esq_livre else 'OCUPADA'} | Dir: {'LIVRE' if dir_livre else 'OCUPADA'}"
    
    textos = [
        (f"FPS: {int(fps)}", (255, 255, 255)),
        (f"Modo: {estado_sistema}", cor_sistema),
        (f"Sensores: {sensores}", (200, 200, 200)),
        (f"Radar YOLO: {alerta}", (0, 255, 0) if alerta == "LIVRE" else (0, 0, 255)),
        (f"[P] Ligar/Desligar Autonomo", (150, 150, 150))
    ]
    
    y = 35
    for texto, cor in textos:
        cv2.putText(frame_display, texto, (20, y), fonte, 0.6, cor, 2)
        y += 25

def main():
    capturador = Capturador(top=0, left=0, width=1920, height=1080)
    
    print("Carregando Rede Neural YOLOv8...")
    detector_veiculos = DetectorVeiculos()
    print("Iniciando Controle Virtual...")
    controlador = ControladorVirtual()
    print("IA e Controle carregados com sucesso!")
    
    ultimo_tempo = time.time()
    
    piloto_automatico = False 
    estado_sistema = "MANUAL"
    
    tempo_inicio_seguindo = 0
    tempo_inicio_troca = 0
    duracao_troca_faixa = 1.5

    print("Iniciando monitoramento... [P] Autonomo | [Q] Sair")

    while True:
        frame_original = capturador.capturar()

        bordas = detectar_faixas_bordas(frame_original)
        mascara = aplicar_roi(bordas)
        frame_linhas, erro_pista = detectar_linhas_e_centro(mascara, frame_original)
        
        frame_ia, dados_veiculos = detector_veiculos.detectar(frame_linhas)
        
        alerta, proximidade_alvo, esq_livre, dir_livre, frame_final = analisar_risco_colisao(
            dados_veiculos, memoria["centro_suavizado"], memoria["largura_faixa"], frame_ia)
        
        if piloto_automatico:
            if "TROCANDO_FAIXA" in estado_sistema:
                if (time.time() - tempo_inicio_troca) > duracao_troca_faixa:
                    estado_sistema = "CRUZEIRO"
            else:
                if alerta in ["PERIGO A FRENTE", "SEGUINDO"]:
                    if tempo_inicio_seguindo == 0:
                        tempo_inicio_seguindo = time.time()
                    
                    tempo_preso = time.time() - tempo_inicio_seguindo
                    
                    if tempo_preso > 2.0:
                        if esq_livre:
                            estado_sistema = "TROCANDO_FAIXA_ESQ"
                            tempo_inicio_troca = time.time()
                            tempo_inicio_seguindo = 0 
                        elif dir_livre:
                            estado_sistema = "TROCANDO_FAIXA_DIR"
                            tempo_inicio_troca = time.time()
                            tempo_inicio_seguindo = 0 
                        else:
                            estado_sistema = "EMERGENCIA" if alerta == "PERIGO A FRENTE" else "ACC (SEGUINDO)"
                    else:
                        estado_sistema = "EMERGENCIA" if alerta == "PERIGO A FRENTE" else "ACC (SEGUINDO)"
                
                elif erro_pista is None:
                    estado_sistema = "CEGO"
                    tempo_inicio_seguindo = 0
                else:
                    estado_sistema = "CRUZEIRO"
                    tempo_inicio_seguindo = 0
        else:
            estado_sistema = "MANUAL"
            tempo_inicio_seguindo = 0
        
        if estado_sistema == "CRUZEIRO":
            controlador.atualizar_controles(erro_pista, alerta, proximidade_alvo)
            
        elif estado_sistema == "ACC (SEGUINDO)":
            controlador.atualizar_controles(erro_pista, alerta, proximidade_alvo)
            
        elif estado_sistema == "EMERGENCIA":
            controlador.atualizar_controles(erro_pista if erro_pista else 0, alerta, proximidade_alvo)
            
        elif estado_sistema == "TROCANDO_FAIXA_ESQ":
            controlador.forcar_mudanca_faixa("ESQUERDA")
            
        elif estado_sistema == "TROCANDO_FAIXA_DIR":
            controlador.forcar_mudanca_faixa("DIREITA")
            
        elif estado_sistema in ["CEGO", "MANUAL"]:
            controlador.soltar_tudo()
        
        frame_display = cv2.resize(frame_final, (1280, 720))
        tempo_atual = time.time()
        fps = 1 / (tempo_atual - ultimo_tempo) if (tempo_atual - ultimo_tempo) > 0 else 0
        ultimo_tempo = tempo_atual

        desenhar_hud(frame_display, fps, estado_sistema, alerta, esq_livre, dir_livre)
        cv2.imshow("Monitor ADAS", frame_display)

        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord('q'):
            break
        elif tecla == ord('p'):
            piloto_automatico = not piloto_automatico

    controlador.soltar_tudo()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()