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

## Browser version

The game also has a browser interface. From this directory, start a local web
server:

```sh
python3 -m http.server 8000
```

Then open [http://localhost:8000/web/](http://localhost:8000/web/) in your
browser. Stop the server with `Ctrl+C` in the terminal.

Click one of the current player's pieces to select it, then click a highlighted
destination to move it. Click the selected piece again to cancel the selection.
Press `F` to flip the board to the other player's perspective. Use the
`Previous` and `Next` buttons, or the left and right arrow keys, to replay
positions without changing the current game. `Take back` undoes the latest
completed move and restores the position before it, even while replaying an
earlier position. Clicking the board during replay returns to the current
position. Scroll over the move history panel to browse earlier moves. Close the
window to quit.

## Project layout

- `toy_chessboard.py` starts Pygame and runs the event loop.
- `chess_game.py` owns the board, turns, move history, and piece movement rules.
- `chess_display.py` draws the board and translates mouse coordinates into
  board squares.
- `web/` contains a static browser version. Its `app.js` implements the same
  toy rules for play without Pygame.
- `assets/pieces-basic-png/` contains the piece images used by both interfaces.
- `assets/pieces/` contains the previous piece set and its license.

The game logic module does not depend on Pygame. Keep new rules and game state
in `chess_game.py`; keep screen layout, colors, fonts, and drawing in
`chess_display.py`. Keep `toy_chessboard.py` focused on startup and connecting
input to the game and display.
When changing game rules, keep `web/app.js` in sync with `chess_game.py`.

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

The active images are transparent 128×128 PNGs in `assets/pieces-basic-png/`.
They come from [Green Chess's downloads page](https://greenchess.net/info.php?item=downloads),
which says the standard chess pieces are based on Wikipedia images, slightly
modified, and requires attribution and share-alike under
[CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/). The attribution
notice is also included in `assets/pieces-basic-png/COPYRIGHT.txt`. The previous
2D Chessnut set by Alexis Luengas remains in `assets/pieces/`, with its Apache
License 2.0 and copyright notice.
