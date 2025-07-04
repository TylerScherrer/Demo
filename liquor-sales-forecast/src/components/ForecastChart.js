import React from "react";
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Label
} from "recharts";

export default function ForecastChart({ data }) {
  // Prepare formatted data with type labels for tooltip clarity
  const formattedData = data.map((item) => ({
    ...item,
    label: `${item.type === "actual" ? "Actual" : "Forecast"}`,
    displayLabel: item.label || `Month ${item.month}`

  }));

  return (
    <div style={{ marginTop: "30px" }}>
      <h3 style={{ textAlign: "left" }}>Monthly Liquor Sales Forecast</h3>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={formattedData} margin={{ top: 10, right: 30, left: 20, bottom: 30 }}>
          <CartesianGrid stroke="#ccc" strokeDasharray="5 5" />
          <XAxis
            dataKey="displayLabel"
            angle={-35}
            textAnchor="end"
            interval={0}
            height={60}
            label={{ value: "Month", position: "insideBottomRight", offset: -10 }}
          />
          <YAxis
            label={{ value: "Sales ($)", angle: -90, position: "insideLeft", offset: -10 }}
            tickFormatter={(value) => `$${value.toLocaleString()}`}
          />
          <Tooltip
            formatter={(value, name) => [`$${value.toLocaleString()}`, name]}
            labelFormatter={(label) => label}

          />
          <Legend verticalAlign="top" height={36} />

          <Line
            type="monotone"
            dataKey="value"
            stroke="#2e86de"
            name="Sales"
            dot={{ r: 3 }}
            strokeWidth={2}
            strokeDasharray="0"
            isAnimationActive={false}
          />

          <Line
            type="monotone"
            dataKey="upper"
            stroke="#27ae60"
            name="Upper Bound"
            strokeDasharray="4 2"
            isAnimationActive={false}
          />

          <Line
            type="monotone"
            dataKey="lower"
            stroke="#e74c3c"
            name="Lower Bound"
            strokeDasharray="4 2"
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
