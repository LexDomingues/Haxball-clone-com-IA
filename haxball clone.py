import pygame
import sys
import math
import time
import random

pygame.init()

# ===== JANELA (FULLSCREEN) =====
info = pygame.display.Info()
LARGURA, ALTURA = info.current_w, info.current_h
TELA = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN)
pygame.display.set_caption("HaxBall Clone")

# ===== CORES =====
BRANCO = (255, 255, 255)
VERMELHO = (200, 0, 0)
AZUL = (0, 100, 255)
PRETO = (0, 0, 0)
VERDE = (0, 200, 0)
CINZA = (30, 30, 30)
AMARELO = (255, 255, 0)  # Cor para destaque do menu

# ===== FONTES =====
fonte_gigante = pygame.font.SysFont("arial", 120, True)
fonte_grande = pygame.font.SysFont("arial", 90, True)
fonte_media = pygame.font.SysFont("arial", 60, True)
fonte_pequena = pygame.font.SysFont("arial", 40, True)

# ===== CONFIG =====
FPS = 60
clock = pygame.time.Clock()


# ===== JOGADORES E BOLA =====
class Jogador:
    def __init__(self, x, y, cor, lado):
        self.x = x
        self.y = y
        self.vel = 7
        self.raio = 40
        self.cor = cor
        self.lado = lado
        self.direcao = pygame.math.Vector2(0, 0)
        self.travado = False
        self.pos_inicial = (x, y)
        self.ultimo_chute = 0
        self.cooldown_chute = 0.5
        self.encostou = False  # flag pra detectar toque na bola

    def mover(self, teclas):
        # REGRA DO KICK-OFF: Não se move se estiver travado.
        if self.travado:
            return

        self.direcao = pygame.math.Vector2(0, 0)

        # Movimentação para o jogador da Esquerda (Vermelho - Humano)
        if self.lado == "esquerda":
            if teclas[pygame.K_w]: self.direcao.y = -1
            if teclas[pygame.K_s]: self.direcao.y = 1
            if teclas[pygame.K_a]: self.direcao.x = -1
            if teclas[pygame.K_d]: self.direcao.x = 1

        # Movimentação para o jogador da Direita (Azul - Humano)
        elif self.lado == "direita" and modo_jogo == '2j':
            if teclas[pygame.K_UP]: self.direcao.y = -1
            if teclas[pygame.K_DOWN]: self.direcao.y = 1
            if teclas[pygame.K_LEFT]: self.direcao.x = -1
            if teclas[pygame.K_RIGHT]: self.direcao.x = 1

        if self.direcao.length() > 0:
            self.direcao = self.direcao.normalize()
        self.x += self.direcao.x * self.vel
        self.y += self.direcao.y * self.vel

        self.x = max(self.raio, min(LARGURA - self.raio, self.x))
        self.y = max(self.raio, min(ALTURA - self.raio, self.y))

    def chute(self, bola, tecla_chute, teclas):
        # REGRA DO KICK-OFF: Não chuta se estiver travado.
        if self.travado:
            return

        agora = time.time()

        # Verifica se o jogador é humano ou se é a IA
        if self.lado == "direita" and 'ia' in modo_jogo:
            chutando = tecla_chute  # No caso da IA, 'tecla_chute' será um booleano (True/False)
        else:
            chutando = teclas[tecla_chute]  # Verifica a tecla pressionada para o humano

        if chutando and agora - self.ultimo_chute >= self.cooldown_chute:
            dx = bola.x - self.x
            dy = bola.y - self.y
            distancia = math.hypot(dx, dy)
            if distancia <= self.raio + bola.raio + 10:
                direcao = pygame.math.Vector2(dx, dy)
                if direcao.length() > 0:
                    direcao = direcao.normalize()
                    forca_chute = 18

                    bola.velx += direcao.x * forca_chute
                    bola.vely += direcao.y * forca_chute
                    self.ultimo_chute = agora
                    self.encostou = True  # marcou toque ao chutar

    def desenhar(self):
        pygame.draw.circle(TELA, self.cor, (int(self.x), int(self.y)), self.raio)
        pygame.draw.circle(TELA, BRANCO, (int(self.x), int(self.y)), self.raio, 3)


