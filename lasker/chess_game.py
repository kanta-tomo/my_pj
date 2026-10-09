"""Chess piece movement and game state for the toy chessboard."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


BOARD_SIZE = 8
FILES = "abcdefgh"
KNIGHT_OFFSETS = (
    (1, 2), (2, 1), (2, -1), (1, -2),
    (-1, -2), (-2, -1), (-2, 1), (-1, 2),
)
DIAGONAL_DIRECTIONS = ((1, 1), (1, -1), (-1, 1), (-1, -1))
STRAIGHT_DIRECTIONS = ((1, 0), (-1, 0), (0, 1), (0, -1))

PIECE_SYMBOLS = {
    f"{color}{piece_type}": piece_type
    for color in "wb"
    for piece_type in "PRNBQK"
}

Square = tuple[int, int]
Board = list[list[Optional[str]]]
PromotionMove = tuple[Square, Square, str]


def create_initial_board() -> Board:
    """Return a fresh board in the standard starting position."""
    back_rank = list("RNBQKBNR")
    return [
        [f"b{piece}" for piece in back_rank],
        ["bP"] * BOARD_SIZE,
        *([[None] * BOARD_SIZE for _ in range(4)]),
        ["wP"] * BOARD_SIZE,
        [f"w{piece}" for piece in back_rank],
    ]


def in_bounds(row: int, col: int) -> bool:
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


def board_to_notation(square: Square) -> str:
    row, col = square
    return f"{FILES[col]}{BOARD_SIZE - row}"


def _add_if_available(board: Board, moves: list[Square], square: Square, color: str) -> None:
    row, col = square
    if in_bounds(row, col):
        target = board[row][col]
        if target is None or (target[0] != color and target[1] != "K"):
            moves.append(square)


def _sliding_moves(board: Board, square: Square, directions: tuple[Square, ...]) -> list[Square]:
    row, col = square
    piece = board[row][col]
    if piece is None:
        return []

    moves = []
    for d_row, d_col in directions:
        target_row, target_col = row + d_row, col + d_col
        while in_bounds(target_row, target_col):
            target = board[target_row][target_col]
            if target is None:
                moves.append((target_row, target_col))
            else:
                if target[0] != piece[0] and target[1] != "K":
                    moves.append((target_row, target_col))
                break
            target_row += d_row
            target_col += d_col
    return moves


def legal_moves(board: Board, square: Optional[Square]) -> list[Square]:
    """Return moves allowed by the toy's piece movement rules.

    Check, castling, and en passant are intentionally not modeled. A pawn
    reaching the last rank waits for the player to choose its promotion piece.
    """
    if square is None:
        return []
    row, col = square
    if not in_bounds(row, col):
        return []

    piece = board[row][col]
    if piece is None:
        return []

    color, piece_type = piece
    if piece_type == "P":
        direction = -1 if color == "w" else 1
        start_rank = 6 if color == "w" else 1
        moves = []
        one_step = (row + direction, col)
        if in_bounds(*one_step) and board[one_step[0]][one_step[1]] is None:
            moves.append(one_step)
            two_step = (row + 2 * direction, col)
            if row == start_rank and board[two_step[0]][two_step[1]] is None:
                moves.append(two_step)
        for delta_col in (-1, 1):
            target = (row + direction, col + delta_col)
            if in_bounds(*target):
                occupant = board[target[0]][target[1]]
                if (
                    occupant is not None
                    and occupant[0] != color
                    and occupant[1] != "K"
                ):
                    moves.append(target)
        return moves

    if piece_type == "N":
        moves = []
        for d_row, d_col in KNIGHT_OFFSETS:
            _add_if_available(board, moves, (row + d_row, col + d_col), color)
        return moves
    if piece_type == "B":
        return _sliding_moves(board, square, DIAGONAL_DIRECTIONS)
    if piece_type == "R":
        return _sliding_moves(board, square, STRAIGHT_DIRECTIONS)
    if piece_type == "Q":
        return _sliding_moves(board, square, DIAGONAL_DIRECTIONS + STRAIGHT_DIRECTIONS)
    if piece_type == "K":
        moves = []
        for d_row in (-1, 0, 1):
            for d_col in (-1, 0, 1):
                if d_row or d_col:
                    _add_if_available(board, moves, (row + d_row, col + d_col), color)
        return moves
    return []


def move_to_san(board: Board, start: Square, end: Square) -> str:
    """Format a move in algebraic notation for the rules this toy supports."""
    start_row, start_col = start
    piece = board[start_row][start_col]
    if piece is None:
        raise ValueError("Cannot format a move from an empty square")

    piece_type = piece[1]
    is_capture = board[end[0]][end[1]] is not None
    destination = board_to_notation(end)

    if piece_type == "P":
        prefix = FILES[start_col] if is_capture else ""
    else:
        prefix = PIECE_SYMBOLS[piece]
        competitors = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                candidate_square = (row, col)
                candidate = board[row][col]
                if (
                    candidate_square != start
                    and candidate is not None
                    and candidate[0] == piece[0]
                    and candidate[1] == piece_type
                    and end in legal_moves(board, candidate_square)
                ):
                    competitors.append(candidate_square)

        if competitors:
            same_file = any(col == start_col for _, col in competitors)
            same_rank = any(row == start_row for row, _ in competitors)
            if not same_file:
                prefix += FILES[start_col]
            elif not same_rank:
                prefix += str(BOARD_SIZE - start_row)
            else:
                prefix += f"{FILES[start_col]}{BOARD_SIZE - start_row}"

    capture_marker = "x" if is_capture else ""
    return f"{prefix}{capture_marker}{destination}"


def _piece_attacks_square(board: Board, start: Square, target: Square) -> bool:
    """Check piece geometry and intervening blockers, without capture rules."""
    start_row, start_col = start
    target_row, target_col = target
    piece = board[start_row][start_col]
    if piece is None:
        return False

    row_delta = target_row - start_row
    col_delta = target_col - start_col
    abs_row, abs_col = abs(row_delta), abs(col_delta)
    piece_type = piece[1]

    if piece_type == "P":
        direction = -1 if piece[0] == "w" else 1
        return row_delta == direction and abs_col == 1
    if piece_type == "N":
        return (abs_row, abs_col) in {(1, 2), (2, 1)}
    if piece_type == "K":
        return max(abs_row, abs_col) == 1
    if piece_type == "B" and abs_row != abs_col:
        return False
    if piece_type == "R" and row_delta != 0 and col_delta != 0:
        return False
    if piece_type not in {"B", "R", "Q"}:
        return False
    if row_delta == 0 and col_delta == 0:
        return False
    if row_delta != 0 and col_delta != 0 and abs_row != abs_col:
        return False

    step_row = (row_delta > 0) - (row_delta < 0)
    step_col = (col_delta > 0) - (col_delta < 0)
    row, col = start_row + step_row, start_col + step_col
    while (row, col) != target:
        if board[row][col] is not None:
            return False
        row += step_row
        col += step_col
    return True


def is_king_in_check(board: Board, color: str) -> bool:
    """Return whether the given color's king is attacked on the current board."""
    king_square = None
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == f"{color}K":
                king_square = (row, col)
                break
        if king_square is not None:
            break
    if king_square is None:
        return False

    opponent = "b" if color == "w" else "w"
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece is not None and piece[0] == opponent:
                if _piece_attacks_square(board, (row, col), king_square):
                    return True
    return False


