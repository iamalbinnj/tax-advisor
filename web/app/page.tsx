"use client";

import type React from "react";
import { useState, useRef, useEffect } from "react";

type Message = {
  id: string;
  content: string;
  sender: "user" | "ai";
  timestamp: Date;
};

export default function ChatInterface() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [showWelcome, setShowWelcome] = useState(true);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setShowWelcome(false);
    setLoading(true);

    // AI Placeholder
    const aiMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: "",
      sender: "ai",
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, aiMessage]);

    try {
      const response = await fetch(`http://localhost:8000/query?q=${encodeURIComponent(userMessage.content)}`);

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let aiResponseText = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        aiResponseText += decoder.decode(value, { stream: true });

        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === aiMessage.id ? { ...msg, content: aiResponseText } : msg
          )
        );
      }
    } catch (error) {
      console.error("Error fetching AI response:", error);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === aiMessage.id ? { ...msg, content: "Error fetching response. Please try again." } : msg
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="container max-w-screen-2xl mx-auto xl:px-24 py-16 flex flex-col h-screen bg-[#1a1a1a] text-white">
      <div className={`flex-1 p-4 space-y-4 ${showWelcome ? "overflow-hidden" : "overflow-y-auto"}`}>
        {showWelcome ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <h2 className="text-2xl font-bold mb-2">Hi, I'm Tax Advisor.</h2>
            <p className="text-white/70 mb-8">How can I help you today?</p>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`p-3 rounded-lg max-w-xl ${message.sender === "user" ? "bg-blue-600" : "bg-gray-700"}`}>
                {message.content}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 flex-shrink-0 sticky bottom-0">
        <form onSubmit={handleSubmit} className="relative flex items-center">
          <textarea
            ref={inputRef}
            value={input}
            onChange={handleTextareaChange}
            placeholder="Ask anything"
            className="w-full bg-[#333] text-white rounded-lg pl-4 pr-12 py-3 resize-none min-h-[50px] max-h-[120px] focus:outline-none focus:ring-1 focus:ring-blue-600"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                if (input.trim()) handleSubmit(e);
              }
            }}
          />
          <button
            type="submit"
            className="absolute bottom-3 right-3 p-2 cursor-pointer bg-blue-600 rounded-full hover:bg-blue-700 disabled:opacity-50"
            disabled={!input.trim() || loading}
          >
            {loading ? "..." : "Send"}
          </button>
        </form>
        <div className="text-xs text-center mt-2 text-white/50">AI-generated, for reference only</div>
      </div>
    </div>
  );
}
