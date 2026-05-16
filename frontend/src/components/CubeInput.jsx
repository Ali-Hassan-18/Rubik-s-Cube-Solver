import React, { useState, useCallback } from 'react';
import ColorGrid from './ColorGrid';
import '../styles/CubeInput.css';

const FACES = ['U', 'R', 'F', 'D', 'L', 'B'];
const FACE_NAMES = {
  U: 'Up (Yellow)',
  R: 'Right (Blue)',
  F: 'Front (Orange)',
  D: 'Down (White)',
  L: 'Left (Green)',
  B: 'Back (Red)',
};
const COLOR_NAMES = {
  W: 'White',
  Y: 'Yellow',
  R: 'Red',
  O: 'Orange',
  B: 'Blue',
  G: 'Green',
};
const COLORS = ['W', 'Y', 'R', 'O', 'B', 'G'];
const COLOR_DISPLAY = {
  W: '#ffffff',
  Y: '#ffff00',
  R: '#ff0000',
  O: '#ffa500',
  B: '#0000ff',
  G: '#00aa00',
};

function CubeInput({ onSolve, loading }) {
  const [faces, setFaces] = useState({
    U: 'YYYYYYYYY',
    R: 'BBBBBBBBB',
    F: 'OOOOOOOOO',
    D: 'WWWWWWWWW',
    L: 'GGGGGGGGG',
    B: 'RRRRRRRRR',
  });

  const [selectedFace, setSelectedFace] = useState('U');

  const updateFaceColor = useCallback((faceKey, index, color) => {
    setFaces((prev) => {
      const newFace = prev[faceKey].split('');
      newFace[index] = color;
      return {
        ...prev,
        [faceKey]: newFace.join(''),
      };
    });
  }, []);

  const cycleColor = useCallback((faceKey, index) => {
    const current = faces[faceKey][index];
    const nextIdx = (COLORS.indexOf(current) + 1) % COLORS.length;
    updateFaceColor(faceKey, index, COLORS[nextIdx]);
  }, [faces, updateFaceColor]);

  const reset = useCallback(() => {
    setFaces({
      U: 'YYYYYYYYY',
      R: 'BBBBBBBBB',
      F: 'OOOOOOOOO',
      D: 'WWWWWWWWW',
      L: 'GGGGGGGGG',
      B: 'RRRRRRRRR',
    });
  }, []);

  const handleSolve = () => {
    // Combine all faces into a single state string
    const state = FACES.map((face) => faces[face]).join('');
    onSolve(state);
  };

  const buildCubeString = () => {
    return FACES.map((face) => faces[face]).join('');
  };

  return (
    <div className="cube-input">
      <h2>Enter Cube Colors</h2>
      <p className="instructions">
        Click on squares to cycle through colors. Select a face to edit, then click squares.
      </p>

      <div className="face-selector">
        {FACES.map((face) => (
          <button
            key={face}
            className={`face-btn ${selectedFace === face ? 'active' : ''}`}
            onClick={() => setSelectedFace(face)}
          >
            {face}: {FACE_NAMES[face]}
          </button>
        ))}
      </div>

      <div className="color-input-container">
        <div className="color-picker-panel">
          <h3>{FACE_NAMES[selectedFace]}</h3>
          <ColorGrid
            faceColors={faces[selectedFace]}
            onColorClick={(index) => cycleColor(selectedFace, index)}
            onColorSelect={(index, color) => updateFaceColor(selectedFace, index, color)}
          />
        </div>

        <div className="color-legend">
          <h4>Colors:</h4>
          <div className="legend-grid">
            {COLORS.map((color) => (
              <div key={color} className="legend-item">
                <div
                  className="color-box"
                  style={{ backgroundColor: COLOR_DISPLAY[color] }}
                />
                <span>{COLOR_NAMES[color]}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="button-group">
        <button
          className="solve-btn"
          onClick={handleSolve}
          disabled={loading}
        >
          {loading ? 'Solving...' : 'Solve Cube'}
        </button>
        <button className="reset-btn" onClick={reset} disabled={loading}>
          Reset to Solved
        </button>
        <button className="debug-btn" onClick={() => console.log(buildCubeString())}>
          Log State
        </button>
      </div>

      <div className="state-preview">
        <h4>Current State (Copy for debugging):</h4>
        <code>{buildCubeString()}</code>
      </div>
    </div>
  );
}

export default CubeInput;