class Bola:
    def __init__(self):
        self.x = LARGURA // 2
        self.y = ALTURA // 2
        self.raio = 25
        self.velx = 0
        self.vely = 0

    def mover(self):
        self.x += self.velx
        self.y += self.vely
        self.velx *= 0.985
        self.vely *= 0.985
        if math.hypot(self.velx, self.vely) < 0.1:
            self.velx = self.vely = 0

        # colisão com as bordas
        if self.y - self.raio < 0:
            self.y = self.raio
            self.vely *= -1
        elif self.y + self.raio > ALTURA:
            self.y = ALTURA - self.raio
            self.vely *= -1
        if self.x - self.raio < 0:
            self.x = self.raio
            self.velx *= -1
        elif self.x + self.raio > LARGURA:
            self.x = LARGURA - self.raio
            self.velx *= -1

    def desenhar(self):
        pygame.draw.circle(TELA, BRANCO, (int(self.x), int(self.y)), self.raio)
        pygame.draw.circle(TELA, PRETO, (int(self.x), int(self.y)), self.raio, 2)


def colisao_bola_jogador(bola, jogador):
    dx = bola.x - jogador.x
    dy = bola.y - jogador.y
    distancia = math.hypot(dx, dy)
    soma_raios = bola.raio + jogador.raio
    if distancia < soma_raios:
        # A flag é definida APENAS se houver toque neste frame (USADA PARA O KICK-OFF)
        jogador.encostou = True
        angulo = math.atan2(dy, dx)
        sobreposicao = soma_raios - distancia
        bola.x += math.cos(angulo) * sobreposicao / 2
        bola.y += math.sin(angulo) * sobreposicao / 2
        jogador.x -= math.cos(angulo) * sobreposicao / 2
        jogador.y -= math.sin(angulo) * sobreposicao / 2
        bola.velx = math.cos(angulo) * 8
        bola.vely = math.sin(angulo) * 8


def verificar_gol(bola):
    if bola.y > ALTURA // 2 - 100 and bola.y < ALTURA // 2 + 100:
        if bola.x - bola.raio <= 0:
            return "azul"
        elif bola.x + bola.raio >= LARGURA:
            return "vermelho"
    return None


def resetar_posicoes(j1, j2, bola):
    j1.x, j1.y = j1.pos_inicial
    j2.x, j2.y = j2.pos_inicial
    bola.x, bola.y = LARGURA // 2, ALTURA // 2
    bola.velx = bola.vely = 0
    j1.travado = False
    j2.travado = False

    # === Reseta as flags de toque após o gol ===
    j1.encostou = False
    j2.encostou = False
    # ====================================================


# ===== GERENCIAMENTO DE ESTADO (Variáveis Globais Inicializadas) =====
j1 = Jogador(LARGURA * 0.25, ALTURA / 2, VERMELHO, "esquerda")
j2 = Jogador(LARGURA * 0.75, ALTURA / 2, AZUL, "direita")
bola = Bola()
placar = [0, 0]
tempo_inicio = time.time()
tempo_pausado = 0
gol_marcado = False
tempo_gol = 0
esperando_toque = False
ultimo_gol = None
estado_jogo = 'menu'
vencedor = None
modo_jogo = '2j'


def iniciar_jogo(modo):
    global j1, j2, bola, placar, tempo_inicio, tempo_pausado, gol_marcado, esperando_toque, ultimo_gol, estado_jogo, vencedor, modo_jogo

    j1 = Jogador(LARGURA * 0.25, ALTURA / 2, VERMELHO, "esquerda")
    j2 = Jogador(LARGURA * 0.75, ALTURA / 2, AZUL, "direita")
    bola = Bola()
    placar = [0, 0]
    tempo_inicio = time.time()
    tempo_pausado = 0
    gol_marcado = False
    esperando_toque = False
    ultimo_gol = None
    vencedor = None
    modo_jogo = modo
    estado_jogo = 'jogando'


