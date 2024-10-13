import pygame
import sys
import copy
 
# Initialize Pygame
pygame.init()
 
# Get the screen's width and height
screen_info = pygame.display.Info()
WIDTH, HEIGHT = screen_info.current_w, screen_info.current_h
 
# Ensure the window is not bigger than the actual screen
WIDTH = min(WIDTH, 600)  # Max width 600
HEIGHT = min(HEIGHT, 600)  # Max height 600
 
# Screen dimensions
ROWS, COLS = 8, 8
SQUARE_SIZE = min(WIDTH // COLS, HEIGHT // ROWS)
 
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREY = (128, 128, 128)
GREEN = (0, 255, 0)
 
# Initialize screen with resizable option
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('Checkers - The Pycodes')
 
# Piece class
class Piece:
 PADDING = 15
 BORDER = 2
 
 def __init__(self, row, col, color):
     self.row = row
     self.col = col
     self.color = color
     self.king = False
     self.x = 0
     self.y = 0
     self.calc_pos()
 
 def calc_pos(self):
     self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
     self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2
 
 def make_king(self):
     self.king = True
 
 def draw(self, win):
     radius = SQUARE_SIZE // 2 - self.PADDING
     pygame.draw.circle(win, self.color, (self.x, self.y), radius + self.BORDER)
     pygame.draw.circle(win, GREY, (self.x, self.y), radius)
     if self.king:
         pygame.draw.circle(win, GREEN, (self.x, self.y), radius - 5)
 
 def move(self, row, col):
     self.row = row
     self.col = col
     self.calc_pos()
 
# Board class
class Board:
 def __init__(self):
     self.board = []
     self.red_left = self.blue_left = 12
     self.red_kings = self.blue_kings = 0
     self.create_board()
 
 def create_board(self):
     for row in range(ROWS):
         self.board.append([])
         for col in range(COLS):
             if (row + col) % 2 == 0:
                 self.board[row].append(0)
             else:
                 if row < 3:
                     self.board[row].append(Piece(row, col, BLUE))
                 elif row > 4:
                     self.board[row].append(Piece(row, col, RED))
                 else:
                     self.board[row].append(0)
 
 def draw_squares(self, win):
     win.fill(BLACK)
     for row in range(ROWS):
         for col in range(row % 2, COLS, 2):
             pygame.draw.rect(win, WHITE, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
 
 def draw(self, win):
     self.draw_squares(win)
     for row in range(ROWS):
         for col in range(COLS):
             piece = self.board[row][col]
             if piece != 0:
                 piece.draw(win)
 
 def move(self, piece, row, col):
     self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
     piece.move(row, col)
 
 
     if row == 0 or row == ROWS - 1:
         piece.make_king()
 
 def get_piece(self, row, col):
     return self.board[row][col]
 
 def get_all_pieces(self, color):
     pieces = []
     for row in self.board:
         for piece in row:
             if piece != 0 and piece.color == color:
                 pieces.append(piece)
     return pieces
 
 def get_valid_moves(self, piece):
     moves = {}
     left = piece.col - 1
     right = piece.col + 1
     row = piece.row
 
     if piece.color == RED or piece.king:
         moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
         moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
 
     if piece.color == BLUE or piece.king:
         moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
         moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))
 
     return moves
 
 def _traverse_left(self, start, stop, step, color, left, skipped=[]):
     moves = {}
     last = []
     for r in range(start, stop, step):
         if left < 0:
             break
 
         current = self.board[r][left]
         if current == 0:
             if skipped and not last:
                 break
             elif skipped:
                 moves[(r, left)] = last + skipped
             else:
                 moves[(r, left)] = last
 
             if last:
                 if step == -1:
                     row = max(r - 3, 0)
                 else:
                     row = min(r + 3, ROWS)
                 moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=last))
                 moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=last))
             break
         elif current.color == color:
             break
         else:
             last = [current]
 
         left -= 1
 
     return moves
 
 def _traverse_right(self, start, stop, step, color, right, skipped=[]):
     moves = {}
     last = []
     for r in range(start, stop, step):
         if right >= COLS:
             break
 
         current = self.board[r][right]
         if current == 0:
             if skipped and not last:
                 break
             elif skipped:
                 moves[(r, right)] = last + skipped
             else:
                 moves[(r, right)] = last
 
             if last:
                 if step == -1:
                     row = max(r - 3, 0)
                 else:
                     row = min(r + 3, ROWS)
                 moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=last))
                 moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=last))
             break
         elif current.color == color:
             break
         else:
             last = [current]
 
         right += 1
 
     return moves
 
 def remove(self, pieces):
     for piece in pieces:
         self.board[piece.row][piece.col] = 0
         if piece != 0:
             if piece.color == RED:
                 self.red_left -= 1
             else:
                 self.blue_left -= 1
 
 def evaluate(self):
     score = 0
     for piece in self.get_all_pieces(BLUE):
         score += 10  # Higher score for BLUE pieces
         if piece.king:
             score += 5  # Additional score for kings
     for piece in self.get_all_pieces(RED):
         score -= 10  # Lower score for RED pieces
         if piece.king:
             score -= 5  # Additional penalty for opponent's kings
     return score
 
 def winner(self):
     if self.red_left <= 0:
         return "BLUE"
     elif self.blue_left <= 0:
         return "RED"
     return None
 
