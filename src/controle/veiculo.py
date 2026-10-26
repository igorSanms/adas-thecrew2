import vgamepad as vg

class ControladorVirtual:
    def __init__(self):
        self.gamepad = vg.VX360Gamepad()
        self.Kp = 85 
        self.Kd = 300 
        
        self.erro_anterior = 0

    def atualizar_controles(self, erro_pista, risco):
        comando_direcao = 0
        
        if erro_pista is not None:
            taxa_variacao = erro_pista - self.erro_anterior
            self.erro_anterior = erro_pista
            comando_direcao = int((erro_pista * self.Kp) + (taxa_variacao * self.Kd))
            comando_direcao = max(-32768, min(32767, comando_direcao))
        
        self.gamepad.left_joystick(x_value=comando_direcao, y_value=0)

        if risco == "PERIGO A FRENTE":
            self.gamepad.right_trigger(value=0)
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
        else:
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
            self.gamepad.right_trigger(value=100)

        self.gamepad.update()

    def soltar_tudo(self):
        self.gamepad.reset()
        self.gamepad.update()
        self.erro_anterior = 0