# ===== MENU PRINCIPAL E SELEÇÃO =====
opcoes_menu = ["2 Jogadores", "Contra a IA", "Instruções", "Sair"]
selecao_menu = 0
pode_selecionar = True

opcoes_ia = [
    ("Fácil", 'ia_facil'),
    ("Médio", 'ia_medio'),
    ("Difícil", 'ia_dificil'),
    ("Hard", 'ia_hard')
]
selecao_ia = 0
pode_selecionar_ia = True


def desenhar_menu():
    TELA.fill(CINZA)

    titulo = fonte_gigante.render("HAXBALL CLONE", True, BRANCO)
    TELA.blit(titulo, (LARGURA / 2 - titulo.get_width() / 2, ALTURA / 4))

    for i, opcao in enumerate(opcoes_menu):
        cor = AMARELO if i == selecao_menu else BRANCO
        texto_opcao = fonte_media.render(opcao, True, cor)
        pos_y = ALTURA / 2 + i * 80
        TELA.blit(texto_opcao, (LARGURA / 2 - texto_opcao.get_width() / 2, pos_y))


def processar_menu(eventos):
    global selecao_menu, pode_selecionar, estado_jogo

    for evento in eventos:
        if evento.type == pygame.KEYDOWN:
            if pode_selecionar:
                if evento.key == pygame.K_DOWN or evento.key == pygame.K_s:
                    selecao_menu = (selecao_menu + 1) % len(opcoes_menu)
                elif evento.key == pygame.K_UP or evento.key == pygame.K_w:
                    selecao_menu = (selecao_menu - 1 + len(opcoes_menu)) % len(opcoes_menu)

                pode_selecionar = False

                if evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                    if selecao_menu == 0:
                        iniciar_jogo('2j')
                    elif selecao_menu == 1:
                        estado_jogo = 'selecao_ia'
                        selecao_ia = 0
                        pode_selecionar_ia = True
                    elif selecao_menu == 2:
                        estado_jogo = 'instrucoes'
                    elif selecao_menu == 3:
                        pygame.quit()
                        sys.exit()

        if evento.type == pygame.KEYUP:
            if evento.key in [pygame.K_DOWN, pygame.K_UP, pygame.K_s, pygame.K_w]:
                pode_selecionar = True


def desenhar_selecao_ia():
    TELA.fill(CINZA)

    titulo = fonte_grande.render("SELECIONE A DIFICULDADE DA IA", True, BRANCO)
    TELA.blit(titulo, (LARGURA / 2 - titulo.get_width() / 2, ALTURA / 4))

    for i, (nome, _) in enumerate(opcoes_ia):
        cor_destaque = AMARELO if i == selecao_ia else BRANCO
        texto_opcao = fonte_media.render(nome, True, cor_destaque)
        pos_y = ALTURA / 2 + i * 80
        TELA.blit(texto_opcao, (LARGURA / 2 - texto_opcao.get_width() / 2, pos_y))

    voltar_txt = fonte_pequena.render("Pressione ESC para voltar", True, BRANCO)
    TELA.blit(voltar_txt, (LARGURA / 2 - voltar_txt.get_width() / 2, ALTURA - 100))


def processar_selecao_ia(eventos):
    global selecao_ia, pode_selecionar_ia, estado_jogo

    for evento in eventos:
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                estado_jogo = 'menu'
                return

            if pode_selecionar_ia:
                if evento.key == pygame.K_DOWN or evento.key == pygame.K_s:
                    selecao_ia = (selecao_ia + 1) % len(opcoes_ia)
                elif evento.key == pygame.K_UP or evento.key == pygame.K_w:
                    selecao_ia = (selecao_ia - 1 + len(opcoes_ia)) % len(opcoes_ia)

                pode_selecionar_ia = False

                if evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                    modo = opcoes_ia[selecao_ia][1]
                    iniciar_jogo(modo)

        if evento.type == pygame.KEYUP:
            if evento.key in [pygame.K_DOWN, pygame.K_UP, pygame.K_s, pygame.K_w]:
                pode_selecionar_ia = True


