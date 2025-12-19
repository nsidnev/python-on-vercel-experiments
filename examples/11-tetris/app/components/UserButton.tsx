"use client";

import { useEffect, useState } from "react";

interface User {
  username: string;
  name: string;
  avatar: string;
}

export function UserButton() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/auth/me")
      .then((res) => res.json())
      .then((data) => {
        if (data.authenticated) {
          setUser(data.user);
        }
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="text-gray-600">Loading...</div>;
  }

  if (!user) {
    return (
      <a
        href="/api/auth/login"
        className="px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition-colors"
      >
        Sign in with GitHub
      </a>
    );
  }

  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-2">
        {user.avatar && (
          <img
            src={user.avatar}
            alt={user.username}
            className="w-8 h-8 rounded-full"
          />
        )}
        <span className="text-gray-700">@{user.username}</span>
      </div>
      <a
        href="/api/auth/logout"
        className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
      >
        Sign out
      </a>
    </div>
  );
}
