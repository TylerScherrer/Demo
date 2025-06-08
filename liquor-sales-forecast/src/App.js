import React, { useEffect, useState } from "react";
import ForecastChart from "./components/ForecastChart";

export default function App() {
  const [storeList, setStoreList] = useState([]);
  const [selectedStore, setSelectedStore] = useState("");
  const [forecast, setForecast] = useState([]);
  const [error, setError] = useState("");

  const BASE_URL = "http://localhost:8000"; // Update if using a deployed API

  // Load stores on initial render
  useEffect(() => {
    fetch(`${BASE_URL}/api/stores`)
      .then((res) => res.json())
      .then((data) => setStoreList(data.stores || []))
      .catch((err) => {
        console.error("❌ Failed to load stores:", err);
        setError("Could not load store list");
      });
  }, []);

  // Handle forecast request
  const handleForecast = async () => {
    if (!selectedStore) {
      setError("Please select a store.");
      return;
    }

    try {
      setError("");
      const res = await fetch(`${BASE_URL}/api/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ store: selectedStore, weeks: 4 }),
      });

      const data = await res.json();
      if (!data.prediction) {
        setForecast([]);
        setError("No forecast returned");
      } else {
        setForecast(data.prediction);
      }
    } catch (err) {
      console.error("❌ Forecast request failed:", err);
      setError("Backend error");
    }
  };

  return (
    <div style={{ margin: "30px", fontFamily: "Arial" }}>
      <h1>Liquor Sales Forecast</h1>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {/* Store Selection */}
      <div style={{ marginBottom: "15px" }}>
        <label><strong>Store:</strong>{" "}</label>
        <select
          value={selectedStore}
          onChange={(e) => setSelectedStore(e.target.value)}
        >
          <option value="">Select store</option>
          {storeList.map((store) => (
            <option key={store} value={store}>
              {store}
            </option>
          ))}
        </select>
      </div>

      {/* Forecast Button */}
      <button onClick={handleForecast}>Get Forecast</button>

      {/* Forecast Results */}
      {forecast.length > 0 && (
        <div style={{ marginTop: "30px" }}>
          <h2>Forecast Results</h2>
          <ul>
            {forecast.map((item) => {
              const range = Math.round((item.upper - item.predicted) * 100) / 100;
              return (
                <li key={item.week}>
                  Week {item.week}: {item.predicted} (±{range})
                </li>
              );
            })}
          </ul>

          {/* Chart Visualization */}
          <ForecastChart data={forecast} />
        </div>
      )}
    </div>
  );
}
