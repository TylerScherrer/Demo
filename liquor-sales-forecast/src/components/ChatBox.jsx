// src/components/ChatBox.jsx
import React, { useState } from "react";
import axios from "axios";

// Use same environment base URL
const BASE_URL = "https://ml-forecast-api-bpa9g0hscaccc0e0.canadacentral-01.azurewebsites.net";


export default function ChatBox({ chartData, chartType }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const send = async () => {
    if (!input.trim()) return;
    console.log("🛰️ Sending chat question:", input, chartType, chartData);
    try {
      const { data } = await axios.post(`${BASE_URL}/api/chat`, {
        question: input,
        chartType,
        chartData,
      });
      console.log("🛰️ /api/chat response:", data);
      if (data.reply) {
        setMessages((m) => [...m, { sender: "ai", text: data.reply }]);
      } else if (data.error) {
        console.error("⚠️ /api/chat returned error:", data.error);
      }
    } catch (e) {
      console.error("❌ Error talking to AI:", e);
      setMessages((m) => [...m, { sender: "ai", text: "🤖 Error talking to AI" }]);
    }
  };

  return (
    <div style={{ border: "1px solid #ccc", padding: 10, borderRadius: 4 }}>
      <div style={{ maxHeight: 200, overflowY: "auto", marginBottom: 10 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ textAlign: m.sender === "ai" ? "left" : "right" }}>
            <b>{m.sender === "ai" ? "AI" : "You"}:</b> {m.text}
          </div>
        ))}
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        <input
          style={{ flex: 1, padding: 4 }}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Ask about this chart…"
        />
        <button onClick={send}>Send</button>
      </div>
    </div>
  );
}
