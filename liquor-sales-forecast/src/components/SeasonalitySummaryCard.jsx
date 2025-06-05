import React from "react";

function SeasonalitySummaryCard({ seasonalityData }) {
  if (!seasonalityData || seasonalityData.length === 0) return null;

  // Example: find the month with the highest average sales
  let maxMonthObj = seasonalityData[0];
  seasonalityData.forEach((m) => {
    if (m.avg_sales > maxMonthObj.avg_sales) {
      maxMonthObj = m;
    }
  });

  const { month, avg_sales } = maxMonthObj;
  const friendlySales = avg_sales.toLocaleString(undefined, { maximumFractionDigits: 0 });

  return (
    <div style={{
      border: "1px solid #ccc",
      padding: "10px",
      marginBottom: "10px",
      borderRadius: "4px",
      backgroundColor: "#f9f9f9"
    }}>
      <strong>Seasonality Summary</strong>
      <p style={{ margin: 0 }}>
        Historically, month <strong>{month}</strong> shows the highest average sales at 
        approximately <strong>\${friendlySales}</strong>.
      </p>
      <p style={{ margin: 0 }}>
        This pattern can help with planning promotions or staffing during peak months.
      </p>
    </div>
  );
}

export default SeasonalitySummaryCard;
