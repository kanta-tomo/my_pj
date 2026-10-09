"use strict";

const SIZE = 8;
const FILES = "abcdefgh";
const ASSET_NAMES = { P: "pawn", R: "rook", N: "knight", B: "bishop", Q: "queen", K: "king" };
const PROMOTION_TYPES = ["Q", "R", "B", "N"];
const boardElement = document.querySelector("#board");
const statusElement = document.querySelector("#game-status");
const historyElement = document.querySelector("#move-list");
const countElement = document.querySelector("#history-count");
const promotionDialog = document.querySelector("#promotion-dialog");
const promotionOptions = document.querySelector("#promotion-options");

function initialBoard() {
  const backRank = ["R", "N", "B", "Q", "K", "B", "N", "R"];
  return [
    backRank.map((piece) => `b${piece}`),
    Array(SIZE).fill("bP"),
    ...Array.from({ length: 4 }, () => Array(SIZE).fill(null)),
    Array(SIZE).fill("wP"),
    backRank.map((piece) => `w${piece}`),
  ];
}

const game = {
  board: initialBoard(),
  turn: "w",
  selected: null,
  moveHistory: [],
  positions: [],
  castlingRights: new Set(["wK", "wQ", "bK", "bQ"]),
  pendingPromotion: null,
  replayIndex: null,
  flipped: false,
};

function copyBoard(board) { return board.map((rank) => rank.slice()); }

function savePosition() {
  game.positions.push({
    board: copyBoard(game.board),
    turn: game.turn,
    castlingRights: new Set(game.castlingRights),
  });
}

function restorePosition(positionIndex) {
  const position = game.positions[positionIndex];
  game.board = copyBoard(position.board);
  game.turn = position.turn;
  game.castlingRights = new Set(position.castlingRights);
  game.moveHistory = game.moveHistory.slice(0, positionIndex);
  game.positions = game.positions.slice(0, positionIndex + 1);
  game.selected = null;
  game.pendingPromotion = null;
  game.replayIndex = null;
}

savePosition();

function inside(row, col) { return row >= 0 && row < SIZE && col >= 0 && col < SIZE; }
function sameSquare(a, b) { return a && b && a[0] === b[0] && a[1] === b[1]; }
function squareName([row, col]) { return `${FILES[col]}${SIZE - row}`; }

function addIfAvailable(board, moves, square, color) {
  const [row, col] = square;
  if (!inside(row, col)) return;
  const target = board[row][col];
  if (!target || (target[0] !== color && target[1] !== "K")) moves.push(square);
}

function slidingMoves(board, [row, col], directions) {
  const piece = board[row][col];
  if (!piece) return [];
  const moves = [];
  for (const [dr, dc] of directions) {
    let r = row + dr;
    let c = col + dc;
    while (inside(r, c)) {
      const target = board[r][c];
      if (!target) moves.push([r, c]);
      else {
        if (target[0] !== piece[0] && target[1] !== "K") moves.push([r, c]);
        break;
      }
      r += dr;
      c += dc;
    }
  }
  return moves;
}

function pseudoMoves(board, square, rights = game.castlingRights) {
  if (!square) return [];
  const [row, col] = square;
  if (!inside(row, col)) return [];
  const piece = board[row][col];
  if (!piece) return [];
  const [color, type] = piece;

  if (type === "P") {
    const direction = color === "w" ? -1 : 1;
    const startRank = color === "w" ? 6 : 1;
    const moves = [];
    const one = [row + direction, col];
    if (inside(...one) && !board[one[0]][one[1]]) {
      moves.push(one);
      const two = [row + direction * 2, col];
      if (row === startRank && !board[two[0]][two[1]]) moves.push(two);
    }
    for (const dc of [-1, 1]) {
      const target = [row + direction, col + dc];
      if (!inside(...target)) continue;
      const occupant = board[target[0]][target[1]];
      if (occupant && occupant[0] !== color && occupant[1] !== "K") moves.push(target);
    }
    return moves;
  }
  if (type === "N") {
    const moves = [];
    for (const [dr, dc] of [[1, 2], [2, 1], [2, -1], [1, -2], [-1, -2], [-2, -1], [-2, 1], [-1, 2]]) {
      addIfAvailable(board, moves, [row + dr, col + dc], color);
    }
    return moves;
  }
  if (type === "B") return slidingMoves(board, square, [[1, 1], [1, -1], [-1, 1], [-1, -1]]);
  if (type === "R") return slidingMoves(board, square, [[1, 0], [-1, 0], [0, 1], [0, -1]]);
  if (type === "Q") return slidingMoves(board, square, [[1, 1], [1, -1], [-1, 1], [-1, -1], [1, 0], [-1, 0], [0, 1], [0, -1]]);
  if (type === "K") {
    const moves = [];
    for (let dr = -1; dr <= 1; dr += 1) {
      for (let dc = -1; dc <= 1; dc += 1) {
        if (dr || dc) addIfAvailable(board, moves, [row + dr, col + dc], color);
      }
    }
    const homeRow = color === "w" ? 7 : 0;
    if (row === homeRow && col === 4) {
      if (rights.has(`${color}K`) && board[homeRow][7] === `${color}R` && !board[homeRow][5] && !board[homeRow][6]) moves.push([homeRow, 6]);
      if (rights.has(`${color}Q`) && board[homeRow][0] === `${color}R` && !board[homeRow][1] && !board[homeRow][2] && !board[homeRow][3]) moves.push([homeRow, 2]);
    }
    return moves;
  }
  return [];
}

