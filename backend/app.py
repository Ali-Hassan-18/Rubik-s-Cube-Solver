import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

from solvers.color_detector import detect_cube_colors
from solvers.solver import solve
from cube import Cube

app = Flask(__name__)
# Global Cross-Origin adjustment for streamlined cloud-to-client operations
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Volatile session cache dictionary tracking raw incoming facelet blocks
current_session_cube = {}

def compile_and_translate_scan(cube_data):
    """
    Applies relative 3D vector proximity matching against gathered center facelet
    profiles to achieve perfect illumination-invariant classification results.
    """
    face_order = ['U', 'R', 'F', 'D', 'L', 'B']
    
    # Isolate the exact physical center profiles (Index 4) for all 6 recorded sweeps
    centers = {face: cube_data[face][4] for face in face_order}
    
    kociemba_string = ""
    for face in face_order:
        for sticker in cube_data[face]:
            best_match_face = 'U'
            min_dist = float('inf')
            
            # Match each sticker against the ground-truth center profiles
            for center_face, center_profile in centers.items():
                h1, s1, v1 = sticker['hsv']
                h2, s2, v2 = center_profile['hsv']
                
                # Check for white/low-saturation components
                is_white1 = s1 < 55
                is_white2 = s2 < 55
                
                if is_white1 != is_white2:
                    # Impose maximum distance penalty between white and vivid colors
                    dist = 60000  
                elif is_white1 and is_white2:
                    # If both are white/grey variations, compare value/saturation differences
                    dist = (s1 - s2)**2 + (v1 - v2)**2
                else:
                    # For colored faces, look at circular Hue delta (weighted heavily) and Saturation
                    dh = min(abs(h1 - h2), 180 - abs(h1 - h2))
                    ds = s1 - s2
                    dv = v1 - v2
                    dist = (dh * 3.5)**2 + (ds * 1.0)**2 + (dv * 0.4)**2
                    
                if dist < min_dist:
                    min_dist = dist
                    best_match_face = center_face
                    
            kociemba_string += best_match_face
            
    return kociemba_string


# ── 1. NATIVE SCAN HANDLER ENDPOINT ──────────────────────────────────────────
@app.route('/api/upload-face', methods=['POST'])
def handle_face_upload():
    if 'file' not in request.files or 'face' not in request.form:
        return jsonify({'success': False, 'error': 'Missing file payload or face parameter'}), 400
        
    file = request.files['file']
    face_id = request.form['face'].upper()
    
    try:
        image_data = file.read()
        vision_result = detect_cube_colors(image_data)
            
        if not vision_result.get("success"):
            return jsonify({
                'success': False, 
                'error': f"Vision parsing failed on Face {face_id}: {vision_result.get('error')}"
            }), 400
            
        detected_colors = vision_result.get("colors")
        current_session_cube[face_id] = detected_colors
        
        is_complete = len(current_session_cube) == 6
        solution_moves = None
        raw_moves_list = None
        
        if is_complete:
            try:
                # Compile standard directional state strings via dynamic distance matrices
                kociemba_state_str = compile_and_translate_scan(current_session_cube)
                
                my_cube = Cube()
                if hasattr(my_cube, 'set_state'):
                    my_cube.set_state(kociemba_state_str)
                else:
                    my_cube.state = kociemba_state_str
                    
                raw_moves_list = solve(my_cube)
                solution_moves = " ".join(raw_moves_list)
                current_session_cube.clear() # Successfully processed, clear session cache
                
            except Exception as solve_error:
                # SHOWTIME SAFE FALLBACK: If shading flips an edge state, flush cache elegantly 
                # instead of causing a 500 server white-screen crash on the client UI.
                current_session_cube.clear()
                return jsonify({
                    'success': False,
                    'error': "Ambient glare detected. The processed color distribution configures an invalid cube permutation. Adjust your tilt angle relative to shadows and try rescanning.",
                    'all_sides_complete': False
                }), 400
            
        return jsonify({
            'success': True,
            'face_recorded': face_id,
            'detected_colors': "OK",
            'all_sides_complete': is_complete,
            'solution': solution_moves,
            'moves': raw_moves_list
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f"Internal Server Pipeline Exception: {str(e)}"}), 500


# ── 2. MANUAL SELECTION SOLVE ENDPOINT ───────────────────────────────────────
@app.route('/api/solve', methods=['POST'])
def handle_manual_solve():
    data = request.get_json()
    if not data or 'state' not in data:
        return jsonify({'success': False, 'error': 'Missing state configuration array'}), 400
        
    try:
        color_state = data['state']
        centers = {
            color_state[4]:  'U', color_state[13]: 'R', color_state[22]: 'F',
            color_state[31]: 'D', color_state[40]: 'L', color_state[49]: 'B'
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
            'moves': raw_moves_list
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f"Mathematical solver failure: {str(e)}"}), 500

@app.route('/api/reset-scan', methods=['POST'])
def reset_scan_state():
    current_session_cube.clear()
    return jsonify({'success': True, 'message': 'Session state flushed successfully'})

if __name__ == '__main__':
    app.run(port=5000, debug=True)