import pygame
import random
import sys

# --- CONFIGURĂRI INIȚIALE ---
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Prototip: Interfață Șeptică / Cruce")
clock = pygame.time.Clock()

# Culori
GREEN_TABLE = (34, 139, 34)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
BLUE = (0, 0, 128)
GRAY = (200, 200, 200)

# Fonturi
font_large = pygame.font.SysFont('Arial', 32, bold=True)
font_small = pygame.font.SysFont('Arial', 20)


# --- CLASELE JOCULUI ---
class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.width = 80
        self.height = 120
        self.color = RED if suit in ['♥', '♦'] else BLACK

    def draw(self, surface, x, y, face_up=True):
        rect = pygame.Rect(x, y, self.width, self.height)
        if face_up:
            pygame.draw.rect(surface, WHITE, rect, border_radius=8)
            pygame.draw.rect(surface, BLACK, rect, 2, border_radius=8)

            # Text pe carte
            val_text = font_large.render(self.value, True, self.color)
            suit_text = font_large.render(self.suit, True, self.color)

            surface.blit(val_text, (x + 5, y + 5))
            surface.blit(suit_text, (x + self.width - 25, y + self.height - 35))
            # Simbol central
            center_suit = font_large.render(self.suit, True, self.color)
            surface.blit(center_suit, (x + self.width // 2 - 10, y + self.height // 2 - 15))
        else:
            pygame.draw.rect(surface, BLUE, rect, border_radius=8)
            pygame.draw.rect(surface, WHITE, rect, 2, border_radius=8)
            pattern = font_small.render("DIGITAL", True, WHITE)
            surface.blit(pattern, (x + 5, y + 50))
        return rect


class Deck:
    def __init__(self):
        suits = ['♥', '♦', '♣', '♠']
        values = ['7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [Card(s, v) for s in suits for v in values]
        random.shuffle(self.cards)

    def draw_card(self):
        return self.cards.pop() if self.cards else None


class Game:
    def __init__(self):
        self.deck = Deck()
        self.players_hands = {0: [], 1: [], 2: [], 3: []}  # 0 e jucătorul uman
        self.table_cards = []  # Cărțile jucate în runda curentă
        self.turn = 0
        self.deal_initial_cards()

    def deal_initial_cards(self):
        for _ in range(4):
            for i in range(4):
                self.players_hands[i].append(self.deck.draw_card())

    def play_card(self, player_id, card_index):
        if player_id == self.turn and card_index < len(self.players_hands[player_id]):
            card = self.players_hands[player_id].pop(card_index)
            # Salvăm cartea și cine a jucat-o
            self.table_cards.append({"player": player_id, "card": card})
            self.turn = (self.turn + 1) % 4

            # Dacă toți 4 au jucat, așteptăm puțin și curățăm masa (simulare rundă)
            if len(self.table_cards) == 4:
                pygame.time.set_timer(pygame.USEREVENT, 1500)  # Timer de 1.5s pentru a vedea cărțile

    def bot_play(self):
        if self.turn != 0 and len(self.table_cards) < 4:
            pygame.time.wait(600)  # Delay artificial pentru bot
            bot_hand = self.players_hands[self.turn]
            if bot_hand:
                # Botul alege o carte random
                card_idx = random.randint(0, len(bot_hand) - 1)
                self.play_card(self.turn, card_idx)


# --- INIȚIALIZARE JOC ---
game = Game()
card_rects = []  # Pentru a detecta click-urile

# --- BUCILA PRINCIPALĂ (GAME LOOP) ---
running = True
while running:
    screen.fill(GREEN_TABLE)

    # 1. Desenăm elementele de fundal și UI-ul central
    pygame.draw.circle(screen, (24, 110, 24), (WIDTH // 2, HEIGHT // 2), 200)
    info_text = font_large.render("Masa de Joc", True, (0, 50, 0))
    screen.blit(info_text, (WIDTH // 2 - 80, HEIGHT // 2 - 20))

    turn_text = font_small.render(f"Rândul jucătorului: {'TU' if game.turn == 0 else 'Bot ' + str(game.turn)}", True,
                                  WHITE)
    screen.blit(turn_text, (20, 20))

    cards_left = font_small.render(f"Cărți în pachet: {len(game.deck.cards)}", True, WHITE)
    screen.blit(cards_left, (WIDTH - 180, 20))

    # 2. Desenăm mâinile Boților (Cărți cu fața în jos)
    # Bot 1 (Stânga)
    for i, card in enumerate(game.players_hands[1]):
        card.draw(screen, 50, HEIGHT // 2 - 100 + (i * 30), face_up=False)
    # Bot 2 (Sus)
    for i, card in enumerate(game.players_hands[2]):
        card.draw(screen, WIDTH // 2 - 100 + (i * 90), 20, face_up=False)
    # Bot 3 (Dreapta)
    for i, card in enumerate(game.players_hands[3]):
        card.draw(screen, WIDTH - 130, HEIGHT // 2 - 100 + (i * 30), face_up=False)

    # 3. Desenăm mâna Jucătorului Uman (Jos, cu fața în sus)
    card_rects.clear()
    start_x = WIDTH // 2 - (len(game.players_hands[0]) * 90) // 2
    for i, card in enumerate(game.players_hands[0]):
        rect = card.draw(screen, start_x + (i * 90), HEIGHT - 140, face_up=True)
        card_rects.append(rect)

    # 4. Desenăm cărțile de pe masă (Jucate)
    positions = [
        (WIDTH // 2 - 40, HEIGHT // 2 + 50),  # Jucător (Jos)
        (WIDTH // 2 - 150, HEIGHT // 2 - 60),  # Bot 1 (Stânga)
        (WIDTH // 2 - 40, HEIGHT // 2 - 170),  # Bot 2 (Sus)
        (WIDTH // 2 + 70, HEIGHT // 2 - 60)  # Bot 3 (Dreapta)
    ]
    for item in game.table_cards:
        p_id = item["player"]
        item["card"].draw(screen, positions[p_id][0], positions[p_id][1], face_up=True)

    # 5. Gestionarea evenimentelor (Input utilizator)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

        # Curățare masă după ce au jucat toți
        if event.type == pygame.USEREVENT:
            pygame.time.set_timer(pygame.USEREVENT, 0)  # Oprire timer
            game.table_cards.clear()

            # Tragem cărți noi din pachet dacă e nevoie
            for i in range(4):
                if game.deck.cards and len(game.players_hands[i]) < 4:
                    game.players_hands[i].append(game.deck.draw_card())

        # Click jucător uman
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game.turn == 0 and len(game.table_cards) < 4:
                mouse_pos = event.pos
                for i, rect in enumerate(card_rects):
                    if rect.collidepoint(mouse_pos):
                        game.play_card(0, i)
                        break

    # 6. Logica Boților
    game.bot_play()

    pygame.display.flip()
    clock.tick(30)