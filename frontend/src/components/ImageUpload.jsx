import React, { useState, useRef, useCallback } from 'react';
import '../styles/ImageUpload.css';

function ImageUpload({ onDetect, loading }) {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState(null);
  
  // Percent-based layout tracing states to remain container-agnostic
  const [cropBox, setCropBox] = useState({ x: 10, y: 10, size: 80 }); 
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
      setCropBox({ x: 15, y: 15, size: 70 });
    }
  };

  // ── TOUCH & MOUSE DRAG TRACKING TENSORS ──────────────────────────────────
  const handlePointerDown = (e) => {
    setIsDragging(true);
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    setDragStart({ x: clientX, y: clientY });
  };

  const handlePointerMove = useCallback((e) => {
    if (!isDragging || !containerRef.current || !imageRef.current) return;
    
    if (e.cancelable) e.preventDefault(); 

    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;

    const deltaX = clientX - dragStart.x;
    const deltaY = clientY - dragStart.y;

    const imgElement = imageRef.current;
    const renderW = imgElement.clientWidth;
    const renderH = imgElement.clientHeight;

    const deltaXPct = (deltaX / renderW) * 100;
    const deltaYPct = (deltaY / renderH) * 100;

    setCropBox((prev) => {
      // Scale height threshold limits accurately relative to non-square layouts
      const boxHeightPct = (prev.size * renderW) / renderH;
      
      let newX = Math.max(0, Math.min(prev.x + deltaXPct, 100 - prev.size));
      let newY = Math.max(0, Math.min(prev.y + deltaYPct, 100 - boxHeightPct));
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
      if (!imageRef.current) return prev;
      const renderW = imageRef.current.clientWidth;
      const renderH = imageRef.current.clientHeight;
      const boxHeightPct = (newSize * renderW) / renderH;

      let safeX = Math.min(prev.x, 100 - newSize);
      let safeY = Math.min(prev.y, 100 - boxHeightPct);
      return { x: safeX, y: safeY, size: newSize };
    });
  };

  // ── MATH MATRICES CANVAS CROP ENGINE ──────────────────────────────────────
  const executeNativeCanvasCrop = () => {
    if (!image || !preview || !imageRef.current) return;

    const imgElement = imageRef.current;
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    const renderW = imgElement.clientWidth;
    const renderH = imgElement.clientHeight;

    const scaleX = imgElement.naturalWidth / renderW;
    const scaleY = imgElement.naturalHeight / renderH;

    // Map percentage vectors directly to raw unpadded source pixels
    const cropX = (cropBox.x / 100) * renderW * scaleX;
    const cropY = (cropBox.y / 100) * renderH * scaleY;
    
    // Scale widths and heights uniformly using the source aspect ratio
    const cropWidth = (cropBox.size / 100) * renderW * scaleX;
    const cropHeight = (cropBox.size / 100) * renderW * scaleY;

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
        Drag the yellow window directly over the cube face using your finger. Use the scale slider below to match boundaries perfectly.
      </p>

      <div className="upload-area" style={{ overflow: 'hidden', borderRadius: '12px' }}>
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
            style={{ position: 'relative', display: 'block', width: '100%', maxWidth: '340px', margin: '0 auto' }}
          >
            <img 
              src={preview} 
              alt="Workspace Track" 
              ref={imageRef}
              className="preview-image" 
              style={{ width: '100%', height: 'auto', display: 'block', borderRadius: '12px' }}
            />
            {/* Aspect-Ratio Guarded Overlay Frame Box */}
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
                touchAction: 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <div className="drag-indicator" style={{ color: 'white', fontSize: '1.5rem', opacity: 0.7, userSelect: 'none', pointerEvents: 'none' }}>✥</div>
            </div>
          </div>
        )}
      </div>

      {preview && (
        <div className="crop-control-console">
          <label className="control-label">Adjust Target Scale Window</label>
          <input 
            type="range" 
            className="modern-slider"
            min="25" 
            max="95" 
            value={cropBox.size} 
            onChange={handleSizeChange}
            style={{ width: '100%', margin: '10px 0' }}
          />
        </div>
      )}

      {error && <div className="error-message">{error}</div>}

      <div className="button-group">
        {preview ? (
          <>
            <button className="detect-btn active-crop" onClick={executeNativeCanvasCrop} disabled={loading}>
              {loading ? 'Analyzing Matrix...' : 'Confirm Crop & Process Face'}
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