"""
This file is responsible for handling user input and the GameState
"""

import pygame
import os

import ChessAI  # custom file
import ChessEngine  # custom file

pygame.init()
BOARD_WIDTH = BOARD_HEIGHT = 512
WELCOME_SCREEN_WIDTH = 300
WELCOME_SCREEN_HEIGHT = WELCOME_SCREEN_WIDTH // 2
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
FPS = 15
FONT = pygame.font.SysFont(pygame.font.get_default_font(), 20)
IMG = {}
# X, Y = 100, 100
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (100, 100)


def welcome():
    width = WELCOME_SCREEN_WIDTH
    height = WELCOME_SCREEN_HEIGHT

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Chess With Raj')   
    pygame.display.set_icon(pygame.image.load("assets/raj games icon.png"))
    screen.fill(pygame.Color("white"))
    clock = pygame.time.Clock()
    event_loop = True

    while event_loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                event_loop = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                location = pygame.mouse.get_pos()
                return 1 if location[0] < width//2 else 2

        clock.tick(FPS)
        pygame.display.flip()
        images = [pygame.transform.scale(pygame.image.load("assets/one_pawn.png"), (height, height)),
                  pygame.transform.scale(pygame.image.load("assets/two_pawn.png"), (height, height))]

        screen.blit(images[0], pygame.Rect(0, 0, height, height))
        screen.blit(images[1], pygame.Rect(height, 0, height, height))

    pygame.quit()
    return 0  # if user exited the window


def main(player_num):
    """
    handles user input and updating graphics
    :return: null
    """
    win = pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))
    pygame.display.set_caption('Chess With Raj', "assets/raj games icon.png")
    win.fill(pygame.Color("white"))

    game_state = ChessEngine.GameState(win)
    valid_moves = game_state.get_valid_moves

    load_images()
    clock = pygame.time.Clock()

    selected = ()
    player_clicks = []

    run = True
    move_made = False
    game_over = False
    player_one = True  # white Turn (human playing - True , com playing - false)
    player_two = False if player_num == 1 else True  # black Turn (human playing - True , com playing - false)
    capture_pieces = []
    # player_one, player_two = player_two, player_one

    while run:
        is_human_turn = (game_state.white_turn and player_one) or (not game_state.white_turn and player_two)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not game_over and is_human_turn:
                    location = pygame.mouse.get_pos()
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE
                    if selected == (row, col) or 0 > col >= 8:  # ensuring player clicks the board only
                        # deselecting
                        selected = ()
                        player_clicks = []
                    else:
                        # selecting [row][col]
                        selected = (row, col)
                        player_clicks.append(selected)
                    if len(player_clicks) == 2:  # when player clicks the second time making the move
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:  # ensuring that player selected a valid move
                                if game_state.board[valid_moves[i].end_row][valid_moves[i].end_col] != "--":
                                    capture_pieces.append(game_state.board[valid_moves[i].end_row][valid_moves[i].end_col])
                                game_state.make_move(valid_moves[i])
                                move_made = True
                                selected = ()
                                player_clicks = []
                        if not move_made:
                            player_clicks = [selected]
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    game_state.undo()
                    game_state.undo()
                    move_made = True
                    game_over = False
                if event.key == pygame.K_RETURN:
                    game_state = ChessEngine.GameState(win)
                    valid_moves = game_state.get_valid_moves
                    selected = ()
                    player_clicks = []
                    move_made = False
                    game_over = False

        if not game_over and not is_human_turn:
            # start_time = time.time()
            ai_move = ChessAI.find_move_nega_max_alpha_beta(game_state, valid_moves)
            # print(time.time() - start_time)
            if ai_move is None:
                ai_move = ChessAI.random_move(valid_moves)
            if game_state.board[ai_move.end_row][ai_move.end_col] != "--":
                capture_pieces.append(game_state.board[ai_move.end_row][ai_move.end_col])
            game_state.make_move(ai_move)
            move_made = True

        if move_made:
            valid_moves = game_state.get_valid_moves
            move_made = False

        draw(win, game_state, valid_moves, selected)

        game_over = game_state.check_mate or game_state.stale_mate
        if game_over:
            if game_state.white_turn:
                if game_state.check_mate:
                    draw_text(win, "Black Wins By Check Mate")
                else:
                    draw_text(win, 'Black Wins By Stale Mate')
            else:
                if game_state.check_mate:
                    draw_text(win, "White Wins By Check Mate")
                else:
                    draw_text(win, 'White Wins By Stale Mate')

        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()


def load_images():
    pieces = ["wP", "wB", "wR", "wN", "wQ", "wK", "bP", "bB", "bR", "bN", "bQ", "bK"]
    for piece in pieces:
        # C:/Users/Amit/PycharmProjects/Chess - - RajWebz/Chess/assets
        IMG[piece] = pygame.transform.scale(pygame.image.load("assets/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


def draw(win, game_state, valid_moves, square_selected):
    draw_square(win)
    highlight_square(win, game_state, valid_moves, square_selected)
    draw_piece(win, game_state)
    pygame.display.update()


def draw_square(win):
    colors_lis = [pygame.Color("white"), pygame.Color("grey")]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors_lis[((row + col) % 2)]
            pygame.draw.rect(win, color,
                             pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def highlight_square(win, game_state, valid_moves, square_selected):
    enemy_color = ('b' if game_state.white_turn else 'w')
    if square_selected != ():
        r, c = square_selected
        if game_state.board[r][c][0] != enemy_color:  # sq selected should same which turn it is
            surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))  # highlight selected square
            surface.set_alpha(150)  # transparency
            surface.fill((255, 255, 0))  # yellow
            win.blit(surface, (c * SQUARE_SIZE, r * SQUARE_SIZE))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    surface.fill((255, 0, 255))  # pink
                    win.blit(surface, (SQUARE_SIZE * move.end_col, SQUARE_SIZE * move.end_row))
                    if game_state.board[move.end_row][move.end_col][0] == enemy_color:
                        surface.fill((255, 0, 0))  # red
                        win.blit(surface, (SQUARE_SIZE * move.end_col, SQUARE_SIZE * move.end_row))


def draw_piece(win, game_state):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = game_state.board[row][col]
            if piece != "--":
                win.blit(IMG[piece],
                         pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_text(win, text):
    font = pygame.font.SysFont("helvetica", 35, True, False)
    text_object = font.render(text, True, pygame.Color('Black'))
    text_location = pygame.Rect(BOARD_WIDTH // 2 - text_object.get_width() // 2,
                                BOARD_HEIGHT // 2 - text_object.get_height() // 2,
                                text_object.get_width(), text_object.get_height())
    win.blit(text_object, text_location)
    pygame.display.update()


if __name__ == "__main__":
    players = welcome()
    if players > 0:  # main method does not invoke if player has exited welcome screen
        main(players)
