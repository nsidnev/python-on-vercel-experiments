import type { Tetromino } from "../types/tetris";

interface GameInfoProps {
  score: number;
  level: number;
  lines: number;
  nextPiece: Tetromino | null;
  paused: boolean;
  onPause: () => void;
  onRestart: () => void;
}

export function GameInfo({
  score,
  level,
  lines,
  nextPiece,
  paused,
  onPause,
  onRestart,
}: GameInfoProps) {
  return (
    <div className="flex flex-col gap-6">
      {/* Stats */}
      <div className="bg-white rounded-lg shadow-lg p-6 space-y-4 min-w-[200px]">
        <div>
          <p className="text-sm text-gray-600">Score</p>
          <p className="text-3xl font-bold text-gray-800">{score}</p>
        </div>

        <div>
          <p className="text-sm text-gray-600">Level</p>
          <p className="text-2xl font-bold text-indigo-600">{level}</p>
        </div>

        <div>
          <p className="text-sm text-gray-600">Lines</p>
          <p className="text-2xl font-bold text-gray-800">{lines}</p>
        </div>
      </div>

      {/* Next Piece */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <p className="text-sm text-gray-600 mb-3">Next</p>
        <div className="inline-grid gap-[1px] bg-gray-300 p-1 rounded">
          {nextPiece &&
            nextPiece.shape.map((row, y) => (
              <div key={y} className="flex">
                {row.map((cell, x) => (
                  <div
                    key={`${y}-${x}`}
                    className="w-6 h-6"
                    style={{
                      backgroundColor: cell ? nextPiece.color : "#f3f4f6",
                    }}
                  />
                ))}
              </div>
            ))}
        </div>
      </div>

      {/* Controls */}
      <div className="space-y-2">
        <button
          type="button"
          onClick={onPause}
          className="w-full px-4 py-2 bg-yellow-500 text-white rounded-lg font-semibold hover:bg-yellow-600 transition-colors"
        >
          {paused ? "Resume" : "Pause"}
        </button>

        <button
          type="button"
          onClick={onRestart}
          className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
        >
          New Game
        </button>
      </div>
    </div>
  );
}
