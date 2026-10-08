import pygame


LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
BOARD_OUTLINE = (80, 80, 80)
HIGHLIGHT = (255, 215, 0)
SELECT_RING = (76, 175, 80)
MOVE_PANEL = (250, 245, 240)
TEXT_COLOR = (30, 30, 30)
BOARD_SIZE = 8
SQUARE_SIZE = 80
PADDING = 40
MOVE_PANEL_HEIGHT = 140
WINDOW_SIZE = BOARD_SIZE * SQUARE_SIZE + (PADDING * 2) + MOVE_PANEL_HEIGHT

PIECE_SYMBOLS = {
    "wP": "P",
    "wR": "R",
    "wN": "N",
    "wB": "B",
    "wQ": "Q",
    "wK": "K",
    "bP": "P",
    "bR": "R",
    "bN": "N",
    "bB": "B",
    "bQ": "Q",
    "bK": "K",
}


def create_initial_board():
    return [
        ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
        ["bP" for _ in range(8)],
        [None for _ in range(8)],
        [None for _ in range(8)],
        [None for _ in range(8)],
        [None for _ in range(8)],
        ["wP" for _ in range(8)],
        ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
    ]


def in_bounds(row, col):
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


def square_to_screen(row, col):
    x = PADDING + col * SQUARE_SIZE
    y = PADDING + row * SQUARE_SIZE
    return x, y


def is_valid_move(board, start, end):
    if start == end:
        return False

    start_row, start_col = start
    end_row, end_col = end
    if not in_bounds(start_row, start_col) or not in_bounds(end_row, end_col):
        return False

    piece = board[start_row][start_col]
    if piece is None:
        return False

    target = board[end_row][end_col]
    if target is not None and target[0] == piece[0]:
        return False

    return end in legal_moves(board, start)


def legal_moves(board, square):
    if square is None:
        return []

    row, col = square
    if not in_bounds(row, col):
        return []

    piece = board[row][col]
    if piece is None:
        return []

    color = piece[0]
    piece_type = piece[1]
    moves = []

    if piece_type == "P":
        direction = -1 if color == "w" else 1
        start_rank = 6 if color == "w" else 1
        forward_row = row + direction

        if in_bounds(forward_row, col) and board[forward_row][col] is None:
            moves.append((forward_row, col))
            double_row = row + (2 * direction)
            if row == start_rank and in_bounds(double_row, col) and board[double_row][col] is None:
                moves.append((double_row, col))

        for delta_col in (-1, 1):
            target_col = col + delta_col
            target_row = row + direction
            if in_bounds(target_row, target_col):
                target_piece = board[target_row][target_col]
                if target_piece is not None and target_piece[0] != color:
                    moves.append((target_row, target_col))

    elif piece_type == "N":
        for d_row, d_col in [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]:
            r = row + d_row
            c = col + d_col
            if in_bounds(r, c):
                target = board[r][c]
                if target is None or target[0] != color:
                    moves.append((r, c))

    elif piece_type in {"B", "R", "Q"}:
        directions = []
        if piece_type in {"B", "Q"}:
            directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
        if piece_type in {"R", "Q"}:
            directions.extend([(1, 0), (-1, 0), (0, 1), (0, -1)])

        for d_row, d_col in directions:
            r = row + d_row
            c = col + d_col
            while in_bounds(r, c):
                target = board[r][c]
                if target is None:
                    moves.append((r, c))
                else:
                    if target[0] != color:
                        moves.append((r, c))
                    break
                r += d_row
                c += d_col

    elif piece_type == "K":
        for d_row in (-1, 0, 1):
            for d_col in (-1, 0, 1):
                if d_row == 0 and d_col == 0:
                    continue
                r = row + d_row
                c = col + d_col
                if in_bounds(r, c):
                    target = board[r][c]
                    if target is None or target[0] != color:
                        moves.append((r, c))

    return moves


def board_to_notation(row, col):
    file_letter = chr(ord('a') + col)
    rank_number = 8 - row
    return f"{file_letter}{rank_number}"


