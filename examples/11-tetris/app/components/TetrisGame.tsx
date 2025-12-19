"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import type { GameState } from "../types/tetris";
import {
  createEmptyBoard,
  isValidMove,
  mergePieceToBoard,
  clearLines,
  calculateScore,
  calculateLevel,
  getDropSpeed,
} from "../lib/gameLogic";
import { createTetromino, rotateTetromino } from "../lib/tetrominos";
import { Board } from "./Board";
import { GameInfo } from "./GameInfo";
import { GameOverModal } from "./GameOverModal";

export function TetrisGame() {
  const [mounted, setMounted] = useState(false);
  const [gameState, setGameState] = useState<GameState>({
    board: createEmptyBoard(),
    currentPiece: null,
    nextPiece: createTetromino(),
    score: 0,
    level: 0,
    lines: 0,
    gameOver: false,
    paused: false,
  });

  const gameLoopRef = useRef<number | undefined>(undefined);
  const lastDropTime = useRef<number>(0);

  const startGame = useCallback(() => {
    const newCurrentPiece = createTetromino();
    const newNextPiece = createTetromino();
    console.log('[TETRIS] Starting game with pieces:', {
      currentPiece: newCurrentPiece,
      nextPiece: newNextPiece
    });
    setGameState({
      board: createEmptyBoard(),
      currentPiece: newCurrentPiece,
      nextPiece: newNextPiece,
      score: 0,
      level: 0,
      lines: 0,
      gameOver: false,
      paused: false,
    });
    lastDropTime.current = Date.now();
  }, []);

  const movePiece = useCallback(
    (dx: number, dy: number) => {
      if (
        gameState.gameOver ||
        gameState.paused ||
        !gameState.currentPiece
      ) {
        return;
      }

      const newPiece = {
        ...gameState.currentPiece,
        position: {
          x: gameState.currentPiece.position.x + dx,
          y: gameState.currentPiece.position.y + dy,
        },
      };

      if (isValidMove(gameState.board, newPiece)) {
        setGameState((prev) => ({ ...prev, currentPiece: newPiece }));
      } else if (dy > 0) {
        // Lock piece
        const newBoard = mergePieceToBoard(
          gameState.board,
          gameState.currentPiece
        );
        const { board: clearedBoard, linesCleared } = clearLines(newBoard);

        const newLines = gameState.lines + linesCleared;
        const newLevel = calculateLevel(newLines);
        const newScore =
          gameState.score + calculateScore(linesCleared, gameState.level);

        const nextPiece = gameState.nextPiece || createTetromino();

        // Check game over
        if (!isValidMove(clearedBoard, nextPiece)) {
          setGameState((prev) => ({
            ...prev,
            board: clearedBoard,
            gameOver: true,
          }));
          return;
        }

        setGameState({
          board: clearedBoard,
          currentPiece: nextPiece,
          nextPiece: createTetromino(),
          score: newScore,
          level: newLevel,
          lines: newLines,
          gameOver: false,
          paused: false,
        });
      }
    },
    [gameState]
  );

  const rotate = useCallback(() => {
    if (gameState.gameOver || gameState.paused || !gameState.currentPiece) {
      return;
    }

    const rotated = rotateTetromino(gameState.currentPiece);

    if (isValidMove(gameState.board, rotated)) {
      setGameState((prev) => ({ ...prev, currentPiece: rotated }));
    }
  }, [gameState]);

  const hardDrop = useCallback(() => {
    if (gameState.gameOver || gameState.paused || !gameState.currentPiece) {
      return;
    }

    let dropDistance = 0;
    while (
      isValidMove(gameState.board, gameState.currentPiece, 0, dropDistance + 1)
    ) {
      dropDistance++;
    }

    if (dropDistance > 0) {
      movePiece(0, dropDistance);
    }
  }, [gameState, movePiece]);

  const togglePause = useCallback(() => {
    if (!gameState.gameOver) {
      setGameState((prev) => ({ ...prev, paused: !prev.paused }));
    }
  }, [gameState.gameOver]);

  // Keyboard controls
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (gameState.gameOver) return;

      switch (e.key) {
        case "ArrowLeft":
          e.preventDefault();
          movePiece(-1, 0);
          break;
        case "ArrowRight":
          e.preventDefault();
          movePiece(1, 0);
          break;
        case "ArrowDown":
          e.preventDefault();
          movePiece(0, 1);
          break;
        case "ArrowUp":
          e.preventDefault();
          rotate();
          break;
        case " ":
          e.preventDefault();
          hardDrop();
          break;
        case "p":
        case "P":
          e.preventDefault();
          togglePause();
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [gameState.gameOver, movePiece, rotate, hardDrop, togglePause]);

  // Game loop
  useEffect(() => {
    console.log('[TETRIS] Game loop effect triggered', {
      gameOver: gameState.gameOver,
      paused: gameState.paused,
      hasCurrentPiece: !!gameState.currentPiece,
      currentPiece: gameState.currentPiece
    });

    if (gameState.gameOver || gameState.paused || !gameState.currentPiece) {
      console.log('[TETRIS] Game loop exiting early');
      return;
    }

    console.log('[TETRIS] Starting game loop');
    const gameLoop = () => {
      const now = Date.now();
      const dropSpeed = getDropSpeed(gameState.level);

      if (now - lastDropTime.current > dropSpeed) {
        movePiece(0, 1);
        lastDropTime.current = now;
      }

      gameLoopRef.current = requestAnimationFrame(gameLoop);
    };

    gameLoopRef.current = requestAnimationFrame(gameLoop);

    return () => {
      if (gameLoopRef.current) {
        cancelAnimationFrame(gameLoopRef.current);
      }
    };
  }, [gameState, movePiece]);

  // Ensure component only renders on client to avoid hydration mismatch
  useEffect(() => {
    console.log('[TETRIS] Mount effect running');
    setMounted(true);
    // Start game after mounting on client
    startGame();
  }, [startGame]);

  // Don't render until mounted on client
  if (!mounted) {
    console.log('[TETRIS] Not mounted yet, showing loading');
    return (
      <div className="flex flex-col items-center gap-8 p-8">
        <h1 className="text-4xl font-bold text-gray-800">Tetris</h1>
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  console.log('[TETRIS] Rendering game', {
    mounted,
    gameState: {
      hasCurrentPiece: !!gameState.currentPiece,
      score: gameState.score,
      gameOver: gameState.gameOver,
      paused: gameState.paused
    }
  });

  return (
    <div className="flex flex-col items-center gap-8 p-8">
      <h1 className="text-4xl font-bold text-gray-800">Tetris</h1>

      <div className="flex gap-8 items-start">
        <Board board={gameState.board} currentPiece={gameState.currentPiece} />

        <GameInfo
          score={gameState.score}
          level={gameState.level}
          lines={gameState.lines}
          nextPiece={gameState.nextPiece}
          paused={gameState.paused}
          onPause={togglePause}
          onRestart={startGame}
        />
      </div>

      <div className="text-center text-sm text-gray-600 space-y-1">
        <p>
          <strong>Controls:</strong> Arrow Keys to move, Up Arrow to rotate,
          Space to drop
        </p>
        <p>Press P to pause/resume</p>
      </div>

      {gameState.gameOver && (
        <GameOverModal
          score={gameState.score}
          level={gameState.level}
          lines={gameState.lines}
          onRestart={startGame}
        />
      )}
    </div>
  );
}
