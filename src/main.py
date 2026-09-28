import cv2
import time
from captura.tela import Capturador

def main():
    capturador = Capturador(top=0, left=0, width=1280, height=720)
    
    ultimo_tempo = time.time()

    print("Pressione 'q' na janela de vídeo para sair")

    while True:
        frame = capturador.capturar()

        tempo_atual = time.time()
        fps = 1 / (tempo_atual - ultimo_tempo)
        ultimo_tempo = tempo_atual

        cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Visao do Sistema - The Crew 2", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()