def draw_board(screen, board, selected_square=None, legal_targets=None, turn_text="White to move", move_history=None):
    board_surface = pygame.Rect(PADDING, PADDING, BOARD_SIZE * SQUARE_SIZE, BOARD_SIZE * SQUARE_SIZE)
    pygame.draw.rect(screen, BOARD_OUTLINE, board_surface, 4)

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            x, y = square_to_screen(row, col)
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            rect = pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, color, rect)

            if selected_square is not None and selected_square == (row, col):
                pygame.draw.rect(screen, SELECT_RING, rect, 4)

            if legal_targets and (row, col) in legal_targets:
                center = (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2)
                pygame.draw.circle(screen, (120, 190, 120), center, 10)

            piece = board[row][col]
            if piece:
                symbol = PIECE_SYMBOLS[piece]
                center = (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2)
                is_white = piece[0] == "w"
                circle_color = (245, 245, 245) if is_white else (35, 35, 35)
                text_color = (25, 25, 25) if is_white else (245, 245, 245)

                pygame.draw.circle(screen, circle_color, center, 28)
                font = pygame.font.SysFont("Arial", 30, bold=True)
                text = font.render(symbol, True, text_color)
                text_rect = text.get_rect(center=center)
                screen.blit(text, text_rect)

    font = pygame.font.SysFont("Arial", 16)
    for index, letter in enumerate("abcdefgh"):
        label = font.render(letter, True, (40, 40, 40))
        screen.blit(label, (PADDING + index * SQUARE_SIZE + SQUARE_SIZE // 2 - 5, PADDING + BOARD_SIZE * SQUARE_SIZE + 8))

    for index, number in enumerate(reversed("12345678")):
        label = font.render(number, True, (40, 40, 40))
        screen.blit(label, (PADDING - 18, PADDING + index * SQUARE_SIZE + SQUARE_SIZE // 2 - 8))

    turn_font = pygame.font.SysFont("Arial", 22, bold=True)
    turn_label = turn_font.render(turn_text, True, TEXT_COLOR)
    screen.blit(turn_label, (PADDING, WINDOW_SIZE - MOVE_PANEL_HEIGHT + 10))

    move_panel = pygame.Rect(PADDING, WINDOW_SIZE - MOVE_PANEL_HEIGHT + 40, BOARD_SIZE * SQUARE_SIZE, MOVE_PANEL_HEIGHT - 55)
    pygame.draw.rect(screen, MOVE_PANEL, move_panel)
    pygame.draw.rect(screen, BOARD_OUTLINE, move_panel, 2)

    if move_history:
        history_font = pygame.font.SysFont("Arial", 16)
        for index, move in enumerate(move_history[-12:]):
            text = history_font.render(f"{index + 1}. {move}", True, TEXT_COLOR)
            screen.blit(text, (move_panel.x + 12, move_panel.y + 10 + index * 20))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Chess Board")

    board = create_initial_board()
    selected_square = None
    current_turn = "w"
    move_history = []

    running = True
    while running:
        legal_targets = legal_moves(board, selected_square) if selected_square else []
        turn_text = "White to move" if current_turn == "w" else "Black to move"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if not (PADDING <= mouse_x <= PADDING + BOARD_SIZE * SQUARE_SIZE and PADDING <= mouse_y <= PADDING + BOARD_SIZE * SQUARE_SIZE):
                    continue

                row = (mouse_y - PADDING) // SQUARE_SIZE
                col = (mouse_x - PADDING) // SQUARE_SIZE
                clicked_piece = board[row][col]

                if selected_square is None:
                    if clicked_piece and clicked_piece[0] == current_turn:
                        selected_square = (row, col)
                else:
                    start_row, start_col = selected_square
                    if (row, col) == selected_square:
                        selected_square = None
                    elif clicked_piece and clicked_piece[0] == current_turn:
                        selected_square = (row, col)
                    elif (row, col) in legal_targets:
                        start = board[start_row][start_col]
                        board[row][col] = start
                        board[start_row][start_col] = None
                        move_history.append(f"{PIECE_SYMBOLS[start]} {board_to_notation(start_row, start_col)} -> {board_to_notation(row, col)}")
                        selected_square = None
                        current_turn = "b" if current_turn == "w" else "w"

        if not running:
            break

        screen.fill((245, 245, 245))
        draw_board(screen, board, selected_square, legal_targets, turn_text, move_history)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
