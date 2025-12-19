"use client";

import { useState, useEffect } from "react";
import type { HighScore } from "../types/tetris";

export function HighScores() {
  const [scores, setScores] = useState<HighScore[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchScores = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch("/api/high-scores?limit=10");

      if (!response.ok) {
        throw new Error("Failed to load high scores");
      }

      const data = await response.json();
      setScores(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load scores");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchScores();

    // Refresh scores every 30 seconds
    const interval = setInterval(fetchScores, 30000);
    return () => clearInterval(interval);
  }, []);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString([], {
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="bg-white rounded-2xl shadow-2xl p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">High Scores</h2>
        <button
          type="button"
          onClick={fetchScores}
          className="text-indigo-600 hover:text-indigo-700 text-sm font-medium"
          disabled={loading}
        >
          {loading ? "Loading..." : "Refresh"}
        </button>
      </div>

      {error && (
        <p className="text-red-500 text-sm text-center mb-4">{error}</p>
      )}

      {loading && scores.length === 0 ? (
        <div className="text-center text-gray-500 py-8">Loading scores...</div>
      ) : scores.length === 0 ? (
        <div className="text-center text-gray-500 py-8">
          No high scores yet. Be the first!
        </div>
      ) : (
        <div className="space-y-3">
          {scores.map((score, index) => (
            <div
              key={score.id}
              className={`flex items-center gap-4 p-4 rounded-lg ${
                index === 0
                  ? "bg-gradient-to-r from-yellow-100 to-yellow-50 border-2 border-yellow-300"
                  : index === 1
                    ? "bg-gradient-to-r from-gray-100 to-gray-50 border-2 border-gray-300"
                    : index === 2
                      ? "bg-gradient-to-r from-orange-100 to-orange-50 border-2 border-orange-300"
                      : "bg-gray-50"
              }`}
            >
              <div className="text-2xl font-bold text-gray-700 w-8">
                {index === 0 ? "🥇" : index === 1 ? "🥈" : index === 2 ? "🥉" : `${index + 1}.`}
              </div>

              <div className="flex-1 min-w-0">
                <p className="font-semibold text-gray-800 truncate">
                  {score.player_name}
                </p>
                <p className="text-xs text-gray-500">
                  Level {score.level} • {score.lines} lines •{" "}
                  {formatDate(score.created_at)}
                </p>
              </div>

              <div className="text-right">
                <p className="text-xl font-bold text-indigo-600">
                  {score.score.toLocaleString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
