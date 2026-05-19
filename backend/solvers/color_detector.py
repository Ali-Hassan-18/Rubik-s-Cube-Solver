import cv2
import numpy as np

def get_color_name(h, s, v):
    """Maps raw HSV pixel values to standard Rubik's cube color characters."""
    # 📱 THE 'AWB SHADOW' FIX:
    # Phone cameras inject blue into shadows to fix warm lighting (Auto-White Balance).
    # We drastically drop the 'Value' (brightness) threshold for White down to 60
    # and raise the Saturation allowance so dark-grey shadows are caught as White.
    
    if s < 65 and v > 60: return 'W'       # Catches deep, blue-tinted shadows on white stickers
    if h < 11 or h > 160: return 'R'       # Red hue wrap-around
    if 11 <= h < 25: return 'O'            # Safely isolated Orange band
    if 25 <= h < 42: return 'Y'            # Yellow
    if 42 <= h < 88: return 'G'            # Green (Expanded slightly to prevent cyan-bleed)
    if 88 <= h < 145: return 'B'           # Blue
    return 'W'                             # Safety fallback

def get_neighborhood_median_hsv(hsv_img, cx, cy, radius=4):
    """
    AI Kernel Sampler: Extracts a 9x9 matrix window around the center point
    and computes the median value to completely ignore scratches, logos, and dust.
    """
    h, w, _ = hsv_img.shape
    
    y_min = max(0, cy - radius)
    y_max = min(h, cy + radius + 1)
    x_min = max(0, cx - radius)
    x_max = min(w, cx + radius + 1)
    
    # Extract the pixel window region
    kernel_region = hsv_img[y_min:y_max, x_min:x_max]
    
    # Compute median across both dimensions to eliminate outlier anomalies
    median_hsv = np.median(kernel_region, axis=(0, 1))
    return median_hsv

def detect_cube_colors(image_bytes):
    """
    Advanced Hybrid Vision Engine: Slices the camera frame into a geometric 3x3 layout
    optimized for edge-to-edge square cropped canvas elements.
    """
    try:
        # Convert binary stream payload into an OpenCV BGR image matrix
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if img is None:
            return {"success": False, "error": "Decoding empty or corrupted image matrix data"}

        h, w, _ = img.shape
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        detected_sequence = []

        # FIX: Reduce margins from 18% down to 5%. Because the frontend crop tool
        # isolates the face frame tightly, we only need a minor 5% padding to 
        # stay clear of the outer plastic bevel edges.
        margin_x = int(w * 0.05)
        margin_y = int(h * 0.05)
        grid_w = int((w - (2 * margin_x)) / 3)
        grid_h = int((h - (2 * margin_y)) / 3)
        
        # Traverse the grid layout sequentially (3x3 grid)
        for row in range(3):
            for col in range(3):
                # Calculate the center point coordinates of each grid cell
                cx = margin_x + (col * grid_w) + int(grid_w / 2)
                cy = margin_y + (row * grid_h) + int(grid_h / 2)
                
                # Prevent bounding edge overflow coordinates
                cx = min(max(0, cx), w - 1)
                cy = min(max(0, cy), h - 1)
                
                # Extract clean HSV data via neighborhood kernel window
                robust_hsv = get_neighborhood_median_hsv(hsv_img, cx, cy, radius=4)
                
                color_token = get_color_name(robust_hsv[0], robust_hsv[1], robust_hsv[2])
                detected_sequence.append(color_token)

        final_face_string = "".join(detected_sequence)
        return {"success": True, "colors": final_face_string}

    except Exception as e:
        return {"success": False, "error": f"Vision tracking fatal exception: {str(e)}"}