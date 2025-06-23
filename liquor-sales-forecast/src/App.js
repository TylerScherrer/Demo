import React, { useEffect, useState } from "react";
import ForecastChart from "./components/ForecastChart";
import "./App.css";
import dayjs from "dayjs";


export default function App() {
  const [storeList, setStoreList] = useState([]);
  const [selectedStore, setSelectedStore] = useState("");
  const [forecastWeeks, setForecastWeeks] = useState(4);
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
        body: JSON.stringify({ store: selectedStore, weeks: forecastWeeks }),
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

      if (!res.ok) {
        // Server responded but with an error (e.g., 500)
        console.error(`❌ Server responded with status ${res.status}`);
        if (res.status === 500) {
          setSummary("⚠️ Forecast explanation temporarily unavailable due to model loading issue.");
        } else {
          setSummary(`⚠️ Unexpected error (${res.status}) while generating explanation.`);
        }
        return;
      }

      const data = await res.json();
      setSummary(data.summary || "⚠️ No explanation returned.");
    } catch (err) {
      // Network or JSON parsing error
      console.error("❌ Explanation request failed:", err);
      setSummary("⚠️ Failed to generate explanation due to a network or system error.");
    }
  };


  const forecastWeeksOnly = timeline.filter(w => w.type === "forecast");

  const totalForecast = forecastWeeksOnly.reduce((sum, w) => sum + w.value, 0);
  const avgForecast = forecastWeeksOnly.length > 0 ? totalForecast / forecastWeeksOnly.length : 0;

  let growthSummary = "—";
  if (forecastWeeksOnly.length > 1) {
    const deltas = forecastWeeksOnly.slice(1).map((w, i) => {
      const prev = forecastWeeksOnly[i].value;
      const delta = ((w.value - prev) / prev) * 100;
      return { week: w.week, delta };
    });

    const signs = deltas.map(d => `${d.delta >= 0 ? "↑" : "↓"} ${Math.abs(d.delta).toFixed(1)}% (Week ${d.week})`);
    growthSummary = signs.join(", ");
  }

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

        <label htmlFor="weeks-select"><strong>Weeks:</strong></label>
        <select
          id="weeks-select"
          value={forecastWeeks}
          onChange={(e) => setForecastWeeks(parseInt(e.target.value))}
        >
          <option value={4}>4 Weeks</option>
          <option value={8}>8 Weeks</option>
          <option value={12}>12 Weeks</option>
        </select>

        <button className="btn" onClick={handleForecast}>Get Forecast</button>
      </div>

      {timeline.length > 0 && (
        <>
          <h2 className="section-heading">Forecast Results</h2>
          <table className="result-table">
            <thead>
              <tr>
                <th>Month</th>
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
      <React.Fragment key={item.week}>
        <tr className={isForecast ? "forecast-row" : "actual-row"}>
          <td>
            {item.week_start
              ? dayjs(item.week_start).format("MMMM YYYY")
              : `Month ${item.week}`}

          </td>
          <td>{isForecast ? "Forecast" : "Actual"}</td>
          <td>${item.value.toLocaleString()}</td>
          <td>{range !== "—" ? `±${range}` : range}</td>
        </tr>

        {isForecast && item.category_breakdown && (
          <tr className="breakdown-row">
            <td colSpan="4">
              <details>
                <summary>Category Breakdown</summary>
                <ul className="category-list">
                  {Object.entries(item.category_breakdown)
                    .sort(([, a], [, b]) => b - a)
                    .map(([cat, val]) => (
                      <li key={cat}>
                        {cat.replace(/_/g, " ")}: ${val.toLocaleString()}
                      </li>
                    ))}
                </ul>
              </details>
            </td>
          </tr>
        )}
      </React.Fragment>
    );
  })}

</tbody>

          </table>

          <ForecastChart data={timeline} />

          {timeline.length > 0 && (
            <div className="metric-box">
              <h3>📊 Growth Metrics</h3>
              <ul>
                <li><strong>Total Forecasted Sales:</strong> ${totalForecast.toLocaleString()}</li>
                <li><strong>Average Weekly Forecast:</strong> ${avgForecast.toLocaleString()}</li>
                <li><strong>Week-over-Week Growth:</strong> {growthSummary}</li>
              </ul>
            </div>
          )}

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
