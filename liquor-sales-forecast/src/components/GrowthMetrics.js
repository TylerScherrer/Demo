import React from "react";

export default function GrowthMetrics({ totalForecast, avgForecast, growthSummary }) {
  return (
    <div className="metric-box">
      <h3>Growth Metrics</h3>
      <ul>
        <li><strong>Total Forecasted Sales:</strong> ${totalForecast.toLocaleString()}</li>
        <li><strong>Average Monthly Forecast:</strong> ${avgForecast.toLocaleString()}</li>
        <li><strong>Month-over-Month Growth:</strong> {growthSummary}</li>
      </ul>
    </div>
  );
}
