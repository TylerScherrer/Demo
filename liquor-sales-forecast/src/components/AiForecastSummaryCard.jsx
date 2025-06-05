// AiForecastSummaryCard.jsx
import React from "react";

function AiForecastSummaryCard({ aiText }) {
  if (!aiText) return null;
  return (
    <div style={{
      border: "1px solid #ccc",
      padding: "10px",
      marginBottom: "10px",
      borderRadius: "4px",
      backgroundColor: "#f1f1f1"
    }}>
      <strong>AI-Generated Forecast Summary</strong>
      <p>{aiText}</p>
    </div>
  );
}

export default AiForecastSummaryCard;
