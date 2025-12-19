import type { Board as BoardType, Tetromino } from "../types/tetris";
import { BOARD_WIDTH, BOARD_HEIGHT } from "../lib/gameLogic";

interface BoardProps {
  board: BoardType;
  currentPiece: Tetromino | null;
}

export function Board({ board, currentPiece }: BoardProps) {
  // Create a display board with the current piece overlaid
  const displayBoard = board.map((row) => [...row]);

  if (currentPiece) {
    for (let y = 0; y < currentPiece.shape.length; y++) {
      for (let x = 0; x < currentPiece.shape[y].length; x++) {
        if (currentPiece.shape[y][x]) {
          const boardY = currentPiece.position.y + y;
          const boardX = currentPiece.position.x + x;
          if (
            boardY >= 0 &&
            boardY < BOARD_HEIGHT &&
            boardX >= 0 &&
            boardX < BOARD_WIDTH
          ) {
            displayBoard[boardY][boardX] = currentPiece.color;
          }
        }
      }
    }
  }

  return (
    <div
      className="inline-grid gap-[1px] bg-gray-800 p-1 rounded-lg shadow-2xl"
      style={{
        gridTemplateColumns: `repeat(${BOARD_WIDTH}, minmax(0, 1fr))`,
      }}
    >
      {displayBoard.map((row, y) =>
        row.map((cell, x) => (
          <div
            key={`${y}-${x}`}
            className="w-8 h-8 rounded-sm"
            style={{
              backgroundColor: cell || "#1f2937",
              boxShadow: cell ? "inset 0 0 0 1px rgba(255,255,255,0.3)" : "none",
            }}
          />
        ))
      )}
    </div>
  );
}
