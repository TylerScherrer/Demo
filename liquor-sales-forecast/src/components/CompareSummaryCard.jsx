// CompareSummaryCard.jsx
import React from "react";

function CompareSummaryCard({ compareData }) {
  if (!compareData || compareData.length === 0) return null;

  // Example: compute average difference
  let totalError = 0;
  compareData.forEach((d) => {
    totalError += Math.abs(d.actual - d.predicted);
  });
  const avgError = totalError / compareData.length || 0;
  const friendlyError = avgError.toLocaleString(undefined, { maximumFractionDigits: 0 });

  return (
    <div style={{
      border: "1px solid #ccc",
      backgroundColor: "#f9f9f9",
      padding: "10px",
      marginBottom: "10px",
      borderRadius: "4px"
    }}>
      <strong>Historic Comparison Summary</strong>
      <p style={{ margin: 0 }}>
        Over the last {compareData.length} periods, our model’s average error (difference between 
        actual and predicted) was about <strong>\${friendlyError}</strong> per period.
      </p>
      <p style={{ margin: 0 }}>
        This helps you see how close or far predictions can be on historical data.
      </p>
    </div>
  );
}

export default CompareSummaryCard;
