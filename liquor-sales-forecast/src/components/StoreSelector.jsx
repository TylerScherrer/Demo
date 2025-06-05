import React from "react";

function StoreSelector({ storeList, selectedStore, setSelectedStore }) {
  return (
    <div>
      <label><strong>Store:</strong>{" "}</label>
      <select
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

export default StoreSelector;
