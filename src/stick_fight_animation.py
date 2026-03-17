"""
Animação Estilo Stick Fight - Computação Gráfica 2D
Demonstra transformações geométricas: translação, rotação, escala e composição.
Autor: Aluno de Engenharia de Computação
"""

import pygame
import math
import sys

# ======================== CONFIGURAÇÕES ========================
LARGURA, ALTURA = 900, 600
FPS = 60
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (220, 50, 50)
AZUL = (50, 80, 220)
CINZA_CLARO = (200, 200, 200)
VERDE = (80, 180, 80)
AMARELO = (255, 220, 50)
CHAO_COR = (100, 80, 60)

# ======================== FUNÇÕES DE TRANSFORMAÇÃO 2D ========================

def translacao(ponto, tx, ty):
    """Aplica translação T(tx, ty) ao ponto (x, y).
    Matriz: |1  0  tx| |x|   |x + tx|
            |0  1  ty| |y| = |y + ty|
            |0  0   1| |1|   |  1   |
    """
    return (ponto[0] + tx, ponto[1] + ty)


def rotacao(ponto, angulo_rad, centro=(0, 0)):
    """Aplica rotação R(θ) ao ponto em torno de um centro.
    Matriz: |cos θ  -sin θ  0|
            |sin θ   cos θ  0|
            |  0       0    1|
    Composta com translação para rotacionar em torno de ponto arbitrário.
    """
    cx, cy = centro
    # Translada para origem
    px, py = ponto[0] - cx, ponto[1] - cy
    # Aplica rotação
    cos_a = math.cos(angulo_rad)
    sin_a = math.sin(angulo_rad)
    rx = px * cos_a - py * sin_a
    ry = px * sin_a + py * cos_a
    # Translada de volta
    return (rx + cx, ry + cy)


def escala(ponto, sx, sy, centro=(0, 0)):
    """Aplica escala S(sx, sy) ao ponto em torno de um centro.
    Matriz: |sx  0  0|
            |0  sy  0|
            |0   0  1|
    """
    cx, cy = centro
    px, py = ponto[0] - cx, ponto[1] - cy
    return (px * sx + cx, py * sy + cy)


# ======================== FUNÇÕES DE EASING ========================

def ease_in_out_cubic(t):
    """Suavização cúbica com derivada zero nos extremos.
    Elimina descontinuidade de velocidade entre fases de animação.
    Fórmula: 4t³ se t<0.5, senão 1 - (-2t+2)³/2
    """
    if t < 0.5:
        return 4.0 * t * t * t
    else:
        p = -2.0 * t + 2.0
        return 1.0 - p * p * p / 2.0


def ease_out_cubic(t):
    """Saída rápida com desaceleração progressiva.
    Ideal para fase de golpe (início explosivo, fim suave).
    Fórmula: 1 - (1-t)³
    """
    p = 1.0 - t
    return 1.0 - p * p * p


def ease_out_back(t):
    """Overshoot com retorno elástico (follow-through).
    Simula inércia: ultrapassa o destino e volta.
    Fórmula: 1 + (s+1)(t-1)³ + s(t-1)² onde s=1.70158
    """
    s = 1.70158
    p = t - 1.0
    return 1.0 + (s + 1.0) * p * p * p + s * p * p


# ======================== CLASSE STICK FIGURE ========================

