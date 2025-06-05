// FeatureImportanceChart.jsx
import React from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer
} from "recharts";

function FeatureImportanceChart({ data }) {
  // Data shape: [{ feature: "Lag_1", importance: 0.3 }, ...]
  return (
    <div style={{ width: "100%", height: 400 }}>
      <ResponsiveContainer>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 20, right: 30, left: 100, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          {/* XAxis is the 'importance' scale, YAxis is feature names */}
          <XAxis type="number" />
          <YAxis dataKey="feature" type="category" width={150} />
          <Tooltip />
          <Bar dataKey="importance" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default FeatureImportanceChart;
