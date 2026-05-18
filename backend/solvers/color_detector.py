import cv2
import numpy as np

def get_color_name(h, s, v):
    """Maps raw HSV pixel values to standard Rubik's cube color characters."""
    # Resilient color boundaries optimized for standard plastic cube shades
    if s < 45 and v > 130: return 'W'      # White (Low saturation, high reflection)
    if h < 8 or h > 168:                   # Red wraps around the 0/180 boundary
        return 'O' if v < 120 else 'R'     # Value threshold separate deep red from orange
    if 8 <= h < 22: return 'O'             # Orange
    if 22 <= h < 38: return 'Y'            # Yellow
    if 38 <= h < 86: return 'G'            # Green
    if 86 <= h < 135: return 'B'           # Blue
    return 'W'                             # Deflation safety boundary

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