class StickFigure:
    """Representa uma figura de palito (stick figure) com articulações.
    Cada membro é definido por segmentos de reta relativos a articulações,
    permitindo aplicar rotação independente em cada junta (cinemática direta).
    """

    def __init__(self, x, y, cor, nome="Lutador", direcao=1):
        self.x = x  # Posição base (quadril)
        self.y = y
        self.cor = cor
        self.nome = nome
        self.direcao = direcao  # 1 = direita, -1 = esquerda

        # Comprimentos dos membros
        self.torso_len = 50
        self.cabeca_raio = 15
        self.braco_sup_len = 30
        self.braco_inf_len = 25
        self.perna_sup_len = 35
        self.perna_inf_len = 30

        # Ângulos das articulações (em radianos)
        self.angulo_torso = 0
        self.angulo_braco_dir = math.radians(-30) * direcao
        self.angulo_antebraco_dir = math.radians(-20) * direcao
        self.angulo_braco_esq = math.radians(30) * direcao
        self.angulo_antebraco_esq = math.radians(20) * direcao
        self.angulo_perna_dir = math.radians(10) * direcao
        self.angulo_canela_dir = math.radians(5)
        self.angulo_perna_esq = math.radians(-10) * direcao
        self.angulo_canela_esq = math.radians(-5)

        # Estado de animação
        self.vida = 100
        self.escala_x = 1.0
        self.escala_y = 1.0
        self.atacando = False
        self.frame_ataque = 0
        self.tipo_ataque = 'soco'
        self.pulando = False
        self.vel_y = 0
        self.chao_y = y

        # Spring damping: velocidade horizontal para movimento suave
        self._vel_x = 0.0

    def _calcular_ponto_final(self, inicio, comprimento, angulo):
        """Calcula ponto final de um segmento dado início, comprimento e ângulo."""
        fx = inicio[0] + comprimento * math.sin(angulo)
        fy = inicio[1] + comprimento * math.cos(angulo)
        return (fx, fy)

    def _obter_articulacoes(self):
        """Calcula todas as posições das articulações usando cinemática direta.
        Cada articulação depende da anterior (encadeamento de transformações).
        """
        quadril = (self.x, self.y)

        # Torso: do quadril até os ombros
        ombros = self._calcular_ponto_final(quadril, -self.torso_len, self.angulo_torso)

        # Cabeça: acima dos ombros
        cabeca_centro = (ombros[0], ombros[1] - self.cabeca_raio - 3)

        # Braço direito
        cotovelo_dir = self._calcular_ponto_final(
            ombros, self.braco_sup_len,
            self.angulo_torso + self.angulo_braco_dir
        )
        mao_dir = self._calcular_ponto_final(
            cotovelo_dir, self.braco_inf_len,
            self.angulo_torso + self.angulo_braco_dir + self.angulo_antebraco_dir
        )

        # Braço esquerdo
        cotovelo_esq = self._calcular_ponto_final(
            ombros, self.braco_sup_len,
            self.angulo_torso + self.angulo_braco_esq
        )
        mao_esq = self._calcular_ponto_final(
            cotovelo_esq, self.braco_inf_len,
            self.angulo_torso + self.angulo_braco_esq + self.angulo_antebraco_esq
        )

        # Perna direita
        joelho_dir = self._calcular_ponto_final(
            quadril, self.perna_sup_len, self.angulo_perna_dir
        )
        pe_dir = self._calcular_ponto_final(
            joelho_dir, self.perna_inf_len,
            self.angulo_perna_dir + self.angulo_canela_dir
        )

        # Perna esquerda
        joelho_esq = self._calcular_ponto_final(
            quadril, self.perna_sup_len, self.angulo_perna_esq
        )
        pe_esq = self._calcular_ponto_final(
            joelho_esq, self.perna_inf_len,
            self.angulo_perna_esq + self.angulo_canela_esq
        )

        return {
            'quadril': quadril,
            'ombros': ombros,
            'cabeca': cabeca_centro,
            'cotovelo_dir': cotovelo_dir,
            'mao_dir': mao_dir,
            'cotovelo_esq': cotovelo_esq,
            'mao_esq': mao_esq,
            'joelho_dir': joelho_dir,
            'pe_dir': pe_dir,
            'joelho_esq': joelho_esq,
            'pe_esq': pe_esq,
        }

    def desenhar(self, tela):
        """Renderiza a stick figure na tela usando as articulações calculadas."""
        pts = self._obter_articulacoes()
        espessura = 3

        # Aplicar escala visual (efeito de impacto)
        if self.escala_x != 1.0 or self.escala_y != 1.0:
            centro = pts['quadril']
            for chave in pts:
                if chave != 'quadril':
                    pts[chave] = escala(pts[chave], self.escala_x, self.escala_y, centro)

        cor = self.cor

        # Desenha torso
        pygame.draw.line(tela, cor, pts['quadril'], pts['ombros'], espessura)

        # Desenha cabeça
        pygame.draw.circle(tela, cor, (int(pts['cabeca'][0]), int(pts['cabeca'][1])),
                          int(self.cabeca_raio * self.escala_x), 2)

        # Desenha braços
        pygame.draw.line(tela, cor, pts['ombros'], pts['cotovelo_dir'], espessura)
        pygame.draw.line(tela, cor, pts['cotovelo_dir'], pts['mao_dir'], espessura)
        pygame.draw.line(tela, cor, pts['ombros'], pts['cotovelo_esq'], espessura)
        pygame.draw.line(tela, cor, pts['cotovelo_esq'], pts['mao_esq'], espessura)

        # Desenha pernas
        pygame.draw.line(tela, cor, pts['quadril'], pts['joelho_dir'], espessura)
        pygame.draw.line(tela, cor, pts['joelho_dir'], pts['pe_dir'], espessura)
        pygame.draw.line(tela, cor, pts['quadril'], pts['joelho_esq'], espessura)
        pygame.draw.line(tela, cor, pts['joelho_esq'], pts['pe_esq'], espessura)

        # Barra de vida
        barra_x = int(pts['cabeca'][0]) - 20
        barra_y = int(pts['cabeca'][1]) - 30
        pygame.draw.rect(tela, VERMELHO, (barra_x, barra_y, 40, 5))
        pygame.draw.rect(tela, VERDE, (barra_x, barra_y, int(40 * self.vida / 100), 5))

    def animar_idle(self, tempo):
        """Animação de repouso: balanço dos braços + respiração sutil."""
        oscilacao = math.sin(tempo * 3) * 0.1
        self.angulo_braco_dir = (math.radians(-30) + oscilacao) * self.direcao
        self.angulo_braco_esq = (math.radians(30) - oscilacao) * self.direcao
        self.angulo_perna_dir = math.radians(10) * self.direcao + oscilacao * 0.3
        self.angulo_perna_esq = math.radians(-10) * self.direcao - oscilacao * 0.3

        # Respiração: oscilação vertical sutil (1.5px) e micro-rotação do torso
        respiracao = math.sin(tempo * 2.5) * 1.5
        if not self.pulando:
            self.y = self.chao_y + respiracao
        self.angulo_torso = math.sin(tempo * 2.5) * 0.02

    def animar_soco(self, progresso):
        """Animação de soco com easing e movimento secundário (torso + braço oposto).
        progresso: 0.0 a 1.0 (início ao fim do soco)
        """
        if progresso < 0.4:
            # Preparação (wind-up): braço vai para trás
            t = ease_in_out_cubic(progresso / 0.4)
            self.angulo_braco_dir = math.radians(-30 - 60 * t) * self.direcao
            self.angulo_antebraco_dir = math.radians(-20 - 30 * t) * self.direcao
            # Movimento secundário: torso inclina para trás na preparação
            self.angulo_torso = -0.15 * t * self.direcao
            # Braço oposto como contrapeso (vai para trás)
            self.angulo_braco_esq = (math.radians(30) + 0.3 * t) * self.direcao
        elif progresso < 0.7:
            # Golpe: braço vai rápido para frente com desaceleração
            t = ease_out_cubic((progresso - 0.4) / 0.3)
            self.angulo_braco_dir = math.radians(-90 + 140 * t) * self.direcao
            self.angulo_antebraco_dir = math.radians(-50 + 60 * t) * self.direcao
            # Torso inclina para frente no golpe
            self.angulo_torso = (-0.15 + 0.30 * t) * self.direcao
            # Braço oposto balança para frente como contrapeso
            self.angulo_braco_esq = (math.radians(30) + 0.3 - 0.6 * t) * self.direcao
        else:
            # Retorno com overshoot (follow-through)
            t = ease_out_back((progresso - 0.7) / 0.3)
            self.angulo_braco_dir = math.radians(50 - 80 * t) * self.direcao
            self.angulo_antebraco_dir = math.radians(10 - 30 * t) * self.direcao
            # Torso retorna à posição neutra
            self.angulo_torso = 0.15 * (1.0 - t) * self.direcao
            # Braço oposto retorna
            self.angulo_braco_esq = (math.radians(30) - 0.3 + 0.3 * t) * self.direcao

    def animar_chute(self, progresso):
        """Animação de chute com easing e inclinação do torso como contrapeso.
        Para direcao=1 usa perna_dir, para direcao=-1 usa perna_esq."""
        if progresso < 0.3:
            t = ease_in_out_cubic(progresso / 0.3)
            ang_perna = math.radians(-(10 - 70 * t)) * self.direcao
            ang_canela = math.radians(-(5 + 40 * t)) * self.direcao
            # Torso inclina para trás como contrapeso da perna
            self.angulo_torso = -0.20 * t * self.direcao
        elif progresso < 0.6:
            t = ease_out_cubic((progresso - 0.3) / 0.3)
            ang_perna = math.radians(-(-60 + 20 * t)) * self.direcao
            ang_canela = math.radians(-(45 - 10 * t)) * self.direcao
            # Torso mantém inclinação máxima
            self.angulo_torso = -0.20 * self.direcao
        else:
            t = ease_out_back((progresso - 0.6) / 0.4)
            ang_perna = math.radians(-(-40 + 50 * t)) * self.direcao
            ang_canela = math.radians(-(35 - 30 * t)) * self.direcao
            # Torso retorna suavemente
            self.angulo_torso = -0.20 * (1.0 - t) * self.direcao

        self.angulo_perna_dir = ang_perna
        self.angulo_canela_dir = ang_canela

    def animar_pulo(self, tempo):
        """Animação de pulo: translação vertical com gravidade simulada
        e squash/stretch no pouso."""
        if self.pulando:
            self.vel_y += 0.5  # gravidade
            self.y += self.vel_y
            if self.y >= self.chao_y:
                self.y = self.chao_y
                self.pulando = False
                self.vel_y = 0
                # Squash no pouso: achatamento para dar sensação de peso
                self.escala_x = 1.15
                self.escala_y = 0.85

    def pular(self):
        if not self.pulando:
            self.pulando = True
            self.vel_y = -12

    def atualizar(self, tempo):
        """Atualiza a animação frame a frame."""
        self.animar_pulo(tempo)

        if self.atacando:
            self.frame_ataque += 1
            progresso = self.frame_ataque / 40.0
            if progresso >= 1.0:
                self.atacando = False
                self.frame_ataque = 0
                # Resetar torso ao fim do ataque
                self.angulo_torso = 0
            else:
                if self.tipo_ataque == 'chute':
                    self.animar_chute(progresso)
                else:
                    self.animar_soco(progresso)
        else:
            self.animar_idle(tempo)

        # Efeito de escala de impacto (squash & stretch)
        if self.escala_x != 1.0:
            self.escala_x += (1.0 - self.escala_x) * 0.1
        if self.escala_y != 1.0:
            self.escala_y += (1.0 - self.escala_y) * 0.1