function pieceAttacks(board, start, target) {
  const [r1, c1] = start;
  const [r2, c2] = target;
  const piece = board[r1][c1];
  if (!piece) return false;
  const dr = r2 - r1;
  const dc = c2 - c1;
  const ar = Math.abs(dr);
  const ac = Math.abs(dc);
  const type = piece[1];
  if (type === "P") return dr === (piece[0] === "w" ? -1 : 1) && ac === 1;
  if (type === "N") return (ar === 1 && ac === 2) || (ar === 2 && ac === 1);
  if (type === "K") return Math.max(ar, ac) === 1;
  if (type === "B" && ar !== ac) return false;
  if (type === "R" && dr !== 0 && dc !== 0) return false;
  if (!["B", "R", "Q"].includes(type) || (dr !== 0 && dc !== 0 && ar !== ac) || (!dr && !dc)) return false;
  const sr = Math.sign(dr);
  const sc = Math.sign(dc);
  for (let row = r1 + sr, col = c1 + sc; row !== r2 || col !== c2; row += sr, col += sc) {
    if (board[row][col]) return false;
  }
  return true;
}

function inCheck(board, color) {
  let king = null;
  for (let row = 0; row < SIZE; row += 1) {
    for (let col = 0; col < SIZE; col += 1) {
      if (board[row][col] === `${color}K`) king = [row, col];
    }
  }
  if (!king) return false;
  const opponent = color === "w" ? "b" : "w";
  for (let row = 0; row < SIZE; row += 1) {
    for (let col = 0; col < SIZE; col += 1) {
      const piece = board[row][col];
      if (piece && piece[0] === opponent && pieceAttacks(board, [row, col], king)) return true;
    }
  }
  return false;
}

function isValidMove(board, start, end, rights = game.castlingRights) {
  if (sameSquare(start, end) || !inside(...start) || !inside(...end)) return false;
  const piece = board[start[0]][start[1]];
  if (!piece || !pseudoMoves(board, start, rights).some((square) => sameSquare(square, end))) return false;
  const castling = piece[1] === "K" && Math.abs(end[1] - start[1]) === 2;
  if (castling) {
    if (inCheck(board, piece[0])) return false;
    const transitCol = (start[1] + end[1]) / 2;
    const transit = copyBoard(board);
    transit[start[0]][transitCol] = piece;
    transit[start[0]][start[1]] = null;
    if (inCheck(transit, piece[0])) return false;
  }
  const after = copyBoard(board);
  after[end[0]][end[1]] = piece;
  after[start[0]][start[1]] = null;
  if (castling) {
    const rookStart = end[1] === 6 ? 7 : 0;
    const rookEnd = end[1] === 6 ? 5 : 3;
    after[end[0]][rookEnd] = after[end[0]][rookStart];
    after[end[0]][rookStart] = null;
  }
  return !inCheck(after, piece[0]);
}

function legalMoves(board, square, rights = game.castlingRights) {
  return pseudoMoves(board, square, rights).filter((end) => isValidMove(board, square, end, rights));
}

