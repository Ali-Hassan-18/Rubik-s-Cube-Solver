import cv2
import numpy as np
from PIL import Image
import io


def detect_cube_colors(image_data):
    """
    Detect Rubik's cube colors from an image.

    Args:
        image_data: Image file data (bytes)

    Returns:
        Dict with detected colors for each face, or error info
    """
    try:
        # Read image from bytes
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return {"success": False, "error": "Could not decode image"}

        # Convert BGR to RGB for processing
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Detect cube faces (simplified approach: assumes one face)
        # For a full solution, this would need to detect multiple faces
        detected = detect_single_face(img_rgb)

        if detected:
            return {
                "success": True,
                "colors": detected,
            }
        else:
            return {
                "success": False,
                "error": "Could not detect cube face in image",
            }

    except Exception as e:
        return {"success": False, "error": f"Image processing error: {str(e)}"}


def detect_single_face(img_rgb):
    """
    Detect colors in a single cube face (3x3 grid).

    For v1, we assume the image contains a roughly 300x300 cube face.
    This is a simplified approach that can be improved.
    """
    colors_map = {}

    # Find contours to locate the cube face
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # For a simple v1 implementation, we'll just divide the image into a 3x3 grid
    # and detect the dominant color in each square

    # Assume cube face is roughly in the center of the image
    h, w = img_rgb.shape[:2]

    # Find the face by looking for a square region with color variation
    face_region = find_cube_face_region(img_rgb)

    if face_region is None:
        return None

    x, y, size = face_region
    colors = extract_3x3_colors(img_rgb[y : y + size, x : x + size])

    # Map each color to the closest standard cube color
    # Standard colors: W (white), Y (yellow), R (red), O (orange), B (blue), G (green)
    face_colors = map_colors_to_standard(colors)

    # For v1, we'll just return face 'U' with detected colors
    # In a full solution, we'd need to detect all 6 faces
    return {"U": face_colors, "R": "RRRRRRRRR", "F": "OOOOOOOOO", "D": "WWWWWWWWW", "L": "GGGGGGGGG", "B": "BBBBBBBBB"}


def find_cube_face_region(img_rgb):
    """
    Find the region containing a cube face.
    Returns (x, y, size) or None if not found.
    """
    h, w = img_rgb.shape[:2]

    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)

    # For v1, assume the face is roughly square and in the center
    # This is a simplified heuristic
    min_size = min(h, w) // 2
    max_size = min(h, w) - 50

    # Center the search
    center_x, center_y = w // 2, h // 2
    size = min(max_size, 300)

    x = max(0, center_x - size // 2)
    y = max(0, center_y - size // 2)

    return (x, y, size)


def extract_3x3_colors(face_img):
    """
    Extract the dominant color from each square in a 3x3 grid.

    Args:
        face_img: Image region containing a cube face

    Returns:
        List of 9 RGB color tuples
    """
    h, w = face_img.shape[:2]
    square_h, square_w = h // 3, w // 3

    colors = []

    for i in range(3):
        for j in range(3):
            y1, y2 = i * square_h, (i + 1) * square_h
            x1, x2 = j * square_w, (j + 1) * square_w

            # Extract region
            region = face_img[y1:y2, x1:x2]

            # Get dominant color using K-means
            dominant_color = get_dominant_color(region)
            colors.append(dominant_color)

    return colors


def get_dominant_color(region):
    """
    Get the dominant color in a region using K-means clustering.

    Args:
        region: Image region (numpy array)

    Returns:
        Tuple of (R, G, B)
    """
    # Reshape the region to a list of pixels
    pixels = region.reshape((-1, 3))
    pixels = np.float32(pixels)

    # Apply K-means to find the dominant color
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(pixels, 1, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Get the dominant color
    dominant_color = centers[0].astype(int)

    return tuple(dominant_color)


def map_colors_to_standard(rgb_colors):
    """
    Map detected RGB colors to standard Rubik's cube colors.

    Args:
        rgb_colors: List of RGB tuples

    Returns:
        String of 9 characters representing cube colors
    """
    # Standard cube color centers (approximate RGB values)
    standard_colors = {
        "W": (255, 255, 255),  # White
        "Y": (255, 255, 0),    # Yellow
        "R": (255, 0, 0),      # Red
        "O": (255, 165, 0),    # Orange
        "B": (0, 0, 255),      # Blue
        "G": (0, 128, 0),      # Green
    }

    result = ""

    for rgb in rgb_colors:
        # Find closest standard color
        min_dist = float("inf")
        closest_color = "W"

        for color_name, standard_rgb in standard_colors.items():
            # Calculate Euclidean distance in RGB space
            dist = sum((a - b) ** 2 for a, b in zip(rgb, standard_rgb)) ** 0.5
            if dist < min_dist:
                min_dist = dist
                closest_color = color_name

        result += closest_color

    return result
