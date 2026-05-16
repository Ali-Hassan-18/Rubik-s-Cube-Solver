import React, { useState } from 'react';
import '../styles/ImageUpload.css';

function ImageUpload({ onDetect, loading }) {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      setPreview(URL.createObjectURL(file));
      setError(null);
    }
  };

  // 🔥 CRITICAL FIX: Ab hum sara kaam App.jsx ke handleFaceScan pipeline ko handover kar rahe hain
  const handleUpload = () => {
    if (!image) {
      setError('Please select an image first');
      return;
    }

    if (onDetect) {
      // Yeh line chupke se file object ko App.jsx ke paas bhej degi
      onDetect(image);

      // Reset fields taake aglay face ki photo ke liye clean workspace milay
      setImage(null);
      setPreview(null);
      setError(null);
    } else {
      setError('System Error: Tracking callback is missing.');
    }
  };

  return (
    <div className="image-upload">
      <h2>Upload Cube Image</h2>
      <p className="instructions">
        Take a photo of your Rubik's cube and upload it. The solver will automatically
        detect the colors and solve it.
      </p>

      <div className="upload-area">
        <label htmlFor="image-input" className="upload-label">
          <span>📷 Click to choose image or drag and drop</span>
          <input
            id="image-input"
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            disabled={loading}
          />
        </label>

        {preview && (
          <div className="preview-container">
            <img src={preview} alt="Preview" className="preview-image" />
          </div>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="button-group">
        <button
          className="detect-btn"
          onClick={handleUpload}
          disabled={!image || loading}
        >
          {loading ? 'Detecting Matrix Configuration...' : 'Detect Colors & Save Side'}
        </button>
      </div>

      <div className="tips">
        <h4>Tips for best results:</h4>
        <ul>
          <li>Use good lighting conditions</li>
          <li>Place the cube flat on a surface</li>
          <li>Ensure all colors are clearly visible</li>
          <li>Avoid shadows and glare</li>
        </ul>
      </div>
    </div>
  );
}

export default ImageUpload;