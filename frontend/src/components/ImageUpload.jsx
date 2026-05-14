import React, { useState } from 'react';
import '../styles/ImageUpload.css';

function ImageUpload({ onDetect, loading }) {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [detectedColors, setDetectedColors] = useState(null);
  const [error, setError] = useState(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      setPreview(URL.createObjectURL(file));
      setError(null);
      setDetectedColors(null);
    }
  };

  const handleUpload = async () => {
    if (!image) {
      setError('Please select an image first');
      return;
    }

    const formData = new FormData();
    formData.append('image', image);

    try {
      const response = await fetch('/api/detect-colors', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        setDetectedColors(data.colors);
        // Pass the detected state to solve
        const state = Object.values(data.colors).join('');
        onDetect(state);
      } else {
        setError(data.error || 'Failed to detect colors');
      }
    } catch (err) {
      setError('Error uploading image: ' + err.message);
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

      {detectedColors && (
        <div className="detected-colors">
          <h3>Detected Colors:</h3>
          <div className="faces-display">
            {Object.entries(detectedColors).map(([face, colors]) => (
              <div key={face} className="face-display">
                <h4>Face {face}</h4>
                <div className="colors-grid">
                  {colors.split('').map((color, idx) => (
                    <div key={idx} className="color-dot" title={color} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="button-group">
        <button
          className="detect-btn"
          onClick={handleUpload}
          disabled={!image || loading}
        >
          {loading ? 'Detecting...' : 'Detect Colors & Solve'}
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
