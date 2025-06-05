import React from "react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Line
} from "recharts";

const ForecastChart = ({ data }) => {
  // data = [ 
  //   { week: 1, predicted: 82000, upper: 87000, lower: 77000 },
  //   { week: 2, predicted: 81000, upper: 86000, lower: 76000 },
  //   ...
  // ]

  return (
    <ResponsiveContainer width="100%" height={400}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="confidenceBand" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#8884d8" stopOpacity={0.3} />
            <stop offset="100%" stopColor="#8884d8" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="#ccc" />
        <XAxis dataKey="week" />
        <YAxis />
        <Tooltip />
        <Legend />
        
        {/* Upper band */}
        <Area
          type="monotone"
          dataKey="upper"
          stroke={false}
          fill="url(#confidenceBand)"
        />
        {/* Lower band */}
        <Area
          type="monotone"
          dataKey="lower"
          stroke={false}
          fill="url(#confidenceBand)"
        />
        
        {/* Middle line: predicted */}
        <Line
          type="monotone"
          dataKey="predicted"
          stroke="#8884d8"
          strokeWidth={2}
          name="Predicted Sales"
          dot={{ r: 2 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
};

export default ForecastChart;
