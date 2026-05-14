import React from 'react';
import '../styles/ColorGrid.css';

const COLOR_DISPLAY = {
  W: '#ffffff',
  Y: '#ffff00',
  R: '#ff0000',
  O: '#ffa500',
  B: '#0000ff',
  G: '#00aa00',
};

function ColorGrid({ faceColors, onColorClick, onColorSelect }) {
  return (
    <div className="color-grid">
      {faceColors.split('').map((color, index) => (
        <div
          key={index}
          className="grid-cell"
          style={{ backgroundColor: COLOR_DISPLAY[color] }}
          onClick={() => onColorClick(index)}
          title={`Click to cycle colors. Currently: ${color}`}
        />
      ))}
    </div>
  );
}

export default ColorGrid;
