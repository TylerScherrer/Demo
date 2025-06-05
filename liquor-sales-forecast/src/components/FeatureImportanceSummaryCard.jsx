import React from "react";

function FeatureImportanceSummaryCard({ actionableData, conceptualData }) {
  const combined = [...actionableData, ...conceptualData].sort((a, b) => b.importance - a.importance);
  if (combined.length === 0) return null;

  const top = combined[0];  // the most important feature
  const second = combined[1] || null;

  return (
    <div style={{
      border: "1px solid #ccc",
      padding: "10px",
      marginBottom: "10px",
      borderRadius: "4px",
      backgroundColor: "#f9f9f9"
    }}>
      <strong>Feature Importance Summary</strong>
      <p style={{ margin: 0 }}>
        The most influential feature is <strong>{top.feature}</strong>, 
        indicating that changes in this factor have the largest impact on the model’s predictions.
      </p>
      {second && (
        <p style={{ margin: 0 }}>
          The second most important factor is <strong>{second.feature}</strong>.
        </p>
      )}
    </div>
  );
}

export default FeatureImportanceSummaryCard;
