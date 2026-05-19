import React, { useState, useRef, useCallback } from 'react';
import '../styles/ImageUpload.css';

function ImageUpload({ onDetect, loading }) {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState(null);
  
  // Crop state with touch-tracking parameters
  const [cropBox, setCropBox] = useState({ x: 5, y: 15, size: 90 }); 
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  const imageRef = useRef(null);
  const containerRef = useRef(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      setPreview(URL.createObjectURL(file));
      setError(null);
      setCropBox({ x: 5, y: 15, size: 90 });
    }
  };

  // ── TOUCH & MOUSE DRAG HANDLERS ──────────────────────────────────────────
  const handlePointerDown = (e) => {
    setIsDragging(true);
    // Support both mouse clicks and mobile finger touches
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    setDragStart({ x: clientX, y: clientY });
  };

  const handlePointerMove = useCallback((e) => {
    if (!isDragging || !containerRef.current) return;
    
    // Prevent the screen from scrolling while the user is trying to drag the crop box
    if (e.cancelable) e.preventDefault(); 

    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;

    const deltaX = clientX - dragStart.x;
    const deltaY = clientY - dragStart.y;

    const container = containerRef.current.getBoundingClientRect();
    const deltaXPct = (deltaX / container.width) * 100;
    const deltaYPct = (deltaY / container.height) * 100;

    setCropBox((prev) => {
      // Prevent the box from being dragged outside the image boundaries
      let newX = Math.max(0, Math.min(prev.x + deltaXPct, 100 - prev.size));
      let newY = Math.max(0, Math.min(prev.y + deltaYPct, 100 - prev.size));
      return { ...prev, x: newX, y: newY };
    });

    setDragStart({ x: clientX, y: clientY });
  }, [isDragging, dragStart]);

  const handlePointerUp = () => {
    setIsDragging(false);
  };

  const handleSizeChange = (e) => {
    const newSize = parseInt(e.target.value);
    setCropBox((prev) => {
      // Auto-correct X and Y if expanding the size pushes the box out of bounds
      let safeX = prev.x;
      let safeY = prev.y;
      if (safeX + newSize > 100) safeX = 100 - newSize;
      if (safeY + newSize > 100) safeY = 100 - newSize;
      return { x: safeX, y: safeY, size: newSize };
    });
  };

  // ── CANVAS SLICING ENGINE ────────────────────────────────────────────────
  const executeNativeCanvasCrop = () => {
    if (!image || !preview) return;

    const imgElement = imageRef.current;
    const frameElement = containerRef.current.querySelector('.visual-crop-frame');
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    const imgRect = imgElement.getBoundingClientRect();
    const frameRect = frameElement.getBoundingClientRect();

    const scaleX = imgElement.naturalWidth / imgRect.width;
    const scaleY = imgElement.naturalHeight / imgRect.height;

   // Determine exact pixel coordinates mapping directly to the source file
    let cropX = (frameRect.left - imgRect.left) * scaleX;
    let cropY = (frameRect.top - imgRect.top) * scaleY;
    let cropWidth = frameRect.width * scaleX;
    
    // 📱 MOBILE FIX: Ignore frameRect.height which contains sub-pixel rectangular rounding errors. 
    // Force a flawless 1:1 mathematical square pixel slice based purely on the width.
    let cropHeight = cropWidth; 

    // Dynamic Boundary Guard: Clamp values inside the natural source image dimensions
    cropX = Math.max(0, Math.min(cropX, imgElement.naturalWidth));
    cropY = Math.max(0, Math.min(cropY, imgElement.naturalHeight));
    cropWidth = Math.min(cropWidth, imgElement.naturalWidth - cropX);
    cropHeight = Math.min(cropHeight, imgElement.naturalHeight - cropY);

    canvas.width = 400;
    canvas.height = 400;

    ctx.drawImage(
      imgElement,
      cropX, cropY, cropWidth, cropHeight, 
      0, 0, 400, 400
    );

    canvas.toBlob((blob) => {
      if (blob) {
        const croppedFile = new File([blob], "cropped_face.png", { type: "image/png" });
        onDetect(croppedFile);
        
        setImage(null);
        setPreview(null);
        setError(null);
      } else {
        setError("Cropping engine failed to slice pixel array components.");
      }
    }, 'image/png');
  };

  return (
    <div className="image-upload">
      <h2>Capture / Scan Cube Face</h2>
      <p className="instructions">
        Upload or take a snapshot. <b>Drag the yellow box with your finger</b> to center it over the cube, and use the slider to zoom.
      </p>

      <div className="upload-area">
        {!preview ? (
          <label htmlFor="image-input" className="upload-label">
            <span>📷 Tap to Open Mobile Camera</span>
            <input
              id="image-input"
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handleImageChange}
              disabled={loading}
            />
          </label>
        ) : (
          <div 
            className="crop-workspace-container" 
            ref={containerRef}
            onMouseMove={handlePointerMove}
            onTouchMove={handlePointerMove}
            onMouseUp={handlePointerUp}
            onMouseLeave={handlePointerUp}
            onTouchEnd={handlePointerUp}
          >
            <img 
              src={preview} 
              alt="Workspace Track" 
              ref={imageRef}
              className="preview-image" 
            />
            {/* Draggable Frame Layer */}
            <div 
              className="visual-crop-frame"
              onMouseDown={handlePointerDown}
              onTouchStart={handlePointerDown}
              style={{
                position: 'absolute',
                border: '3px solid #fab12f',
                boxShadow: '0 0 0 4000px rgba(0, 0, 0, 0.65)', 
                borderRadius: '8px',
                left: `${cropBox.x}%`,
                top: `${cropBox.y}%`,
                width: `${cropBox.size}%`,
                aspectRatio: '1 / 1', 
                cursor: 'move',
                touchAction: 'none' // Prevents the browser from zooming the webpage when touching the box
              }}
            >
              <div className="drag-indicator">✥</div>
            </div>
          </div>
        )}
      </div>

      {preview && (
        <div className="crop-control-console">
          <label className="control-label">Zoom Matrix Size</label>
          <input 
            type="range" 
            className="modern-slider"
            min="30" 
            max="100" 
            value={cropBox.size} 
            onChange={handleSizeChange}
          />
        </div>
      )}

      {error && <div className="error-message">{error}</div>}

      <div className="button-group">
        {preview ? (
          <>
            <button className="detect-btn active-crop" onClick={executeNativeCanvasCrop} disabled={loading}>
              {loading ? 'Analyzing...' : 'Confirm Crop & Scan'}
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