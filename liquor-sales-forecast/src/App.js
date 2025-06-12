import React, { useEffect, useState } from "react";
import ForecastChart from "./components/ForecastChart";
import "./App.css";

export default function App() {
  const [storeList, setStoreList] = useState([]);
  const [selectedStore, setSelectedStore] = useState("");
  const [timeline, setTimeline] = useState([]);
  const [summary, setSummary] = useState("");
  const [error, setError] = useState("");

  const BASE_URL = "http://localhost:8000";

  useEffect(() => {
    fetch(`${BASE_URL}/api/stores`)
      .then((res) => res.json())
      .then((data) => setStoreList(data.stores || []))
      .catch((err) => {
        console.error("❌ Failed to load stores:", err);
        setError("Could not load store list.");
      });
  }, []);

  const handleForecast = async () => {
    if (!selectedStore) {
      setError("Please select a store.");
      return;
    }

    try {
      setError("");
      setSummary("");
      setTimeline([]);

      const res = await fetch(`${BASE_URL}/api/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ store: selectedStore, weeks: 4 }),
      });

      const data = await res.json();
      if (!data.timeline || data.timeline.length === 0) {
        setError("No forecast returned.");
        return;
      }

      setTimeline(data.timeline);
      explainForecast(data.timeline);
    } catch (err) {
      console.error("❌ Forecast request failed:", err);
      setError("Backend error");
    }
  };

  const explainForecast = async (timelineData) => {
    try {
      const res = await fetch(`${BASE_URL}/api/explain_forecast`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ timeline: timelineData }),
      });
      const data = await res.json();
      setSummary(data.summary || "No explanation returned.");
    } catch (err) {
      console.error("❌ Explanation request failed:", err);
      setSummary("Failed to generate explanation.");
    }
  };

  return (
    <div className="container">
      <h1 className="title">📊 Liquor Sales Forecast</h1>

      {error && <p className="error">{error}</p>}

      <div className="control-row">
        <label htmlFor="store-select"><strong>Store:</strong></label>
        <select
          id="store-select"
          value={selectedStore}
          onChange={(e) => setSelectedStore(e.target.value)}
        >
          <option value="">Select store</option>
          {storeList.map((store) => (
            <option key={store} value={store}>{store}</option>
          ))}
        </select>
        <button className="btn" onClick={handleForecast}>Get Forecast</button>
      </div>

      {timeline.length > 0 && (
        <>
          <h2 className="section-heading">Forecast Results</h2>
          <table className="result-table">
            <thead>
              <tr>
                <th>Week</th>
                <th>Type</th>
                <th>Sales ($)</th>
                <th>Range (±)</th>
              </tr>
            </thead>
            <tbody>
              {timeline.map((item) => {
                const isForecast = item.type === "forecast";
                const range = isForecast
                  ? Math.round(item.upper - item.value).toLocaleString()
                  : "—";
                return (
                  <tr key={item.week} className={isForecast ? "forecast-row" : "actual-row"}>
                    <td>{`Week ${item.week}`}</td>
                    <td>{isForecast ? "Forecast" : "Actual"}</td>
                    <td>${item.value.toLocaleString()}</td>
                    <td>{range !== "—" ? `±${range}` : range}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          <ForecastChart data={timeline} />

          {summary && (
            <div className="ai-box">
              <h3>AI-Generated Insight:</h3>
              <p>{summary}</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
