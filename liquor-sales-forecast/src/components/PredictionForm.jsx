import React, { useState } from 'react';
import axios from 'axios';

const PredictionForm = () => {
  const [store, setStore] = useState('');
  const [prediction, setPrediction] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:5000/predict', {
        store: parseInt(store),
      });
      setPrediction(response.data.prediction[0]);
    } catch (error) {
      console.error('Prediction error:', error);
      setPrediction('Error fetching prediction');
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <label>
          Store Number:
          <input
            type="number"
            value={store}
            onChange={(e) => setStore(e.target.value)}
            required
            style={{ marginLeft: '10px' }}
          />
        </label>
        <button type="submit" style={{ marginLeft: '10px' }}>Predict</button>
      </form>

      {prediction !== null && (
        <p style={{ marginTop: '20px' }}>
          📈 Predicted Sales: <strong>{prediction}</strong>
        </p>
      )}
    </div>
  );
};

export default PredictionForm;
