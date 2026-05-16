import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

# Dynamic internal module resolution
from solvers.color_detector import detect_cube_colors
from solvers.solver import solve
from cube import Cube

app = Flask(__name__)
# Enable global Cross-Origin handling for seamless local workspace execution
CORS(app, resources={r"/api/*": {"origins": "*"}})

UPLOAD_FOLDER = 'temp_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Cache memory sequence mapping for the 6 scanned faces
current_session_cube = {}

def compile_and_translate_scan(cube_data):
    """
    Validates structural matrix completeness and applies dynamic center-tracking
    to automatically handle variations in physical cube orientation during scans.
    """
    face_order = ['U', 'R', 'F', 'D', 'L', 'B']
    
    # 1. Structural Integrity Check
    for face in face_order:
        face_stickers = cube_data.get(face)
        if not face_stickers or len(face_stickers) != 9:
            raise ValueError(f"Face {face} vision mapping data is incomplete or pixel contours were dropped.")
    
    # 2. Dynamic Center Vector Resolution (Reads index 4 of each captured face layout)
    centers = {
        cube_data['U'][4]: 'U',
        cube_data['R'][4]: 'R',
        cube_data['F'][4]: 'F',
        cube_data['D'][4]: 'D',
        cube_data['L'][4]: 'L',
        cube_data['B'][4]: 'B'
    }
    
    if len(centers) < 6:
        raise ValueError("Duplicate face center colors resolved. Ensure uniform lighting environmental conditions.")
        
    # 3. Assemble complete standard mathematical state string
    kociemba_string = ""
    for face in face_order:
        for color in cube_data[face]:
            kociemba_string += centers[color]
            
    return kociemba_string


# ── 1. CAMERA SCAN PIPELINE ENDPOINT ─────────────────────────────────────────
@app.route('/api/upload-face', methods=['POST'])
def handle_face_upload():
    if 'file' not in request.files or 'face' not in request.form:
        return jsonify({'success': False, 'error': 'Missing file payload or face identifier parameter'}), 400
        
    file = request.files['file']
    face_id = request.form['face'].upper()
    
    try:
        # FIX: Read the file stream directly into memory as raw binary bytes 
        # instead of creating a temporary string file path.
        image_data = file.read()
        
        # Run your computer vision tracking directly on the raw bytes data
        vision_result = detect_cube_colors(image_data)
            
        if not vision_result.get("success"):
            return jsonify({
                'success': False, 
                'error': f"Vision parsing failed on Face {face_id}: {vision_result.get('error', 'Contour detection timeout')}"
            }), 400
            
        detected_colors = vision_result.get("colors")
        
        if not detected_colors or len(detected_colors) != 9:
            return jsonify({'success': False, 'error': f"Face {face_id} returned incomplete matrix structure ({len(detected_colors) if detected_colors else 0}/9 tokens)"}), 400

        current_session_cube[face_id] = detected_colors
        is_complete = len(current_session_cube) == 6
        solution_moves = None
        
        if is_complete:
            kociemba_state_str = compile_and_translate_scan(current_session_cube)
            
            my_cube = Cube()
            if hasattr(my_cube, 'set_state'):
                my_cube.set_state(kociemba_state_str)
            else:
                my_cube.state = kociemba_state_str
                
            raw_moves_list = solve(my_cube)
            solution_moves = " ".join(raw_moves_list)
            current_session_cube.clear()
            
        return jsonify({
            'success': True,
            'face_recorded': face_id,
            'detected_colors': detected_colors,
            'all_sides_complete': is_complete,
            'solution': solution_moves,
            'moves': raw_moves_list if is_complete else None  # 🔥 ADD THIS CRITICAL LINE
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f"Internal Vision Processing Error: {str(e)}"}), 500


# ── 2. MANUAL GRID SOLVE ENDPOINT ────────────────────────────────────────────
@app.route('/api/solve', methods=['POST'])
def handle_manual_solve():
    data = request.get_json()
    if not data or 'state' not in data:
        return jsonify({'success': False, 'error': 'Missing 54-character state configuration vector'}), 400
        
    try:
        color_state = data['state']
        centers = {
            color_state[4]:  'U',
            color_state[13]: 'R',
            color_state[22]: 'F',
            color_state[31]: 'D',
            color_state[40]: 'L',
            color_state[49]: 'B'
        }
        
        if len(centers) < 6:
            return jsonify({"success": False, "error": "Invalid input grid configuration: Center colors must be unique."}), 400
            
        translated_state = "".join([centers[color] for color in color_state])
        
        my_cube = Cube()
        if hasattr(my_cube, 'set_state'):
            my_cube.set_state(translated_state)
        else:
            my_cube.state = translated_state
            
        raw_moves_list = solve(my_cube)
        solution_moves = " ".join(raw_moves_list)
        
        return jsonify({
            'success': True,
            'solution': solution_moves,
            'moves': raw_moves_list  # 🔥 ADD THIS CRITICAL LINE
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f"Mathematical engine evaluation failure: {str(e)}"}), 500

@app.route('/api/reset-scan', methods=['POST'])
def reset_scan_state():
    current_session_cube.clear()
    return jsonify({'success': True, 'message': 'Session state flushed successfully'})

if __name__ == '__main__':
    app.run(port=5000, debug=True)