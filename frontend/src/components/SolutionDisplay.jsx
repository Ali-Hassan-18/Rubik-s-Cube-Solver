import React from 'react';
import '../styles/SolutionDisplay.css';

function SolutionDisplay({ solution }) {
  const { moves, move_count, solved } = solution;

  if (solved) {
    return (
      <div className="solution-display">
        <div className="solved-message">
          <h3>🎉 Cube Already Solved!</h3>
          <p>Your cube is already in the solved state.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="solution-display">
      <h3>Solution Found!</h3>
      <div className="move-count">
        <p>
          <strong>Moves needed: {move_count}</strong>
          {move_count <= 20 && ' (Optimal!)'}
        </p>
      </div>

      <div className="moves-list">
        <h4>Steps to solve:</h4>
        <div className="moves-grid">
          {moves.map((move, index) => (
            <div key={index} className="move-item">
              <span className="move-number">{index + 1}</span>
              <span className="move-notation">{move}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="move-legend">
        <h4>Move Notation Guide:</h4>
        <div className="notation-table">
          <div className="notation-row">
            <span><strong>U, D, L, R, F, B</strong> - Face rotations</span>
          </div>
          <div className="notation-row">
            <span><strong>X'</strong> - Counterclockwise rotation</span>
          </div>
          <div className="notation-row">
            <span><strong>X2</strong> - 180-degree rotation</span>
          </div>
        </div>
      </div>

      <div className="instructions">
        <h4>How to use these moves:</h4>
        <ol>
          <li>Hold your cube with the face label facing you</li>
          <li>Perform each move in order from the list above</li>
          <li>U = Up face (clockwise when looking at it)</li>
          <li>D = Down face | L = Left | R = Right | F = Front | B = Back</li>
          <li>Add a ' (prime) mark to rotate counterclockwise</li>
          <li>Add a 2 to rotate 180 degrees</li>
        </ol>
      </div>

      <button
        className="copy-btn"
        onClick={() => navigator.clipboard.writeText(moves.join(' '))}
      >
        📋 Copy All Moves
      </button>
    </div>
  );
}

export default SolutionDisplay;