function sanForMove(start, end) {
  const [row, col] = start;
  const piece = game.board[row][col];
  if (piece[1] === "K" && Math.abs(end[1] - col) === 2) return end[1] === 6 ? "O-O" : "O-O-O";
  const capture = Boolean(game.board[end[0]][end[1]]);
  let prefix = "";
  if (piece[1] === "P") prefix = capture ? FILES[col] : "";
  else {
    prefix = piece[1];
    const competitors = [];
    for (let r = 0; r < SIZE; r += 1) {
      for (let c = 0; c < SIZE; c += 1) {
        const candidate = game.board[r][c];
        if (candidate && candidate[0] === piece[0] && candidate[1] === piece[1] && !sameSquare([r, c], start)
          && legalMoves(game.board, [r, c]).some((square) => sameSquare(square, end))) competitors.push([r, c]);
      }
    }
    if (competitors.length) {
      const sameFile = competitors.some((square) => square[1] === col);
      const sameRank = competitors.some((square) => square[0] === row);
      if (!sameFile) prefix += FILES[col];
      else if (!sameRank) prefix += String(SIZE - row);
      else prefix += `${FILES[col]}${SIZE - row}`;
    }
  }
  return `${prefix}${capture ? "x" : ""}${squareName(end)}`;
}

function removeRookRight(color, square) {
  const homeRow = color === "w" ? 7 : 0;
  if (square[0] === homeRow && square[1] === 0) game.castlingRights.delete(`${color}Q`);
  if (square[0] === homeRow && square[1] === 7) game.castlingRights.delete(`${color}K`);
}

function finishMove(san) {
  const opponent = game.turn === "w" ? "b" : "w";
  game.moveHistory.push(`${san}${inCheck(game.board, opponent) ? "+" : ""}`);
  game.turn = opponent;
  game.selected = null;
  game.pendingPromotion = null;
  savePosition();
  render();
}

function movePiece(start, end) {
  const piece = game.board[start[0]][start[1]];
  const captured = game.board[end[0]][end[1]];
  const san = sanForMove(start, end);
  if (piece[1] === "K") {
    game.castlingRights.delete(`${piece[0]}K`);
    game.castlingRights.delete(`${piece[0]}Q`);
  } else if (piece[1] === "R") removeRookRight(piece[0], start);
  if (captured && captured[1] === "R") removeRookRight(captured[0], end);

  game.board[end[0]][end[1]] = piece;
  game.board[start[0]][start[1]] = null;
  if (piece[1] === "K" && Math.abs(end[1] - start[1]) === 2) {
    const rookStart = end[1] === 6 ? 7 : 0;
    const rookEnd = end[1] === 6 ? 5 : 3;
    game.board[end[0]][rookEnd] = game.board[end[0]][rookStart];
    game.board[end[0]][rookStart] = null;
  }
  const promotes = piece === "wP" && end[0] === 0 || piece === "bP" && end[0] === 7;
  if (promotes) {
    game.pendingPromotion = { color: piece[0], end, san };
    showPromotion();
    render();
  } else finishMove(san);
}

function showPromotion() {
  const color = game.pendingPromotion.color;
  promotionOptions.replaceChildren();
  for (const type of PROMOTION_TYPES) {
    const button = document.createElement("button");
    button.className = "promotion-choice";
    button.type = "button";
    button.setAttribute("aria-label", `Promote to ${ASSET_NAMES[type]}`);
    const image = document.createElement("img");
    image.src = piecePath(`${color}${type}`);
    image.alt = "";
    if (type === "R") image.classList.add("rook");
    button.append(image);
    button.addEventListener("click", () => {
      const { end, san } = game.pendingPromotion;
      game.board[end[0]][end[1]] = `${color}${type}`;
      promotionDialog.close();
      finishMove(`${san}=${type}`);
    });
    promotionOptions.append(button);
  }
  promotionDialog.showModal();
}

function chooseSquare(square) {
  if (game.replayIndex !== null) {
    game.replayIndex = null;
    render();
    return;
  }
  if (game.pendingPromotion) return;
  const [row, col] = square;
  const clicked = game.board[row][col];
  if (!game.selected) {
    if (clicked && clicked[0] === game.turn) game.selected = square;
    render();
    return;
  }
  if (sameSquare(square, game.selected)) game.selected = null;
  else if (clicked && clicked[0] === game.turn) game.selected = square;
  else if (legalMoves(game.board, game.selected).some((target) => sameSquare(target, square))) movePiece(game.selected, square);
  render();
}

function piecePath(piece) {
  const colorName = piece[0] === "w" ? "white" : "black";
  return `../assets/pieces-basic-png/${colorName}-${ASSET_NAMES[piece[1]]}.png`;
}

function currentPosition() {
  return game.replayIndex === null ? null : game.positions[game.replayIndex];
}

