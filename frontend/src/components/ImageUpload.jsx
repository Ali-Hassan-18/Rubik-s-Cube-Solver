import React, { useState, useRef } from 'react';
import '../styles/ImageUpload.css';

function ImageUpload({ onDetect, loading }) {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState(null);
  
  // Normalized positioning states for tracking the selector element
  const [cropBox, setCropBox] = useState({ x: 0, y: 0, size: 90 }); 
  const imageRef = useRef(null);
  const containerRef = useRef(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      setPreview(URL.createObjectURL(file));
      setError(null);
      setCropBox({ x: 5, y: 15, size: 90 }); // Default initial center placement
    }
  };

  const executeNativeCanvasCrop = () => {
    if (!image || !preview) return;

    const imgElement = imageRef.current;
    const frameElement = containerRef.current.querySelector('.visual-crop-frame');
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    // Get the exact real-time rendered dimensions and positions from the screen DOM
    const imgRect = imgElement.getBoundingClientRect();
    const frameRect = frameElement.getBoundingClientRect();

    // Calculate real-time scaling factors between rendered layout and natural raw pixels
    const scaleX = imgElement.naturalWidth / imgRect.width;
    const scaleY = imgElement.naturalHeight / imgRect.height;

    // Determine exact pixel coordinates mapping directly to the source file
    let cropX = (frameRect.left - imgRect.left) * scaleX;
    let cropY = (frameRect.top - imgRect.top) * scaleY;
    let cropWidth = frameRect.width * scaleX;
    let cropHeight = frameRect.height * scaleY;

    // Dynamic Boundary Guard: Clamp values inside the natural source image dimensions to prevent clipping crashes
    cropX = Math.max(0, Math.min(cropX, imgElement.naturalWidth));
    cropY = Math.max(0, Math.min(cropY, imgElement.naturalHeight));
    cropWidth = Math.min(cropWidth, imgElement.naturalWidth - cropX);
    cropHeight = Math.min(cropHeight, imgElement.naturalHeight - cropY);

    // Enforce stand-alone 400x400 matrices output for high-performance OpenCV parsing
    canvas.width = 400;
    canvas.height = 400;

    ctx.drawImage(
      imgElement,
      cropX, cropY, cropWidth, cropHeight, // Authentic unwarped coordinates
      0, 0, 400, 400
    );

    canvas.toBlob((blob) => {
      if (blob) {
        const croppedFile = new File([blob], "cropped_face.png", { type: "image/png" });
        onDetect(croppedFile);
        
        // Flush states to clear memory buffers for the next side scan
        setImage(null);
        setPreview(null);
        setError(null);
      } else {
        setError("Cropping engine failed to slice pixel array components.");
      }
    }, 'image/png');
  };

  const adjustCropBoxDimensions = (dimension, change) => {
    setCropBox((prev) => {
      const updated = { ...prev };
      if (dimension === 'size') {
        updated.size = Math.min(Math.max(20, prev.size + change), 100);
      } else if (dimension === 'x') {
        updated.x = Math.min(Math.max(0, prev.x + change), 100 - prev.size);
      } else if (dimension === 'y') {
        updated.y = Math.min(Math.max(0, prev.y + change), 100);
      }
      return updated;
    });
  };

  return (
    <div className="image-upload">
      <h2>Capture / Scan Cube Face</h2>
      <p className="instructions">
        Upload or take a face snapshot. Adjust the position controls below to frame the 
        cube face cleanly inside the yellow selection square.
      </p>

      <div className="upload-area">
        {!preview ? (
          <label htmlFor="image-input" className="upload-label">
            <span>📷 Click to Upload Face Image</span>
            <input
              id="image-input"
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              disabled={loading}
            />
          </label>
        ) : (
          <div className="crop-workspace-container" ref={containerRef} style={{ position: 'relative', display: 'inline-block', width: '100%', maxWidth: '340px' }}>
            <img 
              src={preview} 
              alt="Workspace Track" 
              ref={imageRef}
              className="preview-image" 
              style={{ width: '100%', display: 'block', borderRadius: '12px' }}
            />
            {/* Visual Crop Overlay Frame Layer */}
            <div 
              className="visual-crop-frame"
              style={{
                position: 'absolute',
                border: '3px solid #fab12f',
                boxShadow: '0 0 0 4000px rgba(0, 0, 0, 0.55)', // Dim out peripheral background area
                borderRadius: '8px',
                left: `${cropBox.x}%`,
                top: `${cropBox.y}%`,
                width: `${cropBox.size}%`,
                aspectRatio: '1 / 1', // FIX: Forces the display frame to remain a perfect un-squished square
                pointerEvents: 'none',
                transition: 'all 0.1s ease-out'
              }}
            />
          </div>
        )}
      </div>

      {preview && (
        <div className="crop-control-console">
          <label className="control-label">Position Alignment Matrix</label>
          <div className="control-row-grid">
            <button onClick={() => adjustCropBoxDimensions('y', -4)}>▲ Up</button>
            <button onClick={() => adjustCropBoxDimensions('y', 4)}>▼ Down</button>
            <button onClick={() => adjustCropBoxDimensions('x', -4)}>◀ Left</button>
            <button onClick={() => adjustCropBoxDimensions('x', 4)}>▶ Right</button>
          </div>
          <div className="control-row-grid size-row">
            <button onClick={() => adjustCropBoxDimensions('size', 4)}>🔍 Zoom Out</button>
            <button onClick={() => adjustCropBoxDimensions('size', -4)}>🔍 Zoom In</button>
          </div>
        </div>
      )}

      {error && <div className="error-message">{error}</div>}

      <div className="button-group">
        {preview ? (
          <>
            <button className="detect-btn active-crop" onClick={executeNativeCanvasCrop} disabled={loading}>
              {loading ? 'Analyzing Contours...' : 'Confirm Crop & Process Face'}
            </button>
            <button className="reset-btn cancel-btn" onClick={() => { setImage(null); setPreview(null); }} disabled={loading}>
              Retake Photo
            </button>
          </>
        ) : (
          <div className="fallback-file-prompt">
            <label htmlFor="fallback-file" className="fallback-link">Choose a file from local directory</label>
            <input type="file" id="fallback-file" accept="image/*" onChange={handleImageChange} style={{ display: 'none' }} />
          </div>
        )}
      </div>
    </div>
  );
}

export default ImageUpload;