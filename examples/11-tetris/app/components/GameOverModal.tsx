"use client";

import { useState, useEffect } from "react";

interface GameOverModalProps {
  score: number;
  level: number;
  lines: number;
  onRestart: () => void;
}

export function GameOverModal({
  score,
  level,
  lines,
  onRestart,
}: GameOverModalProps) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    // Check authentication status
    fetch("/api/auth/me")
      .then((res) => res.json())
      .then((data) => setIsAuthenticated(data.authenticated))
      .catch(() => setIsAuthenticated(false));
  }, []);

  const handleSubmit = async () => {
    setError("");
    setSubmitting(true);

    try {
      const response = await fetch("/api/high-scores", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          score,
          level,
          lines,
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error("Please sign in to submit your score");
        }
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to submit score");
      }

      setSubmitted(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit score");
    } finally {
      setSubmitting(false);
    }
  };

  const handleRestart = () => {
    setSubmitted(false);
    setError("");
    onRestart();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
        <h2 className="text-3xl font-bold text-gray-800 mb-2 text-center">
          Game Over!
        </h2>

        <div className="bg-gray-100 rounded-lg p-6 mb-6 space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-gray-600">Final Score:</span>
            <span className="text-2xl font-bold text-gray-800">{score}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">Level:</span>
            <span className="text-xl font-semibold text-indigo-600">
              {level}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">Lines:</span>
            <span className="text-xl font-semibold text-gray-800">{lines}</span>
          </div>
        </div>

        {!submitted ? (
          <div className="space-y-4">
            {isAuthenticated === null ? (
              <div className="text-center text-gray-600">Loading...</div>
            ) : !isAuthenticated ? (
              <div className="space-y-4">
                <p className="text-center text-gray-600">
                  Sign in with GitHub to save your score
                </p>
                <div className="flex gap-3">
                  <a
                    href="/api/auth/login"
                    className="flex-1 bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors text-center"
                  >
                    Sign in with GitHub
                  </a>
                  <button
                    type="button"
                    onClick={handleRestart}
                    className="flex-1 bg-gray-500 text-white py-3 rounded-lg font-semibold hover:bg-gray-600 transition-colors"
                  >
                    Skip
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {error && (
                  <p className="text-red-500 text-sm text-center">{error}</p>
                )}

                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={handleSubmit}
                    disabled={submitting}
                    className="flex-1 bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                  >
                    {submitting ? "Submitting..." : "Submit Score"}
                  </button>

                  <button
                    type="button"
                    onClick={handleRestart}
                    className="flex-1 bg-gray-500 text-white py-3 rounded-lg font-semibold hover:bg-gray-600 transition-colors"
                  >
                    Skip
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center space-y-4">
            <p className="text-green-600 font-semibold">
              Score submitted successfully!
            </p>
            <button
              type="button"
              onClick={handleRestart}
              className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
            >
              Play Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
