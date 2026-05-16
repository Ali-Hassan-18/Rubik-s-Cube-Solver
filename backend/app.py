from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import sys

# Add solvers directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'solvers'))

from solvers.cube import Cube
from solvers.solver import solve, get_solver_info
from solvers.color_detector import detect_cube_colors

load_dotenv()

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

def translate_state_to_faces(state):
    """
    Translates a 54-char color string into a Kociemba-compatible face string.
    Identifies centers automatically to handle any physical cube orientation.
    """
    if len(state) != 54:
        raise ValueError(f"Cube state must be 54 characters, got {len(state)}")

    # Kociemba order: Up, Right, Front, Down, Left, Back
    # Centers live at the 5th sticker of each group
    center_indices = [4, 13, 22, 31, 40, 49]
    face_letters = ['U', 'R', 'F', 'D', 'L', 'B']
    
    mapping = {}
    for i, face in zip(center_indices, face_letters):
        color = state[i]
        if color in mapping:
            raise ValueError("Duplicate center colors detected. Each face must have a unique center color.")
        mapping[color] = face
    
    if len(mapping) < 6:
        raise ValueError("Could not map 6 unique faces. Please check your cube input layout.")

    return "".join([mapping[color] for color in state])

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "rubiks-cube-solver",
        "version": "1.0.0"
    })

@app.route('/api/solver-info', methods=['GET'])
def solver_info():
    """Get information about the solver tier."""
    return jsonify(get_solver_info())

@app.route('/api/solve', methods=['POST'])
def solve_cube():
    """
    Solve a cube optimally using its visual state orientation matrix.
    """
    try:
        data = request.get_json()
        if not data or 'state' not in data:
            return jsonify({"success": False, "error": "Missing 'state' field"}), 400

        # Translate input color mappings to standard spatial vectors
        try:
            translated_state = translate_state_to_faces(data['state'])
            cube = Cube(translated_state) 
        except ValueError as e:
            return jsonify({"success": False, "error": str(e)}), 400

        moves = solve(cube)
        return jsonify({
            "success": True,
            "solution": " ".join(moves),
            "moves": moves,
            "move_count": len(moves)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/validate-cube', methods=['POST'])
def validate_cube():
    """Validate structural legality of a given configuration string."""
    try:
        data = request.get_json()
        if not data or 'state' not in data:
            return jsonify({"valid": False, "error": "Missing 'state' field"}), 400

        try:
            translated = translate_state_to_faces(data['state'])
            Cube(translated)
            return jsonify({"valid": True})
        except ValueError as e:
            return jsonify({"valid": False, "error": str(e)})

    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

@app.route('/api/detect-colors', methods=['POST'])
def detect_colors():
    """Detect cube colors from an uploaded image file."""
    try:
        if 'image' not in request.files:
            return jsonify({"success": False, "error": "No image file provided"}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"success": False, "error": "No image selected"}), 400

        image_data = image_file.read()
        result = detect_cube_colors(image_data)

        if result.get("success"):
            return jsonify({
                "success": True,
                "colors": result.get("colors")
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Vision engine failed to classify grid values")
            }), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=5000)