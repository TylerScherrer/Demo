import React from "react";

export default function AIInsight({ summary }) {
  if (!summary) return null;

  return (
    <div className="ai-box">
      <h3>AI-Generated Insight:</h3>
      <p>{summary}</p>
    </div>
  );
}