function renderBoard() {
  const replay = currentPosition();
  const board = replay ? replay.board : game.board;
  const targets = replay || !game.selected ? [] : legalMoves(game.board, game.selected);
  boardElement.replaceChildren();
  for (let displayRow = 0; displayRow < SIZE; displayRow += 1) {
    for (let displayCol = 0; displayCol < SIZE; displayCol += 1) {
      const row = game.flipped ? SIZE - 1 - displayRow : displayRow;
      const col = game.flipped ? SIZE - 1 - displayCol : displayCol;
      const square = [row, col];
      const cell = document.createElement("button");
      cell.type = "button";
      cell.className = `square ${(displayRow + displayCol) % 2 === 0 ? "light" : "dark"}`;
      cell.setAttribute("role", "gridcell");
      cell.setAttribute("aria-label", `${squareName(square)}${board[row][col] ? ` ${board[row][col]}` : " empty"}`);
      if (sameSquare(square, game.selected) && !replay) cell.classList.add("selected");
      if (targets.some((target) => sameSquare(target, square))) cell.classList.add("legal");
      if (displayCol === 0) {
        const rank = document.createElement("span");
        rank.className = "axis-label rank-label";
        rank.textContent = String(8 - row);
        cell.append(rank);
      }
      if (displayRow === 7) {
        const file = document.createElement("span");
        file.className = "axis-label file-label";
        file.textContent = FILES[col];
        cell.append(file);
      }
      const piece = board[row][col];
      if (piece) {
        const img = document.createElement("img");
        img.className = `piece ${ASSET_NAMES[piece[1]]}`;
        img.src = piecePath(piece);
        img.alt = "";
        img.draggable = false;
        cell.append(img);
      }
      cell.addEventListener("click", () => chooseSquare(square));
      boardElement.append(cell);
    }
  }
}

function renderHistory() {
  historyElement.replaceChildren();
  const displayedPosition = game.replayIndex === null ? game.positions.length - 1 : game.replayIndex;
  const currentMoveIndex = displayedPosition - 1;
  if (!game.moveHistory.length) {
    const empty = document.createElement("p");
    empty.className = "empty-history";
    empty.textContent = "No moves yet";
    historyElement.append(empty);
  }
  for (let i = 0; i < game.moveHistory.length; i += 2) {
    const row = document.createElement("div");
    row.className = "move-row";
    const number = document.createElement("span");
    number.className = "move-number";
    number.textContent = `${Math.floor(i / 2) + 1}.`;
    row.append(number);
    for (const index of [i, i + 1]) {
      const move = document.createElement("span");
      move.className = "move";
      if (index < game.moveHistory.length) {
        move.textContent = game.moveHistory[index];
        if (index === currentMoveIndex) move.classList.add("current");
      }
      row.append(move);
    }
    historyElement.append(row);
  }
  countElement.textContent = `${game.moveHistory.length} ${game.moveHistory.length === 1 ? "move" : "moves"}`;
  const activeMove = historyElement.querySelector(".move.current");
  if (activeMove) activeMove.scrollIntoView({ block: "nearest" });
}

function render() {
  const replay = currentPosition();
  const board = replay ? replay.board : game.board;
  const turn = replay ? replay.turn : game.turn;
  const colorName = turn === "w" ? "White" : "Black";
  statusElement.textContent = `${colorName}${inCheck(board, turn) ? " in check" : " to move"}`;
  renderBoard();
  renderHistory();
  const latest = game.positions.length - 1;
  document.querySelector("#previous-button").disabled = latest === 0;
  document.querySelector("#next-button").disabled = game.replayIndex === null;
  document.querySelector("#takeback-button").disabled = latest === 0;
}

function moveReplay(direction) {
  const latest = game.positions.length - 1;
  const current = game.replayIndex === null ? latest : game.replayIndex;
  const next = Math.max(0, Math.min(latest, current + direction));
  game.replayIndex = next === latest ? null : next;
  render();
}

function takeBackLatest() {
  const latest = game.positions.length - 1;
  if (latest <= 0) return;
  restorePosition(latest - 1);
  if (promotionDialog.open) promotionDialog.close();
  render();
}

document.querySelector("#flip-button").addEventListener("click", () => {
  game.flipped = !game.flipped;
  renderBoard();
});
document.querySelector("#previous-button").addEventListener("click", () => moveReplay(-1));
document.querySelector("#next-button").addEventListener("click", () => moveReplay(1));
document.querySelector("#takeback-button").addEventListener("click", takeBackLatest);
document.addEventListener("keydown", (event) => {
  if (promotionDialog.open) return;
  if (event.key === "ArrowLeft") moveReplay(-1);
  else if (event.key === "ArrowRight") moveReplay(1);
  else if (event.key.toLowerCase() === "f") {
    game.flipped = !game.flipped;
    renderBoard();
  }
});

render();
