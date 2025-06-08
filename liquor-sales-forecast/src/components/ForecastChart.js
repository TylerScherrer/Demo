import React from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from "recharts";

export default function ForecastChart({ data }) {
  return (
    <div style={{ marginTop: "30px" }}>
      <h3>Forecast Chart</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="week" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="predicted" stroke="#8884d8" />
          <Line type="monotone" dataKey="upper" stroke="#82ca9d" strokeDasharray="5 5" />
          <Line type="monotone" dataKey="lower" stroke="#ff7f7f" strokeDasharray="5 5" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