# ======================== CLASSE PARTÍCULA ========================

class Particula:
    """Partícula para efeitos visuais (impacto, poeira).
    Demonstra translação contínua + escala decrescente.
    """
    def __init__(self, x, y, cor):
        self.x = x
        self.y = y
        self.cor = cor
        self.vx = (pygame.time.get_ticks() % 7 - 3) * 1.5
        self.vy = -(pygame.time.get_ticks() % 5 + 2) * 1.2
        self.vida = 1.0
        self.raio = 4

    def atualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15  # gravidade
        self.vida -= 0.03
        self.raio = max(1, int(4 * self.vida))  # escala decrescente

    def desenhar(self, tela):
        if self.vida > 0:
            alpha = max(0, min(255, int(255 * self.vida)))
            cor = (min(255, self.cor[0]), min(255, self.cor[1]), min(255, self.cor[2]))
            pygame.draw.circle(tela, cor, (int(self.x), int(self.y)), self.raio)


# ======================== COREOGRAFIA DA LUTA ========================

class Coreografia:
    """Define a sequência de ações da animação automatizada."""

    def __init__(self, lutador1, lutador2):
        self.l1 = lutador1
        self.l2 = lutador2
        self.tempo = 0
        self.particulas = []
        self.fase = 0
        self.eventos = [
            # (tempo_inicio, ação)
            (60,  'l1_avanca'),
            (120, 'l1_soco'),
            (180, 'l2_recua'),
            (220, 'l2_avanca'),
            (280, 'l2_chute'),
            (340, 'l1_pulo'),
            (380, 'l1_soco_aereo'),
            (440, 'ambos_idle'),
            (500, 'l1_avanca'),
            (540, 'l2_soco'),
            (580, 'l1_chute'),
            (640, 'l2_pulo'),
            (700, 'final'),
        ]
        self.evento_idx = 0

    def atualizar(self):
        self.tempo += 1

        # Verificar próximo evento
        if self.evento_idx < len(self.eventos):
            t_evento, acao = self.eventos[self.evento_idx]
            if self.tempo >= t_evento:
                self._executar_acao(acao)
                self.evento_idx += 1

        # Mover personagens suavemente
        self._atualizar_movimento()

        # Atualizar partículas
        for p in self.particulas[:]:
            p.atualizar()
            if p.vida <= 0:
                self.particulas.remove(p)

    def _executar_acao(self, acao):
        import random
        if acao == 'l1_avanca':
            self.l1._meta_x = self.l1.x + 80
        elif acao == 'l1_soco':
            self.l1.atacando = True
            self.l1.frame_ataque = 0
            self.l1.tipo_ataque = 'soco'
            self.l2.vida -= 15
            self.l2.escala_x = 1.2
            self.l2.escala_y = 0.85
            for _ in range(5):
                self.particulas.append(Particula(
                    self.l2.x - 20, self.l2.y - 40, AMARELO))
        elif acao == 'l2_recua':
            self.l2._meta_x = self.l2.x + 40
        elif acao == 'l2_avanca':
            self.l2._meta_x = self.l2.x - 80
        elif acao == 'l2_chute':
            self.l2.atacando = True
            self.l2.frame_ataque = 0
            self.l2.tipo_ataque = 'chute'
            self.l1.vida -= 20
            self.l1.escala_x = 0.85
            self.l1.escala_y = 1.15
            for _ in range(5):
                self.particulas.append(Particula(
                    self.l1.x + 20, self.l1.y - 40, AMARELO))
        elif acao == 'l1_pulo':
            self.l1.pular()
        elif acao == 'l1_soco_aereo':
            self.l1.atacando = True
            self.l1.frame_ataque = 0
            self.l1.tipo_ataque = 'soco'
            self.l2.vida -= 25
            self.l2.escala_x = 1.3
            self.l2.escala_y = 0.8
            for _ in range(8):
                self.particulas.append(Particula(
                    self.l2.x - 10, self.l2.y - 50, VERMELHO))
        elif acao == 'ambos_idle':
            self.l1.atacando = False
            self.l2.atacando = False
        elif acao == 'l2_soco':
            self.l2.atacando = True
            self.l2.frame_ataque = 0
            self.l2.tipo_ataque = 'soco'
            self.l1.vida -= 15
            for _ in range(5):
                self.particulas.append(Particula(
                    self.l1.x + 15, self.l1.y - 35, AMARELO))
        elif acao == 'l1_chute':
            self.l1.atacando = True
            self.l1.frame_ataque = 0
            self.l1.tipo_ataque = 'chute'
            self.l2.vida -= 20
            for _ in range(5):
                self.particulas.append(Particula(
                    self.l2.x - 15, self.l2.y - 30, AMARELO))
        elif acao == 'l2_pulo':
            self.l2.pular()
        elif acao == 'final':
            pass  # Animação encerra

    def _atualizar_movimento(self):
        """Movimento com spring damping: modelo de mola amortecida.
        Substitui interpolação linear por aceleração/desaceleração natural.
        """
        stiffness = 0.08
        damping = 0.15
        for lutador in [self.l1, self.l2]:
            if hasattr(lutador, '_meta_x'):
                diff = lutador._meta_x - lutador.x
                if abs(diff) > 0.5:
                    force = diff * stiffness
                    lutador._vel_x = (lutador._vel_x + force) * (1.0 - damping)
                    lutador.x += lutador._vel_x
                else:
                    lutador._vel_x = 0.0


