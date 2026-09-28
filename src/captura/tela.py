import mss
import numpy as np
import cv2

class Capturador:
    def __init__(self, top=0, left=0, width=1280, height=720):

        self.sct = mss.mss()

        self.monitor = {"top": top, "left": left, "width": width, "height": height}

    def capturar(self):

        img = self.sct.grab(self.monitor)
        
        img_np = np.array(img)
    
        frame = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
        
        return frame