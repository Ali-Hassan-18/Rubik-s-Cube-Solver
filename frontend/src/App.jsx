import React, { useState } from 'react';
import CubeInput from './components/CubeInput';
import ImageUpload from './components/ImageUpload';
import SolutionDisplay from './components/SolutionDisplay';
import './App.css';

function App() {
  const [solution, setSolution] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState('manual'); // 'manual' or 'image'

  const handleSolve = (cubeState) => {
    setLoading(true);
    setError(null);
    setSolution(null);

    fetch('/api/solve', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ state: cubeState }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          setSolution(data);
        } else {
          setError(data.error || 'Failed to solve cube');
        }
      })
      .catch((err) => {
        setError('Error connecting to solver: ' + err.message);
      })
      .finally(() => setLoading(false));
  };

  const handleImageDetect = (detectedState) => {
    // Show detected state and allow user to confirm/adjust
    // Then proceed to solve
    handleSolve(detectedState);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎲 Rubik's Cube Solver</h1>
        <p>Solve your 3x3 Rubik's cube in seconds</p>
      </header>

      <div className="mode-selector">
        <button
          className={`mode-btn ${mode === 'manual' ? 'active' : ''}`}
          onClick={() => setMode('manual')}
        >
          Manual Input
        </button>
        <button
          className={`mode-btn ${mode === 'image' ? 'active' : ''}`}
          onClick={() => setMode('image')}
        >
          Image Detection
        </button>
      </div>

      <main className="App-main">
        {error && <div className="error-message">{error}</div>}

        {mode === 'manual' && (
          <CubeInput onSolve={handleSolve} loading={loading} />
        )}

        {mode === 'image' && (
          <ImageUpload onDetect={handleImageDetect} loading={loading} />
        )}

        {solution && <SolutionDisplay solution={solution} />}
      </main>

      <footer className="App-footer">
        <p>Built with React & Flask | Powered by Kociemba Algorithm</p>
      </footer>
    </div>
  );
}

export default App;
