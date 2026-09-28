import cv2
import time
from captura.tela import Capturador
from percepcao.roi import aplicar_roi
from percepcao.pista import detectar_faixas_bordas 

def desenhar_hud(frame_display, fps, estado_sistema, estado_player):
    fonte = cv2.FONT_HERSHEY_SIMPLEX
    cv2.rectangle(frame_display, (10, 10), (350, 130), (0, 0, 0), -1)
    textos = [
        f"FPS: {int(fps)}",
        f"Sistema: {estado_sistema}",
        f"Player: {estado_player}",
        f"Alvo/Acao: AGUARDANDO..."
    ]
    y = 35
    for texto in textos:
        cv2.putText(frame_display, texto, (20, y), fonte, 0.6, (255, 255, 255), 2)
        y += 25

def main():
    capturador = Capturador(top=0, left=0, width=1920, height=1080)
    ultimo_tempo = time.time()
    estado_sistema = "MANUAL"
    estado_player = "ATIVO"

    print("Iniciando monitoramento... Pressione 'q' na janela de vídeo para sair.")

    while True:
        frame_original = capturador.capturar()

        frame_roi = aplicar_roi(frame_original)
        
        mascara_pista = detectar_faixas_bordas(frame_roi)

        frame_processado = cv2.cvtColor(mascara_pista, cv2.COLOR_GRAY2BGR)
        
        frame_display = cv2.resize(frame_processado, (1280, 720))

        tempo_atual = time.time()
        fps = 1 / (tempo_atual - ultimo_tempo) if (tempo_atual - ultimo_tempo) > 0 else 0
        ultimo_tempo = tempo_atual

        desenhar_hud(frame_display, fps, estado_sistema, estado_player)

        cv2.imshow("Monitor ADAS - Visao Computacional", frame_display)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()