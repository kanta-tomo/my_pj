"""Run the Pygame toy chessboard."""

import pygame

from chess_display import (
    BACKGROUND,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    create_fonts,
    draw_board,
    history_panel_rect,
    load_piece_images,
    max_history_scroll,
    promotion_choice_at,
    screen_to_square,
)
from chess_game import ChessGame


def main() -> None:
    pygame.init()
    try:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Chess Board")
        game = ChessGame()
        fonts = create_fonts()
        piece_images = load_piece_images()
        flipped = False
        history_scroll = 0
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                    flipped = not flipped
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if game.pending_promotion is not None:
                        choice = promotion_choice_at(event.pos, game)
                        if choice is not None:
                            game.promote(choice)
                    else:
                        game.click_square(screen_to_square(event.pos, flipped))
                elif event.type == pygame.MOUSEWHEEL:
                    if history_panel_rect().collidepoint(pygame.mouse.get_pos()):
                        history_scroll = max(
                            0,
                            min(
                                max_history_scroll(len(game.move_history)),
                                history_scroll + event.y,
                            ),
                        )

            screen.fill(BACKGROUND)
            draw_board(screen, game, fonts, piece_images, flipped, history_scroll)
            pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