# Game class
class Game:
 def __init__(self, is_computer=False):
     self.board = Board()
     self.turn = RED
     self.selected_piece = None
     self.valid_moves = {}
     self.is_computer = is_computer  # True if playing against computer
 
 def reset(self):
     self.__init__(self.is_computer)
 
 def select(self, row, col):
     if self.selected_piece:
         result = self._move(row, col)
         if not result:
             self.selected_piece = None
             self.select(row, col)
 
     piece = self.board.get_piece(row, col)
     if piece != 0 and piece.color == self.turn:
         self.selected_piece = piece
         self.valid_moves = self.board.get_valid_moves(piece)
         return True
     return False
 
 def _move(self, row, col):
     piece = self.selected_piece
     if piece and (row, col) in self.valid_moves:
         self.board.move(piece, row, col)
         skipped = self.valid_moves[(row, col)]
         if skipped:
             self.board.remove(skipped)
         self.change_turn()
     else:
         return False
     return True
 
 def change_turn(self):
     self.valid_moves = {}
     self.turn = BLUE if self.turn == RED else RED
 
     if self.is_computer and self.turn == BLUE:
         self.computer_turn()
 
 def draw_valid_moves(self, moves):
     for move in moves:
         row, col = move
         pygame.draw.circle(screen, GREEN,
                            (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), 15)
 
 def update(self):
     self.board.draw(screen)
     if self.selected_piece:
         self.draw_valid_moves(self.valid_moves)
     pygame.display.update()
 
 def winner(self):
     red_moves = any(self.board.get_valid_moves(piece) for piece in self.board.get_all_pieces(RED))
     blue_moves = any(self.board.get_valid_moves(piece) for piece in self.board.get_all_pieces(BLUE))
 
     if self.board.red_left <= 0 or not red_moves:
         return "BLUE"
     elif self.board.blue_left <= 0 or not blue_moves:
         return "RED"
 
     return None
 
 def computer_turn(self):
     # Get all possible moves for BLUE (AI)
     all_moves = get_all_moves(self.board, BLUE)
 
     # If no valid moves, skip turn or handle it appropriately
     if not all_moves:
         winner = self.winner()  # Check if there's a winner
         if winner:
             return  # The game is over, no need to continue.
 
         self.change_turn()  # AI skips its turn due to no valid moves
         return
 
     # If valid moves exist, proceed with minimax
     _, new_board = minimax(self.board, 3, True)  # depth of 3
     self.board = new_board
     self.change_turn()
 
 
