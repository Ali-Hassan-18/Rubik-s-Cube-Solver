import cv2
import numpy as np

def detect_cube_colors(image_bytes):
    """
    Advanced Hybrid Vision Engine: Collects raw multi-channel HSV and BGR color 
    profiles for each grid square to enable relative color space matching.
    """
    try:
        # Convert binary stream payload into an OpenCV BGR image matrix
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if img is None:
            return {"success": False, "error": "Decoding empty or corrupted image matrix data"}

        h, w, _ = img.shape
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        raw_profiles = []

        # Tightly aligned 5% margins matching your updated frontend crop canvas bounds
        margin_x = int(w * 0.05)
        margin_y = int(h * 0.05)
        grid_w = int((w - (2 * margin_x)) / 3)
        grid_h = int((h - (2 * margin_y)) / 3)
        
        # Traverse the 3x3 facelet array sequentially
        for row in range(3):
            for col in range(3):
                # Calculate absolute center coordinates for the current facelet
                cx = margin_x + (col * grid_w) + int(grid_w / 2)
                cy = margin_y + (row * grid_h) + int(grid_h / 2)
                
                # Boundary verification clamping
                cx = min(max(0, cx), w - 1)
                cy = min(max(0, cy), h - 1)
                
                # Extract a 9x9 kernel window around the coordinate to filter scratches/dust
                y_min = max(0, cy - 4)
                y_max = min(h, cy + 5)
                x_min = max(0, cx - 4)
                x_max = min(w, cx + 5)
                
                bgr_kernel = img[y_min:y_max, x_min:x_max]
                hsv_kernel = hsv_img[y_min:y_max, x_min:x_max]
                
                # Extract the robust median color spectrum values
                median_bgr = np.median(bgr_kernel, axis=(0, 1))
                median_hsv = np.median(hsv_kernel, axis=(0, 1))
                
                raw_profiles.append({
                    "bgr": [int(median_bgr[0]), int(median_bgr[1]), int(median_bgr[2])],
                    "hsv": [int(median_hsv[0]), int(median_hsv[1]), int(median_hsv[2])]
                })

        return {"success": True, "colors": raw_profiles}

    except Exception as e:
        return {"success": False, "error": f"Vision engine matrix tracking failure: {str(e)}"}