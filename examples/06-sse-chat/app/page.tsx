'use client';

import { useState, useEffect, useRef } from 'react';

interface Message {
  id: number;
  username: string;
  content: string;
  timestamp: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [username, setUsername] = useState('');
  const [messageContent, setMessageContent] = useState('');
  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Regular API calls - use same origin (works in both dev and prod)
  const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

  // SSE URL: In development, connect directly to FastAPI to avoid Next.js rewrite buffering
  // In production, use same origin since there's no proxy
  const SSE_URL = process.env.NODE_ENV === 'development'
    ? (process.env.NEXT_PUBLIC_SSE_URL || 'http://127.0.0.1:5328')
    : '';

  useEffect(() => {
    loadMessages();
    connectSSE();

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function loadMessages() {
    try {
      const response = await fetch(`${API_URL}/api/messages`);
      const data = await response.json();
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  }

  async function connectSSE() {
    setStatus('connecting');

    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    try {
      // Connect directly to FastAPI for SSE
      const response = await fetch(`${SSE_URL}/api/stream`, {
        signal: abortController.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      setStatus('connected');

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      if (!reader) {
        throw new Error('Response body is null');
      }

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;

        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            try {
              const parsed = JSON.parse(data);

              if (parsed.type === 'message') {
                setMessages((prev) => {
                  if (prev.some((msg) => msg.id === parsed.message.id)) {
                    return prev;
                  }
                  return [...prev, parsed.message];
                });
              }
            } catch (error) {
              console.error('Error parsing SSE message:', error);
            }
          }
        }
      }
    } catch (error: any) {
      if (error.name === 'AbortError') {
        return;
      }

      console.error('SSE error:', error);
      setStatus('disconnected');

      setTimeout(() => {
        connectSSE();
      }, 2000);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    if (!username.trim() || !messageContent.trim()) {
      return;
    }

    try {
      await fetch(`${API_URL}/api/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username.trim(),
          content: messageContent.trim(),
        }),
      });

      setMessageContent('');
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <div className="w-full max-w-3xl h-[600px] bg-white rounded-lg shadow-lg flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h1 className="text-2xl font-bold text-gray-900">SSE Chat</h1>
          <div className="flex items-center gap-2">
            <div
              className={`w-3 h-3 rounded-full ${
                status === 'connected'
                  ? 'bg-green-500'
                  : status === 'connecting'
                    ? 'bg-yellow-500'
                    : 'bg-red-500'
              }`}
            />
            <span className="text-sm text-gray-600 capitalize">{status}</span>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.length === 0 ? (
            <p className="text-gray-500 text-center italic">No messages yet. Start chatting!</p>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className="bg-gray-50 rounded-lg p-3">
                <div className="flex items-baseline gap-2 mb-1">
                  <span className="font-semibold text-blue-600">{msg.username}</span>
                  <span className="text-xs text-gray-500">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <p className="text-gray-800">{msg.content}</p>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="p-4 border-t">
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Your name"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-32 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
            <input
              type="text"
              placeholder="Type a message..."
              value={messageContent}
              onChange={(e) => setMessageContent(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
            <button
              type="submit"
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
