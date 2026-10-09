# Toy Chessboard

A small chessboard demo built with Pygame. It lets two players move pieces by
clicking squares and shows legal destinations and a scrollable move history.
This is a learning project, not a complete chess implementation.

## Run

Use Python 3.9 or newer. Install Pygame if it is not already available:

```sh
python3 -m pip install pygame
```

From this directory, start the game with:

```sh
python3 toy_chessboard.py
```

Click one of the current player's pieces to select it, then click a highlighted
destination to move it. Click the selected piece again to cancel the selection.
Press `F` to flip the board to the other player's perspective. Use the
`Previous` and `Next` buttons, or the left and right arrow keys, to replay
positions without changing the current game. Click `Take back` to undo the
latest completed move and restore the position before it, even while replaying
an earlier position. Clicking the board returns to the current position.
Scroll over the move history panel to browse earlier moves. Close the window to
quit.

## Project layout

- `toy_chessboard.py` starts Pygame and runs the event loop.
- `chess_game.py` owns the board, turns, move history, and piece movement rules.
- `chess_display.py` draws the board and translates mouse coordinates into
  board squares.
- `assets/pieces/` contains the bundled piece images and their license.

The game logic module does not depend on Pygame. Keep new rules and game state
in `chess_game.py`; keep screen layout, colors, fonts, and drawing in
`chess_display.py`. Keep `toy_chessboard.py` focused on startup and connecting
input to the game and display.

## Scope and conventions

- This toy handles basic piece movement and captures, and prevents capturing a
  king. It enforces check by rejecting moves that leave the moving player's
  king under attack. It supports castling when the usual rights and path
  conditions remain, but does not detect checkmate or implement en passant.
  When a pawn reaches the last rank, choose a queen, rook, bishop, or knight
  from the promotion picker.
- Move history uses algebraic notation: for example, `e4`, `Nf3`, `Bxe6`, and
  `e8=Q`, `O-O`, and `O-O-O`. It adds `+` when a move attacks the opposing
  king; it does not add `#` for checkmate.
- Use `(row, column)` tuples for board coordinates. Row `0` is rank 8, and
  column `0` is file `a`.
- Piece codes use a lowercase color followed by an uppercase piece letter:
  `wP` is a white pawn and `bK` is a black king. Empty squares are `None`.
- Keep board dimensions and display layout values as named constants rather
  than scattering literal sizes through the code.
- Add type hints to new functions and keep the code compatible with Python 3.9.
- Avoid importing Pygame in `chess_game.py`, so game rules can be used without
  opening a window.

## Piece artwork

The 2D Chessnut piece artwork is by Alexis Luengas, from
[chessnut-pieces](https://github.com/LexLuengas/chessnut-pieces). The SVGs are
bundled as transparent PNGs for Pygame. The artwork is provided under the
Apache License 2.0; its license and copyright notice are in `assets/pieces/`.
