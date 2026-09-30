from ultralytics import YOLO
import torch

class DetectorVeiculos:
    def __init__(self):
        self.modelo = YOLO("yolov8n.pt")
        self.classes_alvo = [2, 3, 5, 7]
        
        if torch.cuda.is_available():
            nome_gpu = torch.cuda.get_device_name(0)
            print(f"-> [SUCESSO] IA rodando na GPU: {nome_gpu}")
            torch.backends.cudnn.benchmark = True
        else:
            print("-> [ALERTA] IA rodando na CPU! O FPS ficara baixo.")

    def detectar(self, frame_desenho):
        resultados = self.modelo(
            frame_desenho, 
            classes=self.classes_alvo, 
            conf=0.50, 
            imgsz=480, 
            verbose=False
        )

        frame_com_caixas = resultados[0].plot()
        
        dados_veiculos = resultados[0].boxes
        
        return frame_com_caixas, dados_veiculos