import React from "react";

export default function StoreSelector({ storeList, selectedStore, setSelectedStore }) {
  return (
    <div>
      <label htmlFor="store"><strong>Store:</strong>{" "}</label>
      <select
        id="store"
        value={selectedStore}
        onChange={(e) => setSelectedStore(e.target.value)}
      >
        <option value="">Select a store</option>
        {storeList.map((storeId) => (
          <option key={storeId} value={storeId}>
            {storeId}
          </option>
        ))}
      </select>
    </div>
  );
}
