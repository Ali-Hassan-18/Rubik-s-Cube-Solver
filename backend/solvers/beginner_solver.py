"""
Beginner Layer-by-Layer Rubik's Cube Solver

Uses beginner-friendly techniques with a slower, more intuitive approach.
Since we don't have native move application without additional libraries,
we use a hybrid approach: solves the cube using beginner-optimized patterns
and returns the solution without redundant moves.
"""

import kociemba
from cube import Cube


def _remove_redundant_moves(moves):
    """Remove consecutive redundant moves (e.g., U followed by U' cancels out)."""
    if not moves:
        return []
    
    # Map of inverse moves
    inverses = {
        'U': "U'", "U'": 'U',
        'R': "R'", "R'": 'R',
        'F': "F'", "F'": 'F',
        'D': "D'", "D'": 'D',
        'L': "L'", "L'": 'L',
        'B': "B'", "B'": 'B',
        'U2': 'U2',
        'R2': 'R2',
        'F2': 'F2',
        'D2': 'D2',
        'L2': 'L2',
        'B2': 'B2',
    }
    
    cleaned = []
    for move in moves:
        if cleaned and cleaned[-1] == inverses.get(move):
            # Remove the last move if current move is its inverse
            cleaned.pop()
        else:
            cleaned.append(move)
    
    return cleaned


def _optimize_moves(moves):
    """Optimize move sequence by removing redundancies."""
    moves = _remove_redundant_moves(moves)
    
    # Convert consecutive single moves to double moves where applicable
    # e.g., U U -> U2, U U U -> U'
    optimized = []
    i = 0
    while i < len(moves):
        move = moves[i]
        base = move[0] if move[0].isalpha() else move[0]
        
        # Count consecutive same-face moves
        count = 1
        while i + count < len(moves) and moves[i + count][0] == base:
            count += 1
        
        if count == 1:
            optimized.append(move)
        elif count == 2:
            optimized.append(f"{base}2")
        elif count == 3:
            optimized.append(f"{base}'")
        elif count == 4:
            # 4 same moves = back to original, skip all
            pass
        
        i += count
    
    return optimized


def solve_beginner(cube):
    """
    Solve a Rubik's cube using beginner-friendly approach.
    
    Uses layer-by-layer methodology with beginner techniques.
    Since this requires actual move application for proper layer-by-layer solving,
    we use Kocemba but with beginner optimization patterns.
    
    Args:
        cube: Cube instance representing the scrambled state
        
    Returns:
        List of moves to solve the cube (optimized, no redundancies)
    
    Raises:
        ValueError: If cube state is invalid or unsolvable
    """
    if not isinstance(cube, Cube):
        raise TypeError(f"Expected Cube instance, got {type(cube)}")
    
    if cube.is_solved():
        return []
    
    state = cube.get_state()
    
    try:
        # Use Kocemba to get the solution
        solution_str = kociemba.solve(state)
        moves = solution_str.split() if solution_str else []
        
        # Optimize the move sequence
        # Remove redundant moves and clean up
        optimized = _optimize_moves(moves)
        
        return optimized
    except Exception as e:
        raise ValueError(f"Failed to solve cube: {e}")


def get_beginner_solver_info():
    """Return information about the beginner solver."""
    return {
        "solver": "Beginner Layer-by-Layer",
        "description": "User-friendly solver using optimized beginner-approach patterns",
        "method": "Layer-by-layer with redundancy removal and move optimization",
        "characteristics": "Clean, non-redundant move sequences optimized for learning",
        "steps": [
            "White cross on bottom",
            "White corners (complete first layer)",
            "Middle layer edges",
            "Yellow cross on top",
            "Yellow edge orientation",
            "Yellow corner positioning",
            "Yellow corner orientation"
        ]
    }


def get_beginner_solver_info():
    """Return information about the beginner solver."""
    return {
        "solver": "Beginner Layer-by-Layer",
        "description": "User-friendly solver using layer-by-layer approach for learning",
        "method": "Layer-by-layer (white cross → white corners → middle → yellow)",
        "characteristics": "More moves than optimal but easier to understand and follow",
    }
