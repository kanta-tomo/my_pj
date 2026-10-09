"""Run the Pygame toy chessboard."""

import pygame

from chess_display import (
    BACKGROUND,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    create_fonts,
    draw_board,
    history_panel_rect,
    history_navigation_at,
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
        replay_ply = None
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                    flipped = not flipped
                elif event.type == pygame.KEYDOWN and event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    latest_position = len(game.position_history) - 1
                    current_position = latest_position if replay_ply is None else replay_ply
                    direction = -1 if event.key == pygame.K_LEFT else 1
                    next_position = max(0, min(latest_position, current_position + direction))
                    replay_ply = None if next_position == latest_position else next_position
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    navigation = history_navigation_at(event.pos)
                    if navigation is not None:
                        if navigation == "take_back":
                            latest_position = len(game.position_history) - 1
                            if latest_position > 0:
                                game.take_back_to_position(latest_position - 1)
                            replay_ply = None
                            history_scroll = min(
                                history_scroll,
                                max_history_scroll(len(game.move_history)),
                            )
                        else:
                            latest_position = len(game.position_history) - 1
                            current_position = latest_position if replay_ply is None else replay_ply
                            direction = -1 if navigation == "back" else 1
                            next_position = max(0, min(latest_position, current_position + direction))
                            replay_ply = None if next_position == latest_position else next_position
                    elif replay_ply is not None:
                        if screen_to_square(event.pos, flipped) is not None:
                            replay_ply = None
                    elif game.pending_promotion is not None:
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
            draw_board(screen, game, fonts, piece_images, flipped, history_scroll, replay_ply)
            pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
