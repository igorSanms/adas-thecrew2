# VisionADAS: Automação Veicular com Visão Computacional (Nível 2)

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)
![YOLOv8](https://img.shields.io/badge/YOLOv8-PyTorch-orange.svg)
![Status](https://img.shields.io/badge/Status-Estável-brightgreen.svg)

*Linkedln: https://lnkd.in/p/e_jk5x7P*

## 📌 Visão Geral
Este projeto é uma implementação de um sistema **ADAS (Advanced Driver Assistance System)** criado do zero em Python. Utilizando o ambiente complexo e dinâmico do jogo *The Crew 2* como simulador, o sistema captura a tela em tempo real, processa o ambiente via Visão Computacional tradicional e Redes Neurais (YOLOv8), e envia comandos físicos para o veículo através de um joystick virtual.

O sistema alcança o Nível 2 de autonomia, executando controle lateral (volante) e longitudinal (acelerador/freio) simultaneamente.

## 🚀 Funcionalidades (Features)
*   **LKAS (Lane Keeping Assist):** Mantém o veículo centralizado na faixa em retas e curvas.
*   **AEB (Frenagem de Emergência):** Detecta veículos à frente e aciona os freios para evitar colisões.
*   **ACC (Controle de Cruzeiro Adaptativo):** Modula dinamicamente a aceleração para acompanhar o ritmo do trânsito, mantendo distância segura.
*   **ALC (Auto Lane Change):** Máquina de estados que avalia "sensores laterais virtuais" e executa ultrapassagens autônomas se o veículo ficar preso em trânsito lento.

## 🧠 Arquitetura e Decisões de Engenharia

Para garantir processamento em tempo real (evitando latência entre a câmera e a ação mecânica), a arquitetura foi dividida de forma híbrida:

1. **Controle Lateral (Visão Computacional - CPU):**
   * Optei por **não usar Redes Neurais** para a detecção de faixas. Em vez disso, foi construído um pipeline clássico e otimizado com OpenCV: `Escala de Cinza -> CLAHE (Contraste de Iluminação) -> Gaussian Blur -> Canny Edge -> Dilatação Morfológica -> HoughLinesP`.
   * **Por que?** Esse pipeline é extremamente leve e processado exclusivamente na CPU, liberando a GPU inteiramente para a detecção de objetos, além de não exigir datasets massivos de treinamento para rodar.
2. **Controle Longitudinal (YOLOv8 - GPU):**
   * Inferência acelerada via CUDA para detecção espacial de veículos.
   * Resolução de entrada otimizada diretamente no tensor da IA (`imgsz=480px`) para maximizar o FPS sem perder precisão na detecção de objetos distantes, em vez de exigir cálculos de reescala via CPU.
3. **Controle Mecânico (PID + Lookahead):**
   * **Controlador PD (Proporcional-Derivativo):** Transforma o erro da pista em pixels em comandos analógicos suaves de direção, amortecendo a oscilação natural (zigue-zague).
   * **Lookahead (Pure Pursuit):** O cálculo do erro não é feito na base do carro, mas sim projetado à frente (linha do horizonte), permitindo que o sistema antecipe curvas em vez de reagir tardiamente.
4. **Máquina de Estados Finitos (FSM):**
   * Lógica central que impede conflitos de hardware. O veículo só pode estar em um estado lógico por vez: `MANUAL`, `CRUZEIRO`, `ACC (SEGUINDO)`, `EMERGENCIA` ou `CEGO`.

## 🚧 Desafios Superados

* **Latência de Captura e Teclado:** Jogos bloqueiam comandos de teclado via software (Anti-Cheat) e geram "Deadzone". Solucionamos emulando um controle de Xbox 360 virtual (`vgamepad`), permitindo movimentos analógicos e micro-correções precisas de esterçamento.
* **Ruído Visual (Sombras e Texturas):** Sombras de pontes e árvores destruíam a detecção do Canny. Implementamos o algoritmo CLAHE para normalizar a iluminação e Filtros Morfológicos (Dilatação) para "engordar" as faixas reais e ignorar ruídos do asfalto.
* **Lane Straddling (Cavalgar na Faixa):** O sistema tendia a se guiar pela linha central. Implementamos um *Sanity Check* (Filtro do Para-choque) e uma Memória Exponencial (EMA) para a largura da pista: se uma linha matemática nascer exatamente sob o centro do veículo, ela é descartada como anomalia.

## ⚠️ Limitações Conhecidas e Trabalhos Futuros

Como todo sistema baseado em Visão Computacional pura (sem dados de Lidar ou Radar físico), existem cenários extremos que afetam a confiabilidade, conhecidos como *Edge Cases*:

1. **Falsos Positivos por Distorção de Perspectiva:** O corredor de segurança de frenagem é baseado em um cálculo 2D retilíneo. Devido à distorção de perspectiva geométrica, quando o veículo enfrenta aclives (subidas), declives ou desníveis no asfalto, as caixas delimitadoras (Bounding Boxes) dos veículos vizinhos sofrem distorção no eixo X da tela, invadindo momentaneamente a nossa área de risco e causando leves desacelerações preventivas indesejadas.
2. **Condições Climáticas Severas (Chuva/Neve):** O algoritmo de Canny mapeia bordas de alto contraste. Marcas de pneu na neve/asfalto ou reflexos de água no asfalto são matematicamente idênticos a faixas pintadas, causando instabilidade na geração das retas direcionais.
3. **Sombras de Infraestrutura:** Dependendo do ângulo do sol, postes e guard-rails projetam linhas longas e contínuas no asfalto que ocasionalmente competem com as faixas de rolamento.