# LÓGICA DA IA (Defesa/Ataque)
def logica_ia(jogador_ia, bola, modo):
    # REGRA DO KICK-OFF: A IA não se move se estiver travada.
    if jogador_ia.travado:
        return

    # --- Parâmetros de Dificuldade ---
    if modo == 'ia_facil':
        velocidade_multi = 0.5
        precisao_alvo = 0.7
        chance_erro_chute = 0.5
        raio_chute_base = jogador_ia.raio + bola.raio + 5
        deve_defender = False
        chute_cooldown = 0.7

    elif modo == 'ia_medio':
        velocidade_multi = 0.75
        precisao_alvo = 0.4
        chance_erro_chute = 0.1
        raio_chute_base = jogador_ia.raio + bola.raio + 10
        deve_defender = bola.x > LARGURA * (2 / 3)
        chute_cooldown = 0.5

    elif modo == 'ia_dificil':
        velocidade_multi = 1.0
        precisao_alvo = 0.1
        chance_erro_chute = 0.0
        raio_chute_base = jogador_ia.raio + bola.raio + 15
        deve_defender = bola.x > LARGURA * (1 / 2) or bola.velx < -1
        chute_cooldown = 0.3

    elif modo == 'ia_hard':
        # Mais rápida, mais precisa, reação de chute mais rápida.
        velocidade_multi = 1.2
        precisao_alvo = 0.05
        chance_erro_chute = 0.0
        raio_chute_base = jogador_ia.raio + bola.raio + 20
        chute_cooldown = 0.25

        # --- Lógica de Defesa/Ataque para IA_HARD ---
        deve_defender = bola.x > LARGURA * 0.8  # Defesa Absoluta

    # Ajusta o cooldown de chute da IA
    jogador_ia.cooldown_chute = chute_cooldown

    # --- Parâmetros dinâmicos ---
    raio_chute = raio_chute_base

    # --- Definição do Alvo ---

    # Prioridade 1: Kick-off (Toque Inicial) - Move para a bola se estiver livre
    if esperando_toque and not jogador_ia.travado:
        alvo_x = bola.x
        alvo_y = bola.y
        velocidade_multi = 1.0
        deve_defender = False

    # Lógica de Movimento Normal (Ataque/Defesa)
    elif deve_defender:
        # MODO DEFESA: Ficar entre a bola e o gol
        gol_x = LARGURA
        gol_y = ALTURA // 2

        peso_gol = 0.7
        alvo_x = int(gol_x * peso_gol + bola.x * (1 - peso_gol))

        # Alvo vertical SIMPLES
        alvo_y = int(gol_y * 0.5 + bola.y * 0.5)

        # Garante que o alvo não passe muito da linha de ataque da IA
        alvo_x = min(LARGURA - jogador_ia.raio * 1.5, alvo_x)

    else:
        # MODO ATAQUE/CHUTE: Posicionar-se para chutar no gol J1.

        # Alvos padrão (mirar a bola)
        alvo_x = bola.x - (bola.x - jogador_ia.raio) * precisao_alvo
        alvo_y = bola.y

    # Aplica limites de tela
    alvo_x = max(jogador_ia.raio, min(LARGURA - jogador_ia.raio, alvo_x))
    alvo_y = max(jogador_ia.raio, min(ALTURA - jogador_ia.raio, alvo_y))

    # --- Movimento para o Alvo ---
    dx = alvo_x - jogador_ia.x
    dy = alvo_y - jogador_ia.y
    distancia = math.hypot(dx, dy)

    if distancia > 1:
        direcao_ia = pygame.math.Vector2(dx, dy).normalize()
        # Aplica a velocidade multiplicada pela dificuldade
        jogador_ia.x += direcao_ia.x * jogador_ia.vel * velocidade_multi
        jogador_ia.y += direcao_ia.y * jogador_ia.vel * velocidade_multi

        # Aplica limites de tela novamente
        jogador_ia.x = max(jogador_ia.raio, min(LARGURA - jogador_ia.raio, jogador_ia.x))
        jogador_ia.y = max(jogador_ia.raio, min(ALTURA - jogador_ia.raio, jogador_ia.y))

    # --- Chute ---
    dx_bola = bola.x - jogador_ia.x
    dy_bola = bola.y - jogador_ia.y
    distancia_bola = math.hypot(dx_bola, dy_bola)

    # O raio de chute é apenas o base (raio_chute_base)
    deve_chutar = (distancia_bola < raio_chute) and not esperando_toque

    # Aplica a chance de erro, exceto se a chance_erro_chute for 0.0
    if deve_chutar and chance_erro_chute > 0 and random.random() < chance_erro_chute:
        deve_chutar = False

    jogador_ia.chute(bola, deve_chutar, None)


