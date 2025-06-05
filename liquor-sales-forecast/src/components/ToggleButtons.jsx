import React from "react";

function ToggleButtons({
  showForecast,
  setShowForecast,
  handleForecast,
  showCompare,
  setShowCompare,
  handleCompare,
  showSeasonality,
  setShowSeasonality,
  handleSeasonality,
  showMetrics,
  setShowMetrics,
  handleMetrics,
  showFeatureImportance,
  setShowFeatureImportance,
  handleFeatureImportance
}) {
  return (
    <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
      <button
        onClick={async () => {
          if (showForecast) {
            setShowForecast(false);
          } else {
            await handleForecast();
            setShowForecast(true);
          }
        }}
      >
        {showForecast ? "Hide Forecast" : "Show Forecast"}
      </button>

      <button
        onClick={async () => {
          if (showCompare) {
            setShowCompare(false);
          } else {
            await handleCompare();
            setShowCompare(true);
          }
        }}
      >
        {showCompare ? "Hide Compare" : "Show Compare"}
      </button>

      <button
        onClick={async () => {
          if (showSeasonality) {
            setShowSeasonality(false);
          } else {
            await handleSeasonality();
            setShowSeasonality(true);
          }
        }}
      >
        {showSeasonality ? "Hide Seasonality" : "Show Seasonality"}
      </button>

      <button
        onClick={async () => {
          if (showMetrics) {
            setShowMetrics(false);
          } else {
            await handleMetrics();
            setShowMetrics(true);
          }
        }}
      >
        {showMetrics ? "Hide Metrics" : "Show Metrics"}
      </button>

      <button
        onClick={async () => {
          if (showFeatureImportance) {
            setShowFeatureImportance(false);
          } else {
            await handleFeatureImportance();
            setShowFeatureImportance(true);
          }
        }}
      >
        {showFeatureImportance ? "Hide Feature Importances" : "Show Feature Importances"}
      </button>
    </div>
  );
}

export default ToggleButtons;
