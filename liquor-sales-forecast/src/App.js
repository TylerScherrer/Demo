import React, { useEffect, useState } from "react";
import StoreSelector from "./components/StoreSelector";

function App() {
  const [storeList, setStoreList] = useState([]);
  const [selectedStore, setSelectedStore] = useState("");
  const [forecast, setForecast] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("http://localhost:8000/api/stores")
      .then((res) => res.json())
      .then((data) => setStoreList(data.stores || []))
      .catch((err) => {
        console.error("Failed to load stores:", err);
        setStoreList([]);
      });
  }, []);

  // Click handler to fetch forecast
  const fetchForecast = async () => {
    if (!selectedStore) {
      setError("Please select a store");
      return;
    }

    setError("");
    setForecast([]);

    try {
      const res = await fetch("http://localhost:8000/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ store: selectedStore, weeks: 4 }),
      });

      const data = await res.json();
      if (data.prediction) {
        setForecast(data.prediction);
      } else {
        setError("No forecast returned");
      }
    } catch (err) {
      console.error("Forecast fetch error:", err);
      setError("Backend error");
    }
  };

  return (
    <div style={{ margin: "30px", fontFamily: "Arial" }}>
      <h1>Liquor Sales Forecast</h1>

      <StoreSelector
        storeList={storeList}
        selectedStore={selectedStore}
        setSelectedStore={setSelectedStore}
      />

      {selectedStore && (
        <p style={{ marginTop: "20px" }}>
          You selected store <strong>{selectedStore}</strong>
        </p>
      )}

      <button onClick={fetchForecast} style={{ marginTop: "20px" }}>
        Get Forecast
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {forecast.length > 0 && (
        <div style={{ marginTop: "20px" }}>
          <h2>Forecast Results</h2>
          <ul>
            {forecast.map((item) => (
              <li key={item.week}>
                Week {item.week}: {item.predicted} (±{item.upper - item.predicted})
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
