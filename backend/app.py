from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import sys

# Add solvers directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'solvers'))

from cube import Cube
from solver import solve, get_solver_info
from beginner_solver import solve_beginner, get_beginner_solver_info
from color_detector import detect_cube_colors

load_dotenv()

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/api/*": {"origins": "*"}})


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
    """Get information about the solver."""
    return jsonify(get_solver_info())


@app.route('/api/solve', methods=['POST'])
def solve_cube():
    try:
        data = request.get_json()
        state = data['state'] # This is the color string: "BBGGYYY..."

        # 1. IDENTIFY CENTERS (The 5th sticker of each 9-block)
        # Kociemba order: U, R, F, D, L, B
        centers = {
            state[4]:  'U',
            state[13]: 'R',
            state[22]: 'F',
            state[31]: 'D',
            state[40]: 'L',
            state[49]: 'B'
        }

        if len(centers) < 6:
            return jsonify({"success": False, "error": "Duplicate center colors detected"}), 400

        # 2. TRANSLATE COLORS TO FACES
        # Example: If state[4] is 'Y', every 'Y' in the string becomes 'U'
        translated_state = "".join([centers[color] for color in state])

        # 3. NOW PROCEED WITH THE TRANSLATED STRING
        try:
            # Update Cube class to validate U, R, F, D, L, B instead of colors
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


@app.route('/api/solve-beginner', methods=['POST'])
def solve_cube_beginner():
    """Solve cube using beginner-friendly layer-by-layer method."""
    try:
        data = request.get_json()
        state = data['state']

        # 1. IDENTIFY CENTERS (The 5th sticker of each 9-block)
        # Kociemba order: U, R, F, D, L, B
        centers = {
            state[4]:  'U',
            state[13]: 'R',
            state[22]: 'F',
            state[31]: 'D',
            state[40]: 'L',
            state[49]: 'B'
        }

        if len(centers) < 6:
            return jsonify({"success": False, "error": "Duplicate center colors detected"}), 400

        # 2. TRANSLATE COLORS TO FACES
        translated_state = "".join([centers[color] for color in state])

        # 3. PROCEED WITH THE TRANSLATED STRING
        try:
            cube = Cube(translated_state)
        except ValueError as e:
            return jsonify({"success": False, "error": str(e)}), 400

        moves = solve_beginner(cube)
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
    """
    Validate a cube state.

    Request JSON:
    {
        "state": "UUUUU..." (54 characters)
    }

    Response JSON:
    {
        "valid": true/false,
        "error": "error message if invalid"
    }
    """
    try:
        data = request.get_json()
        if not data or 'state' not in data:
            return jsonify({"valid": False, "error": "Missing 'state' field"}), 400

        try:
            Cube(data['state'])
            return jsonify({"valid": True})
        except ValueError as e:
            return jsonify({"valid": False, "error": str(e)})

    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500


@app.route('/api/cube-faces', methods=['POST'])
def cube_from_faces():
    """
    Create a cube state from individual face colors.

    Request JSON:
    {
        "faces": {
            "U": "WWWWWWWWW",
            "R": "RRRRRRRRR",
            ...
        }
    }

    Response JSON:
    {
        "success": true,
        "state": "UUUUU...",
        "faces": {...}
    }
    """
    try:
        data = request.get_json()
        if not data or 'faces' not in data:
            return jsonify({"success": False, "error": "Missing 'faces' field"}), 400

        try:
            cube = Cube.from_face_colors(data['faces'])
            return jsonify({
                "success": True,
                "state": cube.get_state(),
                "faces": cube.to_face_colors()
            })
        except ValueError as e:
            return jsonify({"success": False, "error": str(e)}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/detect-colors', methods=['POST'])
def detect_colors():
    """
    Detect cube colors from an uploaded image.

    Request: multipart/form-data with 'image' field
    Response JSON:
    {
        "success": true/false,
        "colors": {
            "U": "YYYYYYYYY",
            "R": "RRRRRRRRR",
            ...
        },
        "error": "error message if failed"
    }
    """
    try:
        if 'image' not in request.files:
            return jsonify({"success": False, "error": "No image file provided"}), 400

        image_file = request.files['image']

        if image_file.filename == '':
            return jsonify({"success": False, "error": "No image selected"}), 400

        # Read image data
        image_data = image_file.read()

        # Detect colors
        result = detect_cube_colors(image_data)

        if result.get("success"):
            return jsonify({
                "success": True,
                "colors": result.get("colors")
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Unknown error")
            }), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # Run development server
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=5000)
