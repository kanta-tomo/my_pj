"""Pygame rendering and screen-coordinate helpers for the toy chessboard."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pygame

from chess_game import BOARD_SIZE, ChessGame, Square


# Window layout
SQUARE_SIZE = 80
PADDING = 40
BOARD_PIXELS = BOARD_SIZE * SQUARE_SIZE
HISTORY_GAP = 36
HISTORY_PANEL_WIDTH = 300
HISTORY_ROW_HEIGHT = 24
HISTORY_HEADER_HEIGHT = 58
WINDOW_WIDTH = PADDING * 2 + BOARD_PIXELS + HISTORY_GAP + HISTORY_PANEL_WIDTH
WINDOW_HEIGHT = PADDING * 2 + BOARD_PIXELS

# Colors
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
BOARD_OUTLINE = (80, 80, 80)
SELECT_RING = (76, 175, 80)
LEGAL_MOVE_COLOR = (120, 190, 120)
MOVE_PANEL = (250, 245, 240)
TEXT_COLOR = (30, 30, 30)
BACKGROUND = (245, 245, 245)
FILES = "abcdefgh"
RANKS = "87654321"
PIECE_ASSET_NAMES = {
    "P": "pawn",
    "R": "rook",
    "N": "knight",
    "B": "bishop",
    "Q": "queen",
    "K": "king",
}
PIECE_SIZE = (60, 76)
PROMOTION_TYPES = ("Q", "R", "B", "N")
PROMOTION_PANEL_SIZE = (360, 144)
PROMOTION_BUTTON_SIZE = (64, 80)
PROMOTION_BUTTON_GAP = 12


@dataclass
class Fonts:
    """Cached fonts used by the renderer."""

    label: pygame.font.Font
    turn: pygame.font.Font
    history: pygame.font.Font


def create_fonts() -> Fonts:
    """Create renderer fonts after Pygame has initialized."""
    return Fonts(
        label=pygame.font.SysFont("Arial", 16),
        turn=pygame.font.SysFont("Arial", 22, bold=True),
        history=pygame.font.SysFont("Arial", 16),
    )


def load_piece_images() -> dict[str, pygame.Surface]:
    """Load and scale the bundled piece images once at startup."""
    asset_directory = Path(__file__).parent / "assets" / "pieces"
    images = {}
    for color_code, color_name in (("w", "white"), ("b", "black")):
        for piece_code, piece_name in PIECE_ASSET_NAMES.items():
            piece = f"{color_code}{piece_code}"
            image_path = asset_directory / f"{color_name}-{piece_name}.png"
            image = pygame.image.load(str(image_path)).convert_alpha()
            images[piece] = pygame.transform.smoothscale(image, PIECE_SIZE)
    return images


def history_panel_rect() -> pygame.Rect:
    return pygame.Rect(PADDING + BOARD_PIXELS + HISTORY_GAP, PADDING,
                       HISTORY_PANEL_WIDTH, BOARD_PIXELS)


def history_visible_rows() -> int:
    return (BOARD_PIXELS - HISTORY_HEADER_HEIGHT - 16) // HISTORY_ROW_HEIGHT


def max_history_scroll(move_count: int) -> int:
    total_rows = (move_count + 1) // 2
    return max(0, total_rows - history_visible_rows())


def _display_to_board_square(row: int, col: int, flipped: bool) -> Square:
    if flipped:
        return BOARD_SIZE - 1 - row, BOARD_SIZE - 1 - col
    return row, col


def screen_to_square(position: tuple[int, int], flipped: bool = False) -> Square | None:
    """Convert a pixel coordinate to a logical board square."""
    x, y = position
    board_rect = pygame.Rect(PADDING, PADDING, BOARD_PIXELS, BOARD_PIXELS)
    if not board_rect.collidepoint(position):
        return None
    display_row = (y - PADDING) // SQUARE_SIZE
    display_col = (x - PADDING) // SQUARE_SIZE
    return _display_to_board_square(display_row, display_col, flipped)


def square_to_screen(square: Square, flipped: bool = False) -> tuple[int, int]:
    row, col = square
    if flipped:
        row = BOARD_SIZE - 1 - row
        col = BOARD_SIZE - 1 - col
    return PADDING + col * SQUARE_SIZE, PADDING + row * SQUARE_SIZE


def _promotion_layout() -> tuple[pygame.Rect, dict[str, pygame.Rect]]:
    width, height = PROMOTION_PANEL_SIZE
    panel = pygame.Rect(
        PADDING + (BOARD_PIXELS - width) // 2,
        PADDING + (BOARD_PIXELS - height) // 2,
        width,
        height,
    )
    button_width, button_height = PROMOTION_BUTTON_SIZE
    row_width = len(PROMOTION_TYPES) * button_width + (len(PROMOTION_TYPES) - 1) * PROMOTION_BUTTON_GAP
    first_x = panel.x + (panel.width - row_width) // 2
    button_y = panel.y + 50
    buttons = {
        piece_type: pygame.Rect(
            first_x + index * (button_width + PROMOTION_BUTTON_GAP),
            button_y,
            button_width,
            button_height,
        )
        for index, piece_type in enumerate(PROMOTION_TYPES)
    }
    return panel, buttons


def promotion_choice_at(position: tuple[int, int], game: ChessGame) -> str | None:
    """Return the selected promotion piece, if the click hit a choice button."""
    if game.pending_promotion is None:
        return None
    _, buttons = _promotion_layout()
    for piece_type, button in buttons.items():
        if button.collidepoint(position):
            return piece_type
    return None


def _draw_promotion_picker(
    screen: pygame.Surface,
    game: ChessGame,
    fonts: Fonts,
    piece_images: dict[str, pygame.Surface],
) -> None:
    if game.pending_promotion is None:
        return

    overlay = pygame.Surface((BOARD_PIXELS, BOARD_PIXELS), pygame.SRCALPHA)
    overlay.fill((15, 18, 24, 145))
    screen.blit(overlay, (PADDING, PADDING))

    panel, buttons = _promotion_layout()
    pygame.draw.rect(screen, MOVE_PANEL, panel, border_radius=8)
    pygame.draw.rect(screen, BOARD_OUTLINE, panel, 2, border_radius=8)
    title = fonts.turn.render("Choose a promotion", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(midtop=(panel.centerx, panel.y + 10)))

    _, destination = game.pending_promotion
    pawn = game.board[destination[0]][destination[1]]
    color = pawn[0]
    for piece_type, button in buttons.items():
        pygame.draw.rect(screen, (255, 255, 255), button, border_radius=4)
        pygame.draw.rect(screen, BOARD_OUTLINE, button, 1, border_radius=4)
        image = piece_images[f"{color}{piece_type}"]
        screen.blit(image, image.get_rect(center=button.center))


def _draw_history(
    screen: pygame.Surface,
    game: ChessGame,
    fonts: Fonts,
    scroll_offset: int,
) -> None:
    panel = history_panel_rect()
    pygame.draw.rect(screen, MOVE_PANEL, panel)
    pygame.draw.rect(screen, BOARD_OUTLINE, panel, 2)

    title = fonts.turn.render("Move history", True, TEXT_COLOR)
    screen.blit(title, (panel.x + 12, panel.y + 10))
    hint = fonts.label.render("F: flip board", True, TEXT_COLOR)
    screen.blit(hint, (panel.x + 12, panel.y + 36))

    total_rows = (len(game.move_history) + 1) // 2
    if total_rows == 0:
        empty_label = fonts.history.render("No moves yet", True, TEXT_COLOR)
        screen.blit(empty_label, (panel.x + 12, panel.y + HISTORY_HEADER_HEIGHT))
        return

    visible_rows = history_visible_rows()
    end_row = max(0, total_rows - scroll_offset)
    start_row = max(0, end_row - visible_rows)
    content_rect = pygame.Rect(
        panel.x + 8,
        panel.y + HISTORY_HEADER_HEIGHT,
        panel.width - 16,
        panel.height - HISTORY_HEADER_HEIGHT - 8,
    )
    old_clip = screen.get_clip()
    screen.set_clip(content_rect)
    for row, zero_based_number in enumerate(range(start_row, end_row)):
        white_index = zero_based_number * 2
        white_move = game.move_history[white_index]
        black_index = white_index + 1
        black_move = game.move_history[black_index] if black_index < len(game.move_history) else ""
        move_text = f"{zero_based_number + 1}. {white_move} {black_move}".rstrip()
        label = fonts.history.render(move_text, True, TEXT_COLOR)
        screen.blit(label, (content_rect.x + 4,
                            content_rect.y + row * HISTORY_ROW_HEIGHT - 2))
    screen.set_clip(old_clip)

    if total_rows > visible_rows:
        scrollbar = pygame.Rect(panel.right - 9, content_rect.y, 4, content_rect.height)
        pygame.draw.rect(screen, (220, 215, 205), scrollbar)
        thumb_height = max(24, content_rect.height * visible_rows // total_rows)
        max_scroll = total_rows - visible_rows
        thumb_offset = (content_rect.height - thumb_height) * scroll_offset // max_scroll
        thumb = pygame.Rect(scrollbar.x, scrollbar.y + thumb_offset,
                            scrollbar.width, thumb_height)
        pygame.draw.rect(screen, (130, 125, 115), thumb, border_radius=2)


def draw_board(
    screen: pygame.Surface,
    game: ChessGame,
    fonts: Fonts,
    piece_images: dict[str, pygame.Surface],
    flipped: bool = False,
    history_scroll: int = 0,
) -> None:
    """Render the board, piece images, turn, and scrollable move history."""
    legal_targets = set(game.legal_targets)
    for display_row in range(BOARD_SIZE):
        for display_col in range(BOARD_SIZE):
            square = _display_to_board_square(display_row, display_col, flipped)
            x = PADDING + display_col * SQUARE_SIZE
            y = PADDING + display_row * SQUARE_SIZE
            rect = pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE)
            color = LIGHT_SQUARE if (display_row + display_col) % 2 == 0 else DARK_SQUARE
            pygame.draw.rect(screen, color, rect)

            if square == game.selected_square:
                pygame.draw.rect(screen, SELECT_RING, rect, 4)
            if square in legal_targets:
                pygame.draw.circle(screen, LEGAL_MOVE_COLOR, rect.center, 10)

            piece = game.board[square[0]][square[1]]
            if piece:
                image = piece_images[piece]
                screen.blit(image, image.get_rect(center=rect.center))

    board_rect = pygame.Rect(PADDING, PADDING, BOARD_PIXELS, BOARD_PIXELS)
    pygame.draw.rect(screen, BOARD_OUTLINE, board_rect, 4)
    file_labels = FILES[::-1] if flipped else FILES
    rank_labels = RANKS[::-1] if flipped else RANKS
    for col, letter in enumerate(file_labels):
        label = fonts.label.render(letter, True, (40, 40, 40))
        screen.blit(label, (PADDING + col * SQUARE_SIZE + SQUARE_SIZE // 2 - 5,
                            PADDING + BOARD_PIXELS + 8))
    for row, number in enumerate(rank_labels):
        label = fonts.label.render(number, True, (40, 40, 40))
        screen.blit(label, (PADDING - 18, PADDING + row * SQUARE_SIZE + SQUARE_SIZE // 2 - 8))

    turn_label = fonts.turn.render(game.turn_text, True, TEXT_COLOR)
    screen.blit(turn_label, (PADDING, 8))
    _draw_history(screen, game, fonts, history_scroll)
    _draw_promotion_picker(screen, game, fonts, piece_images)
