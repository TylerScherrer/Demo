import React from "react";

function ForecastSummaryCard({ selectedStore, forecastData }) {
  const totalPredicted = forecastData.reduce((acc, cur) => acc + cur.predicted, 0);

  const lowerBound = forecastData[0].lower;
  const upperBound = forecastData[0].upper;

  const friendlyTotal = totalPredicted.toLocaleString(undefined, { maximumFractionDigits: 0 });
  const friendlyLower = lowerBound.toLocaleString(undefined, { maximumFractionDigits: 0 });
  const friendlyUpper = upperBound.toLocaleString(undefined, { maximumFractionDigits: 0 });

  return (
    <div
      style={{
        border: "1px solid #ccc",
        padding: "10px",
        marginBottom: "10px",
        borderRadius: "4px",
        backgroundColor: "#f9f9f9"
      }}
    >
      <strong>Forecast Summary</strong>
      <p style={{ margin: 0 }}>
        {selectedStore
          ? `Store #${selectedStore} is projected to have a total sales of approximately $${friendlyTotal} 
             over the next ${forecastData.length} weeks.`
          : "No store selected."}
      </p>
      <p style={{ margin: 0 }}>
        95% confidence range: 
        <span style={{ marginLeft: 5 }}>
          ${friendlyLower} – ${friendlyUpper}
        </span>
      </p>
    </div>
  );
}

export default ForecastSummaryCard;
