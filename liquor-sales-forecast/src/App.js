import React, { useEffect, useState } from "react";
import ForecastChart from "./components/ForecastChart";

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
        setError("Could not load store list");
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

      // ✅ Send entire timeline (not just forecast) to explanation
      explainForecast(data.timeline);

    } catch (err) {
      console.error("❌ Forecast request failed:", err);
      setError("Backend error");
    }
  };

const explainForecast = async (timelineData) => {
  console.log("🧪 Timeline data sent to /api/explain_forecast:", timelineData); // 🔍 Add this line

  try {
    const res = await fetch(`${BASE_URL}/api/explain_forecast`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ timeline: timelineData }),
    });

    const data = await res.json();
    console.log("📥 Explanation response:", data); // 🔍 Log response

    setSummary(data.summary || "No explanation returned.");
  } catch (err) {
    console.error("❌ Explanation request failed:", err);
    setSummary("Failed to generate explanation.");
  }
};


  return (
    <div style={{ margin: "30px", fontFamily: "Arial, sans-serif" }}>
      <h1>Liquor Sales Forecast</h1>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <div style={{ marginBottom: "15px" }}>
        <label><strong>Store:</strong>{" "}</label>
        <select
          value={selectedStore}
          onChange={(e) => setSelectedStore(e.target.value)}
        >
          <option value="">Select store</option>
          {storeList.map((store) => (
            <option key={store} value={store}>{store}</option>
          ))}
        </select>
        <button style={{ marginLeft: "10px" }} onClick={handleForecast}>
          Get Forecast
        </button>
      </div>

      {timeline.length > 0 && (
        <div>
          <h2>Results</h2>
          <ul>
            {timeline.map((item) => {
              const value = item.value;
              const label = item.type === "forecast" ? "Forecast" : "Actual";
              const range = item.upper
                ? ` (±${Math.round((item.upper - item.value) * 100) / 100})`
                : "";

              return (
                <li key={item.week}>
                  Week {item.week}: {value} [{label}]{range}
                </li>
              );
            })}
          </ul>

          <ForecastChart data={timeline} />

          {summary && (
            <div style={{ marginTop: "20px", background: "#f2f2f2", padding: "10px" }}>
              <strong>AI Explanation:</strong>
              <p>{summary}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