# ======================== LOOP PRINCIPAL ========================

def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Stick Fight - Computação Gráfica 2D")
    relogio = pygame.time.Clock()

    # Fonte para texto na tela
    fonte = pygame.font.SysFont("Arial", 18)
    fonte_titulo = pygame.font.SysFont("Arial", 28, bold=True)

    # Criar lutadores
    lutador1 = StickFigure(250, 430, VERMELHO, "Lutador 1", direcao=1)
    lutador2 = StickFigure(650, 430, AZUL, "Lutador 2", direcao=-1)

    # Criar coreografia automática
    coreografia = Coreografia(lutador1, lutador2)

    tempo = 0
    rodando = True

    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False
                elif evento.key == pygame.K_r:
                    # Reset da animação
                    lutador1 = StickFigure(250, 430, VERMELHO, "Lutador 1", direcao=1)
                    lutador2 = StickFigure(650, 430, AZUL, "Lutador 2", direcao=-1)
                    coreografia = Coreografia(lutador1, lutador2)
                    tempo = 0

        tempo += 1.0 / FPS

        # Atualizar
        coreografia.atualizar()
        lutador1.atualizar(tempo)
        lutador2.atualizar(tempo)

        # ===== RENDERIZAÇÃO =====
        tela.fill((30, 30, 40))  # Fundo escuro

        # Chão com gradiente simples
        pygame.draw.rect(tela, CHAO_COR, (0, 450, LARGURA, 150))
        pygame.draw.line(tela, (120, 100, 70), (0, 450), (LARGURA, 450), 2)

        # Grade de referência (demonstra sistema de coordenadas)
        for gx in range(0, LARGURA, 50):
            pygame.draw.line(tela, (40, 40, 50), (gx, 0), (gx, 450), 1)
        for gy in range(0, 450, 50):
            pygame.draw.line(tela, (40, 40, 50), (0, gy), (LARGURA, gy), 1)

        # Desenhar partículas
        for p in coreografia.particulas:
            p.desenhar(tela)

        # Desenhar lutadores
        lutador1.desenhar(tela)
        lutador2.desenhar(tela)

        # HUD (Interface)
        titulo = fonte_titulo.render("STICK FIGHT - CG 2D", True, BRANCO)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 10))

        # Info de transformações ativas
        info1 = f"L1: pos=({int(lutador1.x)},{int(lutador1.y)}) escala=({lutador1.escala_x:.2f},{lutador1.escala_y:.2f})"
        info2 = f"L2: pos=({int(lutador2.x)},{int(lutador2.y)}) escala=({lutador2.escala_x:.2f},{lutador2.escala_y:.2f})"
        tela.blit(fonte.render(info1, True, VERMELHO), (10, ALTURA - 60))
        tela.blit(fonte.render(info2, True, AZUL), (10, ALTURA - 35))
        tela.blit(fonte.render("[R] Reiniciar  [ESC] Sair", True, CINZA_CLARO), (LARGURA - 250, ALTURA - 35))

        pygame.display.flip()
        relogio.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