def is_valid_move(board: Board, start: Square, end: Square) -> bool:
    """Return whether a piece can move between two squares under toy rules."""
    if start == end or not in_bounds(*start) or not in_bounds(*end):
        return False
    return end in legal_moves(board, start)


@dataclass
class ChessGame:
    """Mutable game state and the rules for selecting and moving pieces."""

    board: Board = field(default_factory=create_initial_board)
    current_turn: str = "w"
    selected_square: Optional[Square] = None
    move_history: list[str] = field(default_factory=list)
    pending_promotion: Optional[PromotionMove] = None

    @property
    def legal_targets(self) -> list[Square]:
        return legal_moves(self.board, self.selected_square)

    @property
    def turn_text(self) -> str:
        return "White to move" if self.current_turn == "w" else "Black to move"

    def click_square(self, square: Optional[Square]) -> None:
        """Select a friendly piece or make a legal move to the clicked square."""
        if self.pending_promotion is not None or square is None or not in_bounds(*square):
            return
        row, col = square
        clicked_piece = self.board[row][col]

        if self.selected_square is None:
            if clicked_piece and clicked_piece[0] == self.current_turn:
                self.selected_square = square
            return
        if square == self.selected_square:
            self.selected_square = None
            return
        if clicked_piece and clicked_piece[0] == self.current_turn:
            self.selected_square = square
            return
        if not is_valid_move(self.board, self.selected_square, square):
            return

        start = self.selected_square
        piece = self.board[start[0]][start[1]]
        san = move_to_san(self.board, start, square)
        self.board[row][col] = piece
        self.board[start[0]][start[1]] = None
        reaches_last_rank = (
            piece == "wP" and row == 0
        ) or (
            piece == "bP" and row == BOARD_SIZE - 1
        )
        if reaches_last_rank:
            self.pending_promotion = (start, square, san)
            self.selected_square = None
            return

        opponent = "b" if piece[0] == "w" else "w"
        check_suffix = "+" if is_king_in_check(self.board, opponent) else ""
        self.move_history.append(f"{san}{check_suffix}")
        self.selected_square = None
        self.current_turn = "b" if self.current_turn == "w" else "w"

    def promote(self, piece_type: str) -> bool:
        """Complete a pending pawn promotion to queen, rook, bishop, or knight."""
        if piece_type not in {"Q", "R", "B", "N"} or self.pending_promotion is None:
            return False

        start, destination, san = self.pending_promotion
        row, col = destination
        pawn = self.board[row][col]
        if pawn not in {"wP", "bP"}:
            return False

        self.board[row][col] = f"{pawn[0]}{piece_type}"
        opponent = "b" if pawn[0] == "w" else "w"
        check_suffix = "+" if is_king_in_check(self.board, opponent) else ""
        self.move_history.append(f"{san}={piece_type}{check_suffix}")
        self.pending_promotion = None
        self.current_turn = "b" if self.current_turn == "w" else "w"
        return True
