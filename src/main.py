import cv2
import time
from captura.tela import Capturador
from percepcao.roi import aplicar_roi
from percepcao.pista import detectar_faixas_bordas
from percepcao.linhas import detectar_linhas_e_centro, memoria 
from percepcao.veiculos import DetectorVeiculos
from percepcao.risco import analisar_risco_colisao
from controle.veiculo import ControladorVirtual

def desenhar_hud(frame_display, fps, estado_sistema, estado_player, erro_pista, alerta):
    fonte = cv2.FONT_HERSHEY_SIMPLEX
    cv2.rectangle(frame_display, (10, 10), (450, 200), (0, 0, 0), -1)
    
    if estado_sistema == "CRUZEIRO": cor_sistema = (0, 255, 0) 
    elif estado_sistema == "EMERGENCIA": cor_sistema = (0, 0, 255) 
    elif estado_sistema == "CEGO": cor_sistema = (0, 165, 255) 
    else: cor_sistema = (255, 255, 255) 
    
    cor_alerta = (0, 0, 255) if alerta == "PERIGO A FRENTE" else (0, 255, 0)
    erro_texto = f"{erro_pista} px" if erro_pista is not None else "PERDIDO"
    
    textos = [
        (f"FPS: {int(fps)}", (255, 255, 255)),
        (f"Modo: {estado_sistema}", cor_sistema),
        (f"Player: {estado_player}", (255, 255, 255)),
        (f"Erro Centro: {erro_texto}", (255, 255, 255)),
        (f"Radar YOLO: {alerta}", cor_alerta),
        (f"[P] Ligar/Desligar Autonomo", (200, 200, 200))
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
    estado_player = "ATIVO"

    print("Iniciando monitoramento... Clique na janela e aperte 'q' para sair, ou 'p' para Autonomo.")

    while True:
        frame_original = capturador.capturar()

        bordas = detectar_faixas_bordas(frame_original)
        mascara = aplicar_roi(bordas)
        frame_linhas, erro_pista = detectar_linhas_e_centro(mascara, frame_original)
        
        frame_ia, dados_veiculos = detector_veiculos.detectar(frame_linhas)
        alerta, frame_final = analisar_risco_colisao(
            dados_veiculos, memoria["centro_suavizado"], memoria["largura_faixa"], frame_ia)
        
        estado_sistema = "MANUAL"
        
        if piloto_automatico:
            if alerta == "PERIGO A FRENTE":
                estado_sistema = "EMERGENCIA"
            elif erro_pista is None:
                estado_sistema = "CEGO"
            else:
                estado_sistema = "CRUZEIRO"
        
        if estado_sistema == "CRUZEIRO":
            controlador.atualizar_controles(erro_pista, "LIVRE")
            
        elif estado_sistema == "EMERGENCIA":
            controlador.atualizar_controles(erro_pista if erro_pista else 0, "PERIGO A FRENTE")
            
        elif estado_sistema == "CEGO":
            controlador.soltar_tudo()
            
        elif estado_sistema == "MANUAL":
            controlador.soltar_tudo()
        
        frame_display = cv2.resize(frame_final, (1280, 720))
        tempo_atual = time.time()
        fps = 1 / (tempo_atual - ultimo_tempo) if (tempo_atual - ultimo_tempo) > 0 else 0
        ultimo_tempo = tempo_atual

        desenhar_hud(frame_display, fps, estado_sistema, estado_player, erro_pista, alerta)
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