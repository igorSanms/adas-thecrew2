import cv2
import time
from captura.tela import Capturador
from percepcao.roi import aplicar_roi
from percepcao.pista import detectar_faixas_bordas
from percepcao.linhas import detectar_linhas_e_centro # Importamos a nova função

def desenhar_hud(frame_display, fps, estado_sistema, estado_player, erro_pista):
    fonte = cv2.FONT_HERSHEY_SIMPLEX
    cv2.rectangle(frame_display, (10, 10), (350, 155), (0, 0, 0), -1)
    textos = [
        f"FPS: {int(fps)}",
        f"Sistema: {estado_sistema}",
        f"Player: {estado_player}",
        f"Erro Centro: {erro_pista} px", # Nova linha exibindo o desvio numérico
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

        # 1. Extrai as bordas da tela INTEIRA primeiro (Canny + CLAHE)
        bordas_tela_toda = detectar_faixas_bordas(frame_original)
        
        # 2. Aplica a ROI em cima das bordas (agora o recorte não criará bordas falsas)
        mascara_bordas = aplicar_roi(bordas_tela_toda)
        
        # 3. Transformada de Hough (Calcula as linhas e o centro)
        # Usamos frame_original aqui para desenhar as linhas coloridas sobre o asfalto real
        frame_com_linhas, erro_pista = detectar_linhas_e_centro(mascara_bordas, frame_original)
        
        # 4. Prepara para exibição
        frame_display = cv2.resize(frame_com_linhas, (1280, 720))

        # 5. Calcula FPS
        tempo_atual = time.time()
        fps = 1 / (tempo_atual - ultimo_tempo) if (tempo_atual - ultimo_tempo) > 0 else 0
        ultimo_tempo = tempo_atual

        # 6. Desenha o HUD (agora passamos o erro_pista também)
        desenhar_hud(frame_display, fps, estado_sistema, estado_player, erro_pista)

        # 7. Exibe a janela
        cv2.imshow("Monitor ADAS - Visao Computacional", frame_display)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()