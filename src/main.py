import cv2
import time
from captura.tela import Capturador
from percepcao.roi import aplicar_roi
from percepcao.pista import detectar_faixas_bordas
from percepcao.linhas import detectar_linhas_e_centro, memoria 
from percepcao.veiculos import DetectorVeiculos
from percepcao.risco import analisar_risco_colisao 

def desenhar_hud(frame_display, fps, estado_sistema, estado_player, erro_pista, alerta):
    fonte = cv2.FONT_HERSHEY_SIMPLEX
    cv2.rectangle(frame_display, (10, 10), (450, 180), (0, 0, 0), -1)
    
    cor_alerta = (0, 0, 255) if alerta == "PERIGO A FRENTE" else (0, 255, 0)
    
    textos = [
        (f"FPS: {int(fps)}", (255, 255, 255)),
        (f"Sistema: {estado_sistema}", (255, 255, 255)),
        (f"Player: {estado_player}", (255, 255, 255)),
        (f"Erro Centro: {erro_pista} px", (255, 255, 255)),
        (f"Risco: {alerta}", cor_alerta),
        (f"Alvo/Acao: AGUARDANDO...", (255, 255, 255))
    ]
    y = 35
    for texto, cor in textos:
        cv2.putText(frame_display, texto, (20, y), fonte, 0.6, cor, 2)
        y += 25

def main():
    capturador = Capturador(top=0, left=0, width=1920, height=1080)
    
    print("Carregando Rede Neural YOLOv8...")
    detector_veiculos = DetectorVeiculos()
    print("IA Carregada com sucesso!")
    
    ultimo_tempo = time.time()
    estado_sistema = "MANUAL"
    estado_player = "ATIVO"

    print("Iniciando monitoramento... Clique na janela de video e aperte 'q' para sair.")

    while True:
        frame_original = capturador.capturar()

        bordas_tela_toda = detectar_faixas_bordas(frame_original)
        mascara_bordas = aplicar_roi(bordas_tela_toda)
        frame_com_linhas, erro_pista = detectar_linhas_e_centro(mascara_bordas, frame_original)
        
        frame_com_ia, dados_veiculos = detector_veiculos.detectar(frame_com_linhas)
        
        alerta, frame_final = analisar_risco_colisao(
            dados_veiculos, 
            memoria["centro_suavizado"], 
            memoria["largura_faixa"], 
            frame_com_ia
        )
        
        frame_display = cv2.resize(frame_final, (1280, 720))
        
        tempo_atual = time.time()
        fps = 1 / (tempo_atual - ultimo_tempo) if (tempo_atual - ultimo_tempo) > 0 else 0
        ultimo_tempo = tempo_atual

        desenhar_hud(frame_display, fps, estado_sistema, estado_player, erro_pista, alerta)

        cv2.imshow("Monitor ADAS - Visao Computacional", frame_display)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()