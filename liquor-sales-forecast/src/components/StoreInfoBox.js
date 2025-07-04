import React from "react";

export default function StoreInfoBox({ store }) {
  if (!store) return null;

  return (
    <div className="store-meta-box">
      <h3>Store Info</h3>
      <ul>
        <li><strong>City:</strong> {store.city}</li>
        <li><strong>County:</strong> {store.county}</li>
        <li><strong>Store #:</strong> {store.store_number}</li>
        <li><strong>Avg Monthly Sales:</strong> ${store.avg_sales.toLocaleString()}</li>
        <li><strong>Peak Month:</strong> {store.peak_month} (${store.peak_value.toLocaleString()})</li>
      </ul>
    </div>
  );
}
