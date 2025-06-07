import React, { useEffect, useState } from "react";
import StoreSelector from "./components/StoreSelector";

function App() {
  const [storeList, setStoreList] = useState([]);
  const [selectedStore, setSelectedStore] = useState("");

  useEffect(() => {
    fetch("http://localhost:8000/api/stores")
      .then((res) => res.json())
      .then((data) => setStoreList(data.stores || []))
      .catch((err) => {
        console.error("Failed to load stores:", err);
        setStoreList([]);
      });
  }, []);

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
          ✅ You selected store <strong>{selectedStore}</strong>
        </p>
      )}
    </div>
  );
}

export default App;
