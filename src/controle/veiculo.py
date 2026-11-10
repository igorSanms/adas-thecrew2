import vgamepad as vg

class ControladorVirtual:
    def __init__(self):
        self.gamepad = vg.VX360Gamepad()
        self.Kp = 85 
        self.Kd = 300 
        self.erro_anterior = 0


    def forcar_mudanca_faixa(self, direcao):
        comando_direcao = -10000 if direcao == "ESQUERDA" else 10000
        
        self.gamepad.left_joystick(x_value=comando_direcao, y_value=0)

        self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
        self.gamepad.right_trigger(value=130)
        
        self.gamepad.update()

        self.erro_anterior = 0

    def atualizar_controles(self, erro_pista, risco, proximidade_alvo):
        comando_direcao = 0
        
        if erro_pista is not None:
            taxa_variacao = erro_pista - self.erro_anterior
            self.erro_anterior = erro_pista
            comando_direcao = int((erro_pista * self.Kp) + (taxa_variacao * self.Kd))
            comando_direcao = max(-32768, min(32767, comando_direcao))
        
        self.gamepad.left_joystick(x_value=comando_direcao, y_value=0)

        acelerador_base = 160 # Controlar velocidade

        if risco == "PERIGO A FRENTE":
            self.gamepad.right_trigger(value=0)
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
            
        elif risco == "SEGUINDO":
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
            
            distancia_acc = proximidade_alvo - 350
            fator_aceleracao = 1.0 - (distancia_acc / 200.0) 
            
            fator_aceleracao = max(0.0, min(1.0, fator_aceleracao))
            
            aceleracao_atual = int(acelerador_base * fator_aceleracao)
            self.gamepad.right_trigger(value=aceleracao_atual)
            
        else: 
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
            self.gamepad.right_trigger(value=acelerador_base)

        self.gamepad.update()

    def soltar_tudo(self):
        self.gamepad.reset()
        self.gamepad.update()
        self.erro_anterior = 0