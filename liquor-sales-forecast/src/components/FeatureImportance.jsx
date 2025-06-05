// FeatureImportance.jsx

import React, { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid
} from "recharts";

// Custom Tooltip component to display explanation and controllable flag
function CustomTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) {
    return null;
  }
  const importanceValue = payload[0].value;
  const { desc, controllable } = payload[0].payload; // desc and controllable come from our metadata

  return (
    <div style={{ backgroundColor: "#fff", border: "1px solid #ccc", padding: 8 }}>
      <p style={{ margin: 0, fontWeight: "bold" }}>{label}</p>
      <p style={{ margin: 0 }}>Importance: {importanceValue.toFixed(4)}</p>
      {desc && (
        <p style={{ marginTop: 4, fontStyle: "italic" }}>{desc}</p>
      )}
      {controllable !== undefined && (
        <p style={{ marginTop: 2, fontWeight: "bold", color: controllable ? "green" : "gray" }}>
          {controllable ? "Manager-Controllable" : "Contextual Feature"}
        </p>
      )}
    </div>
  );
}

function FeatureImportance() {
  // We’ll maintain separate arrays for actionable vs contextual features.
  const [actionableData, setActionableData] = useState([]);
  const [contextualData, setContextualData] = useState([]);

  // Mapping for renaming technical features to friendly labels
  const renameMap = {
    rolling_mean_6: "6-Week Avg Sales",
    rolling_mean_3: "3-Week Avg Sales",
    Lag_12: "Sales Lag (12 Weeks)",
    sales_to_avg_ratio: "Sales vs. Store Avg Ratio",
    store_std_sales: "Store Sales Volatility",
    Month_sin: "Month (Seasonal Sine)",
    rolling_trend: "Recent Sales Trend",
    Month_cos: "Month (Seasonal Cos)",
    store_mean_sales: "Store Mean Sales"
  };

  // Metadata for each feature: friendly label, short explanation, and whether it's manager-controllable
  // For now, all are set as contextual (controllable: false), but you can add actionable features later.
  const featureMetadata = {
    "6-Week Avg Sales": {
      desc: "Short-term average of the last 6 weeks of sales.",
      controllable: false
    },
    "3-Week Avg Sales": {
      desc: "Recent average of the last 3 weeks—captures short-term momentum.",
      controllable: false
    },
    "Sales Lag (12 Weeks)": {
      desc: "Sales from 12 weeks ago, indicating seasonal patterns.",
      controllable: false
    },
    "Sales vs. Store Avg Ratio": {
      desc: "Comparison of current sales to the store’s historical average.",
      controllable: false
    },
    "Store Sales Volatility": {
      desc: "Variability in store sales over time.",
      controllable: false
    },
    "Month (Seasonal Sine)": {
      desc: "Seasonal signal from the sine component of the month.",
      controllable: false
    },
    "Month (Seasonal Cos)": {
      desc: "Seasonal signal from the cosine component of the month.",
      controllable: false
    },
    "Recent Sales Trend": {
      desc: "Direction of short-term sales movement.",
      controllable: false
    },
    "Store Mean Sales": {
      desc: "Historical average sales of the store.",
      controllable: false
    }
  };

  useEffect(() => {
    fetch("http://localhost:5000/feature_importance")
      .then((res) => res.json())
      .then((json) => {
        if (!json.feature_importances) return;
        
        // Separate the data into actionable and contextual arrays.
        const actionable = [];
        const contextual = [];
        
        json.feature_importances.forEach((item) => {
          // Rename using renameMap; fallback to the raw name if not found.
          const displayName = renameMap[item.feature] || item.feature;
          const meta = featureMetadata[displayName] || { desc: "", controllable: false };
          const newObj = {
            name: displayName,
            importance: item.importance,
            desc: meta.desc,
            controllable: meta.controllable
          };

          // For now, since we don't have actionable features, all will go to contextual.
          // If you later add actionable features (e.g., is_promotion), push them to actionable.
          if (newObj.controllable) {
            actionable.push(newObj);
          } else {
            contextual.push(newObj);
          }
        });

        // Optionally sort each array by importance
        contextual.sort((a, b) => b.importance - a.importance);
        actionable.sort((a, b) => b.importance - a.importance);

        setContextualData(contextual);
        setActionableData(actionable);
      })
      .catch((error) => {
        console.error("Error fetching feature importances:", error);
      });
  }, []);

  // Render two separate charts if actionable data exists.
  // Otherwise, only display the contextual features.
  return (
    <div>
      <h2>Model Feature Importances</h2>
      {actionableData.length > 0 && (
        <div style={{ marginBottom: "40px" }}>
          <h3>Actionable Factors</h3>
          <FeatureBarChart data={actionableData} />
        </div>
      )}
      {contextualData.length > 0 && (
        <div style={{ marginBottom: "40px" }}>
          <h3>Contextual (Model) Factors</h3>
          <FeatureBarChart data={contextualData} />
        </div>
      )}
    </div>
  );
}

// A sub-component to render a vertical bar chart for the given feature data
function FeatureBarChart({ data }) {
  const containerHeight = data.length > 0 ? data.length * 45 + 100 : 300;

  return (
    <div style={{ width: "100%", height: containerHeight }}>
      <ResponsiveContainer>
        <BarChart
          layout="vertical"
          data={data}
          margin={{ top: 20, right: 30, left: 200, bottom: 20 }}
          barCategoryGap="40%"
          barGap={5}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis type="number" />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fontSize: 12 }}
            width={160}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="importance" fill="#333" barSize={15} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default FeatureImportance;
