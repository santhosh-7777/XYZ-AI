"use client";

import { useState, useRef, useEffect } from "react";
import api from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  text: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await api.post("/ai/act", { text: userMessage.text });
      const result = response.data.result;
      const replyText =
        result?.message || JSON.stringify(result) || "No response.";

      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: replyText },
      ]);
    } catch (err: any) {
      // Handle confirmation-required responses (409 Conflict)
      if (err.response?.status === 409) {
        const detail: string = err.response.data?.detail || "";
        const match = detail.match(/action_id '([^']+)'/);

        if (match) {
          const actionId = match[1];

          try {
            const confirmResponse = await api.post("/ai/confirm", {
              action_id: actionId,
            });
            const confirmResult = confirmResponse.data.result;
            const replyText =
              confirmResult?.message ||
              JSON.stringify(confirmResult) ||
              "Action confirmed.";

            setMessages((prev) => [
              ...prev,
              { role: "assistant", text: replyText },
            ]);
          } catch (confirmErr: any) {
            setMessages((prev) => [
              ...prev,
              {
                role: "assistant",
                text: "Error: could not confirm the pending action.",
              },
            ]);
          }
        } else {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              text: "There's a pending action but I couldn't identify it.",
            },
          ]);
        }
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", text: "Error: could not reach the assistant." },
        ]);
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4">
        <h1 className="text-xl font-bold">XYZ AI Assistant</h1>
      </header>

      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-md px-4 py-2 rounded-lg ${
                msg.role === "user"
                  ? "bg-black text-white"
                  : "bg-white border text-gray-800"
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="max-w-md px-4 py-2 rounded-lg bg-white border text-gray-400">
              Thinking...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form
        onSubmit={handleSend}
        className="border-t bg-white px-6 py-4 flex gap-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me anything..."
          className="flex-1 border rounded px-3 py-2"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-black text-white px-4 py-2 rounded disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
}