def desenhar_instrucoes():
    TELA.fill(CINZA)
    titulo = fonte_grande.render("INSTRUÇÕES", True, BRANCO)
    TELA.blit(titulo, (LARGURA / 2 - titulo.get_width() / 2, 50))

    instrucoes_texto = [
        "JOGADOR VERMELHO (Esquerda):",
        "Movimento: W, A, S, D",
        "Chute: ESPAÇO",
        "",
        "JOGADOR AZUL (Direita) - IA:",
        "Fácil: Ataca a bola em todo o campo (erros frequentes).",
        "Médio: Prioriza defesa em seu terço (mais erros).",
        "Difícil: Prioriza defesa em sua metade (poucos erros, rápida).",
        "Hard: Defesa absoluta APENAS no último 1/5 do campo. Ataca vigorosamente no restante.",
        # Descrição simplificada
        "",
        "Regras:",
        "Marque 3 gols para vencer.",
        "Após um gol, o time que marcou é travado até o adversário tocar na bola.",
        "",
        "Pressione ESC para voltar ao Menu"
    ]

    for i, linha in enumerate(instrucoes_texto):
        cor = VERMELHO if i == 0 else AZUL if i == 5 else BRANCO
        texto_linha = fonte_pequena.render(linha, True, cor)
        TELA.blit(texto_linha, (LARGURA / 2 - texto_linha.get_width() / 2, 200 + i * 50))


def processar_instrucoes(eventos):
    global estado_jogo
    for evento in eventos:
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                estado_jogo = 'menu'


