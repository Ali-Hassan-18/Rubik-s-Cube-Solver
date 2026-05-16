import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# System paths dynamic injection (jo humne solver.py ke liye kiya tha)
from solvers.color_detector import detect_cube_colors
from solvers.solver import solve
from cube import Cube

app = Flask(__name__)
# CORS configuration allows your localhost:3000 frontend to safely make requests
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

UPLOAD_FOLDER = 'temp_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global dictionary to trace the 6 sides sequentially
current_session_cube = {}

# Map centers to standard Kociemba notation tracking
COLOR_TO_FACE_MAP = {
    'W': 'U',  # White center -> Up
    'R': 'R',  # Red center   -> Right
    'G': 'F',  # Green center -> Front
    'Y': 'D',  # Yellow center-> Down
    'O': 'L',  # Orange center-> Left
    'B': 'B'   # Blue center  -> Back
}

def translate_to_kociemba_string(cube_data):
    kociemba_string = ""
    face_order = ['U', 'R', 'F', 'D', 'L', 'B']
    for face in face_order:
        face_stickers = cube_data.get(face)
        if not face_stickers or len(face_stickers) != 9:
            raise ValueError(f"Face {face} matrix data is incomplete.")
        for color in face_stickers:
            translated_char = COLOR_TO_FACE_MAP.get(color, 'U')
            kociemba_string += translated_char
    return kociemba_string

# ── 1. CAMERA SCAN ENDPOINT ──────────────────────────────────────────────────
@app.route('/api/upload-face', methods=['POST'])
def handle_face_upload():
    if 'file' not in request.files or 'face' not in request.form:
        return jsonify({'success': False, 'error': 'Missing file payload or face parameter'}), 400
        
    file = request.files['file']
    face_id = request.form['face'].upper()
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    
    try:
        detected_colors = detect_cube_colors(file_path)
        os.remove(file_path)
        
        current_session_cube[face_id] = detected_colors
        is_complete = len(current_session_cube) == 6
        solution_moves = None
        
        if is_complete:
            kociemba_state_str = translate_to_kociemba_string(current_session_cube)
            
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
            'solution': solution_moves
        })
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'success': False, 'error': str(e)}), 500

# ── 2. MANUAL GRID ENDPOINT ──────────────────────────────────────────────────
@app.route('/api/solve', methods=['POST'])
def handle_manual_solve():
    data = request.get_json()
    if not data or 'state' not in data:
        return jsonify({'success': False, 'error': 'No state array passed'}), 400
        
    try:
        my_cube = Cube()
        if hasattr(my_cube, 'set_state'):
            my_cube.set_state(data['state'])
        else:
            my_cube.state = data['state']
            
        raw_moves_list = solve(my_cube)
        solution_moves = " ".join(raw_moves_list)
        
        return jsonify({
            'success': True,
            'solution': solution_moves
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reset-scan', methods=['POST'])
def reset_scan_state():
    current_session_cube.clear()
    return jsonify({'success': True, 'message': 'Flushed session'})

if __name__ == '__main__':
    app.run(port=5000, debug=True)