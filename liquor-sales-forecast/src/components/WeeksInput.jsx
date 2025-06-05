import React from "react";

function WeeksInput({ weeks, setWeeks }) {
  return (
    <div>
      <label><strong>Weeks to Predict:</strong>{" "}</label>
      <input
        type="number"
        min={1}
        max={52}
        value={weeks}
        onChange={(e) => setWeeks(parseInt(e.target.value, 10))}
        style={{ width: "60px" }}
      />
    </div>
  );
}

export default WeeksInput;
