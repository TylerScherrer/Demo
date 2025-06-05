import React from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from "recharts";

const CompareChart = ({ data }) => {
  // data = [ { monthLabel: '2025-01', actual: 90000, predicted: 88000 }, ... ]

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <CartesianGrid stroke="#ccc" />
        <XAxis dataKey="monthLabel" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line
          type="monotone"
          dataKey="actual"
          stroke="#ff7300"
          strokeWidth={2}
          name="Actual"
        />
        <Line
          type="monotone"
          dataKey="predicted"
          stroke="#8884d8"
          strokeWidth={2}
          name="Predicted"
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default CompareChart;