# ===== LOOP PRINCIPAL =====
while True:
    TELA.fill(CINZA)
    eventos = pygame.event.get()
    for evento in eventos:
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE and estado_jogo in ['jogando', 'vitoria',
                                                                                               'instrucoes',
                                                                                               'selecao_ia']:
            estado_jogo = 'menu'

    # ===== GERENCIAMENTO DE ESTADOS =====
    if estado_jogo == 'menu':
        desenhar_menu()
        processar_menu(eventos)

    elif estado_jogo == 'selecao_ia':
        desenhar_selecao_ia()
        processar_selecao_ia(eventos)

    elif estado_jogo == 'instrucoes':
        desenhar_instrucoes()
        processar_instrucoes(eventos)

    elif estado_jogo == 'vitoria':
        if vencedor:
            vitoria_txt = fonte_grande.render(f"Vitória do {vencedor.capitalize()}!", True, BRANCO)
            sair_txt = fonte_pequena.render("Pressione ESC para voltar ao Menu", True, VERDE)
            TELA.blit(vitoria_txt, (LARGURA / 2 - vitoria_txt.get_width() / 2, ALTURA / 2 - 100))
            TELA.blit(sair_txt, (LARGURA / 2 - sair_txt.get_width() / 2, ALTURA / 2 + 50))

    elif estado_jogo == 'jogando':
        teclas = pygame.key.get_pressed()

        # JOGADOR VERMELHO (Sempre humano)
        j1.mover(teclas)
        j1.chute(bola, pygame.K_SPACE, teclas)

        # JOGADOR AZUL (Humano ou IA)
        if modo_jogo == '2j':
            j2.mover(teclas)
            j2.chute(bola, pygame.K_RETURN, teclas)
        elif 'ia' in modo_jogo:
            logica_ia(j2, bola, modo_jogo)

        bola.mover()

        # Resetar as flags de toque ANTES de verificar a colisão/toque neste frame
        j1.encostou = False
        j2.encostou = False

        # A colisão pode definir 'encostou' como True para este frame
        colisao_bola_jogador(bola, j1)
        colisao_bola_jogador(bola, j2)

        # ===== GOL =====
        if not gol_marcado:
            gol = verificar_gol(bola)
            if gol:
                gol_marcado = True
                tempo_gol = time.time()
                ultimo_gol = gol
                # Reseta posições e flags de travamento/toque
                resetar_posicoes(j1, j2, bola)

                # O time que marcou o gol é travado (Regra HaxBall)
                if gol == "vermelho":
                    placar[0] += 1
                    j1.travado = True  # J1 (Vermelho) fez o gol, fica travado.
                    j2.travado = False  # J2 (Azul) sofreu, começa livre.
                else:  # gol == "azul"
                    placar[1] += 1
                    j2.travado = True  # J2 (Azul) fez o gol, fica travado.
                    j1.travado = False  # J1 (Vermelho) sofreu, começa livre.

                esperando_toque = True
                tempo_pausado += time.time() - tempo_inicio

                if placar[0] >= 3:
                    vencedor = "vermelho"
                    estado_jogo = 'vitoria'
                elif placar[1] >= 3:
                    vencedor = "azul"
                    estado_jogo = 'vitoria'

        # ===== LIBERAÇÃO DO JOGADOR TRAVADO (Kick-off) - ESTA É A REGRA APLICADA PARA TODOS =====
        if esperando_toque:

            # Se J1 (Vermelho) está travado, ele será liberado se o J2 (Azul, LIVRE, IA ou Humano) tocar.
            if j1.travado:
                if j2.encostou:
                    j1.travado = False
                    esperando_toque = False
                    gol_marcado = False
                    tempo_inicio = time.time()

            # Se J2 (Azul, IA ou Humano) está travado, ele será liberado se o J1 (Vermelho, LIVRE) tocar.
            elif j2.travado:
                if j1.encostou:
                    j2.travado = False
                    esperando_toque = False
                    gol_marcado = False
                    tempo_inicio = time.time()

        # ===== DESENHO DO CAMPO E PLACAR =====
        pygame.draw.line(TELA, BRANCO, (LARGURA / 2, 0), (LARGURA / 2, ALTURA), 5)
        pygame.draw.circle(TELA, BRANCO, (LARGURA // 2, ALTURA // 2), 100, 5)
        pygame.draw.rect(TELA, VERDE, (0, ALTURA / 2 - 100, 20, 200))
        pygame.draw.rect(TELA, VERDE, (LARGURA - 20, ALTURA / 2 - 100, 20, 200))

        j1.desenhar()
        j2.desenhar()
        bola.desenhar()

        texto = fonte_media.render(f"{placar[0]}    {placar[1]}", True, BRANCO)
        TELA.blit(texto, (LARGURA / 2 - texto.get_width() / 2, 40))

        if not gol_marcado:
            tempo_jogo = int(time.time() - tempo_inicio + tempo_pausado)
            minutos = tempo_jogo // 60
            segundos = tempo_jogo % 60
            cronometro = fonte_pequena.render(f"{minutos:02}:{segundos:02}", True, BRANCO)
            TELA.blit(cronometro, (LARGURA / 2 - cronometro.get_width() / 2, 110))

        if gol_marcado:
            gol_txt = fonte_grande.render("GOOOOL!", True, BRANCO)
            TELA.blit(gol_txt, (LARGURA / 2 - gol_txt.get_width() / 2, ALTURA / 2 - 150))

    pygame.display.flip()
    clock.tick(FPS)