# Minimax algorithm
def minimax(position, depth, max_player):
 if depth == 0 or position.winner() is not None:
     return position.evaluate(), position
 
 if max_player:
     max_eval = float('-inf')
     best_move = None
     for move in get_all_moves(position, BLUE):
         evaluation = minimax(move, depth - 1, False)[0]
         max_eval = max(max_eval, evaluation)
         if max_eval == evaluation:
             best_move = move
     return max_eval, best_move
 else:
     min_eval = float('inf')
     best_move = None
     for move in get_all_moves(position, RED):
         evaluation = minimax(move, depth - 1, True)[0]
         min_eval = min(min_eval, evaluation)
         if min_eval == evaluation:
             best_move = move
     return min_eval, best_move
 
def get_all_moves(board, color):
 moves = []
 for piece in board.get_all_pieces(color):
     valid_moves = board.get_valid_moves(piece)
     for move, skipped in valid_moves.items():
         temp_board = copy.deepcopy(board)
         temp_piece = temp_board.get_piece(piece.row, piece.col)
         temp_board.move(temp_piece, move[0], move[1])
 
         if skipped:
             temp_board.remove(skipped)  # Capture the skipped pieces
 
         moves.append(temp_board)
 
 return moves
 
# Main menu function
def main_menu():
 screen.fill(BLACK)
 font = pygame.font.Font(None, 60)
 text = font.render("Checkers - The Pycodes", True, WHITE)
 screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 150))
 
 play_pvp_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
 play_ai_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
 
 pygame.draw.rect(screen, RED, play_pvp_button)
 pygame.draw.rect(screen, BLUE, play_ai_button)
 
 pvp_text = font.render("Player vs Player", True, WHITE)
 ai_text = font.render("Player vs AI", True, WHITE)
 
 screen.blit(pvp_text, (play_pvp_button.x + 10, play_pvp_button.y + 5))
 screen.blit(ai_text, (play_ai_button.x + 20, play_ai_button.y + 5))
 
 pygame.display.update()
 
 while True:
     for event in pygame.event.get():
         if event.type == pygame.QUIT:
             pygame.quit()
             sys.exit()
         if event.type == pygame.MOUSEBUTTONDOWN:
             if play_pvp_button.collidepoint(event.pos):
                 return False  # Player vs Player mode
             if play_ai_button.collidepoint(event.pos):
                 return True  # Player vs Computer mode
 
def display_winner_screen(winner):
 screen.fill(BLACK)
 font = pygame.font.Font(None, 60)
 text = font.render(f"The winner is {winner}", True, WHITE)
 screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 150))
 
 # Create buttons
 main_menu_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
 quit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
 
 # Draw buttons
 pygame.draw.rect(screen, BLUE, main_menu_button)
 pygame.draw.rect(screen, RED, quit_button)
 
 # Button text
 menu_text = font.render("Main Menu", True, WHITE)
 quit_text = font.render("Quit", True, WHITE)
 
 screen.blit(menu_text, (main_menu_button.x + 10, main_menu_button.y + 5))
 screen.blit(quit_text, (quit_button.x + 60, quit_button.y + 5))
 
 pygame.display.update()
 
 while True:
     for event in pygame.event.get():
         if event.type == pygame.QUIT:
             pygame.quit()
             sys.exit()
 
         if event.type == pygame.MOUSEBUTTONDOWN:
             if main_menu_button.collidepoint(event.pos):
                 return "main_menu"
             if quit_button.collidepoint(event.pos):
                 pygame.quit()
                 sys.exit()
 
# Main function
def main():
 while True:
     is_computer = main_menu()  # Returns True if AI is chosen
     game = Game(is_computer)
     clock = pygame.time.Clock()
 
     while True:
         clock.tick(60)
         game.update()
 
         winner = game.winner()
         if winner:
             result = display_winner_screen(winner)
             if result == "main_menu":
                 break  # Return to the main menu loop
 
         for event in pygame.event.get():
             if event.type == pygame.QUIT:
                 pygame.quit()
                 sys.exit()
 
             if event.type == pygame.MOUSEBUTTONDOWN:
                 pos = pygame.mouse.get_pos()
                 row, col = pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE
                 game.select(row, col)
 
if __name__ == '__main__':
 main()
